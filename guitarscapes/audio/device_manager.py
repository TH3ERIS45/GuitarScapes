"""Audio device discovery, validation, and selection.

Provides a high-level interface over ``sounddevice`` for enumerating input-capable
audio devices, selecting a capture device, and hot-swapping at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import sounddevice as sd

from guitarscapes.utils.config import AudioConfig
from guitarscapes.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class AudioDeviceInfo:
    """Immutable snapshot of a single audio input device."""

    index: int
    name: str
    channels: int
    sample_rate: float
    is_default: bool

    def __str__(self) -> str:
        default_tag = " [default]" if self.is_default else ""
        return (
            f"[{self.index}] {self.name} "
            f"(ch={self.channels}, sr={self.sample_rate:.0f}){default_tag}"
        )


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DeviceNotFoundError(Exception):
    """Raised when a requested device index does not exist or is not an input device."""


class DeviceBusyError(Exception):
    """Raised when a device cannot be opened because it is in use."""


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class AudioDeviceManager:
    """Enumerate, validate, and select audio input devices.

    Parameters
    ----------
    config:
        Optional :class:`AudioConfig` used for default sample-rate and channel
        preferences when no explicit values are given.
    """

    def __init__(self, config: AudioConfig | None = None) -> None:
        self._config = config or AudioConfig()
        self._devices: list[AudioDeviceInfo] = []
        self._selected_index: int | None = None
        self.refresh_devices()

    # -- public API ---------------------------------------------------------

    def refresh_devices(self) -> None:
        """Re-scan the host for available input devices."""
        self._devices = self._query_input_devices()
        logger.info("Device scan complete — %d input device(s) found.", len(self._devices))

        # Invalidate selection if the previously-selected device disappeared.
        if self._selected_index is not None:
            if not any(d.index for d in self._devices if d.index == self._selected_index):
                logger.warning(
                    "Previously selected device %d is no longer available.", self._selected_index
                )
                self._selected_index = None

    def get_input_devices(self) -> list[AudioDeviceInfo]:
        """Return a list of all currently known input-capable devices."""
        return list(self._devices)

    def get_default_device(self) -> AudioDeviceInfo | None:
        """Return the system default input device, or ``None`` if unavailable."""
        for device in self._devices:
            if device.is_default:
                return device
        return None

    def select_device(self, index: int) -> AudioDeviceInfo:
        """Select a device by its host index.

        Parameters
        ----------
        index:
            The ``sounddevice`` device index.

        Returns
        -------
        AudioDeviceInfo
            Metadata for the newly-selected device.

        Raises
        ------
        DeviceNotFoundError
            If *index* does not correspond to a known input device.
        """
        device = self._find_device(index)
        if device is None:
            raise DeviceNotFoundError(
                f"No input device with index {index}. "
                f"Available: {[d.index for d in self._devices]}"
            )
        self._selected_index = index
        logger.info("Selected input device: %s", device)
        return device

    @property
    def selected_device(self) -> AudioDeviceInfo | None:
        """The currently selected device, if any."""
        if self._selected_index is None:
            return None
        return self._find_device(self._selected_index)

    def validate_device(self, index: int) -> bool:
        """Check whether *index* points to a usable input device.

        Attempts to momentarily open a very short stream to confirm the device
        is not busy or otherwise inaccessible.

        Returns
        -------
        bool
            ``True`` when the device can be opened for capture.
        """
        device = self._find_device(index)
        if device is None:
            logger.warning("Validation failed — device %d not found.", index)
            return False

        try:
            # Open and immediately close a tiny stream to probe availability.
            with sd.InputStream(
                device=index,
                channels=min(device.channels, self._config.channels),
                samplerate=device.sample_rate,
                blocksize=256,
                dtype=self._config.dtype,
            ):
                pass
            logger.debug("Device %d validated successfully.", index)
            return True
        except sd.PortAudioError as exc:
            logger.warning("Device %d validation failed: %s", index, exc)
            return False
        except Exception:
            logger.exception("Unexpected error validating device %d.", index)
            return False

    # -- internal helpers ---------------------------------------------------

    def _find_device(self, index: int) -> AudioDeviceInfo | None:
        for device in self._devices:
            if device.index == index:
                return device
        return None

    @staticmethod
    def _query_input_devices() -> list[AudioDeviceInfo]:
        """Query ``sounddevice`` and return only input-capable devices."""
        try:
            all_devices: Sequence[dict] = sd.query_devices()  # type: ignore[assignment]
        except sd.PortAudioError:
            logger.exception("PortAudio error while querying devices.")
            return []
        except Exception:
            logger.exception("Unexpected error while querying devices.")
            return []

        # Determine the host default input device index.
        try:
            default_input_index: int | None = sd.default.device[0]  # type: ignore[index]
        except Exception:
            default_input_index = None

        devices: list[AudioDeviceInfo] = []
        for idx, info in enumerate(all_devices):
            max_in: int = int(info.get("max_input_channels", 0))
            if max_in <= 0:
                continue
            devices.append(
                AudioDeviceInfo(
                    index=idx,
                    name=str(info.get("name", f"device-{idx}")),
                    channels=max_in,
                    sample_rate=float(info.get("default_samplerate", 44100.0)),
                    is_default=(idx == default_input_index),
                )
            )
        return devices
