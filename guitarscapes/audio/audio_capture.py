"""Real-time audio capture via ``sounddevice``.

Runs on a :class:`StoppableThread`, feeding raw audio frames into a
:class:`SafeQueue` for downstream processing (FFT, HPCP, etc.).
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np
import sounddevice as sd
from scipy.signal import resample

from guitarscapes.utils.config import AudioConfig
from guitarscapes.utils.logger import get_logger
from guitarscapes.utils.threading_utils import SafeQueue, StoppableThread

logger = get_logger(__name__)

# How long ``run_loop`` sleeps between heartbeat ticks (seconds).
# The actual audio I/O is driven by sounddevice's own PortAudio thread;
# this loop only exists so StoppableThread can check its stop flag.
_HEARTBEAT_INTERVAL: float = 0.05

# Delay before retrying after a recoverable PortAudio error.
_RETRY_DELAY: float = 1.0

# Maximum consecutive errors before giving up.
_MAX_CONSECUTIVE_ERRORS: int = 5


class AudioCapture(StoppableThread):
    """Capture audio from an input device and enqueue frames.

    Parameters
    ----------
    config:
        Audio pipeline configuration (sample rate, block size, etc.).
    output_queue:
        Queue that receives ``numpy.ndarray`` audio frames.
    device_index:
        Initial device to open.  Falls back to *config.device_index* and
        then to the system default.
    """

    def __init__(
        self,
        config: AudioConfig,
        output_queue: SafeQueue,
        device_index: int | None = None,
    ) -> None:
        super().__init__(name="AudioCapture", daemon=True)
        self._config = config
        self._queue = output_queue
        self._device_index: int | None = device_index or config.device_index
        self._stream: sd.InputStream | None = None
        self._error_count: int = 0

    # -- properties ---------------------------------------------------------

    @property
    def is_capturing(self) -> bool:
        """``True`` while the underlying PortAudio stream is active."""
        return self._stream is not None and self._stream.active

    @property
    def current_device_index(self) -> int | None:
        """Index of the device currently being captured, or ``None``."""
        return self._device_index

    # -- public API ---------------------------------------------------------

    def set_device(self, device_index: int) -> None:
        """Hot-swap to a different input device.

        The current stream is stopped, reconfigured, and restarted.
        Safe to call from any thread.

        Parameters
        ----------
        device_index:
            Host device index to switch to.
        """
        logger.info("Hot-swapping capture device → %d", device_index)
        self._close_stream()
        self._device_index = device_index
        self._open_stream()

    # -- StoppableThread overrides ------------------------------------------

    def on_start(self) -> None:
        """Called once when the thread starts."""
        logger.info(
            "AudioCapture starting (sr=%d, bs=%d, dev=%s).",
            self._config.sample_rate,
            self._config.block_size,
            self._device_index,
        )
        self._open_stream()

    def run_loop(self) -> None:
        """Heartbeat loop — audio I/O is handled by sounddevice's thread."""
        time.sleep(_HEARTBEAT_INTERVAL)

    def on_stop(self) -> None:
        """Called once when the thread is stopping."""
        logger.info("AudioCapture stopping.")
        self._close_stream()

    def on_error(self, exc: BaseException) -> None:
        """Handle errors raised during the capture lifecycle."""
        self._error_count += 1

        if isinstance(exc, sd.PortAudioError):
            logger.error(
                "PortAudio error (#%d): %s — retrying in %.1fs.",
                self._error_count,
                exc,
                _RETRY_DELAY,
            )
            self._close_stream()

            if self._error_count >= _MAX_CONSECUTIVE_ERRORS:
                logger.critical(
                    "Exceeded %d consecutive errors. Giving up.", _MAX_CONSECUTIVE_ERRORS
                )
                return

            time.sleep(_RETRY_DELAY)
            self._open_stream()
        else:
            logger.exception("Unexpected capture error (#%d).", self._error_count)

    # -- internal -----------------------------------------------------------

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: Any,
        status: sd.CallbackFlags,
    ) -> None:
        """Sounddevice stream callback — runs on the PortAudio thread.

        Copies the incoming buffer, resamples if needed, and enqueues it.
        This must be as fast as possible; no blocking or heavy computation.
        """
        if status:
            logger.warning("Stream status: %s", status)

        audio = indata.copy()

        # Resample to target rate if device runs at a different rate
        if self._needs_resample and self._resample_ratio != 1.0:
            target_len = int(len(audio) * self._resample_ratio)
            if target_len > 0:
                audio = resample(audio, target_len).astype(np.float32)

        self._queue.put(audio)

        # Reset error count on successful callback.
        self._error_count = 0

    def _open_stream(self) -> None:
        """Open (or re-open) the ``sounddevice.InputStream``.

        Tries the configured sample rate first, then falls back to the
        device's default sample rate, then to common rates.
        """
        target_sr = self._config.sample_rate
        self._needs_resample = False
        self._resample_ratio = 1.0
        self._actual_sample_rate = target_sr

        # Determine sample rates to try
        rates_to_try = [target_sr]

        # Query device default rate
        try:
            device_info = sd.query_devices(self._device_index)
            default_sr = int(device_info["default_samplerate"])
            if default_sr != target_sr:
                rates_to_try.insert(0, default_sr)  # Try native rate first
            # Also try common rates
            for rate in [48000, 44100, 22050, 16000]:
                if rate not in rates_to_try:
                    rates_to_try.append(rate)
        except Exception as exc:
            logger.warning("Could not query device info: %s", exc)

        # Try each sample rate
        for sr in rates_to_try:
            try:
                self._stream = sd.InputStream(
                    device=self._device_index,
                    samplerate=sr,
                    blocksize=self._config.block_size,
                    channels=self._config.channels,
                    dtype=self._config.dtype,
                    callback=self._audio_callback,
                )
                self._stream.start()
                self._actual_sample_rate = sr

                if sr != target_sr:
                    self._needs_resample = True
                    self._resample_ratio = target_sr / sr
                    logger.info(
                        "InputStream opened on device %s at %d Hz "
                        "(resampling to %d Hz, ratio=%.4f).",
                        self._device_index, sr, target_sr,
                        self._resample_ratio,
                    )
                else:
                    logger.info(
                        "InputStream opened on device %s (sr=%d, bs=%d).",
                        self._device_index, sr, self._config.block_size,
                    )
                return  # Success

            except sd.PortAudioError as exc:
                logger.debug("Sample rate %d Hz failed: %s", sr, exc)
                self._stream = None
                continue

        # All rates failed
        logger.error(
            "Failed to open InputStream on device %s — "
            "no supported sample rate found (tried %s).",
            self._device_index,
            rates_to_try,
        )
        self._stream = None

    def _close_stream(self) -> None:
        """Gracefully close the active stream, if any."""
        if self._stream is None:
            return
        try:
            if self._stream.active:
                self._stream.stop()
            self._stream.close()
            logger.debug("InputStream closed.")
        except Exception:
            logger.exception("Error closing InputStream.")
        finally:
            self._stream = None

