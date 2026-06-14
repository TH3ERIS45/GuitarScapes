"""GuitarScapes Pro — Main Entry Point.

Orchestrates all subsystems: audio capture, chord detection, visual rendering,
and user interface. Handles startup, shutdown, and inter-thread communication.
"""

from __future__ import annotations

import signal
import sys
import time
import threading
from pathlib import Path
from typing import Optional

import numpy as np

from guitarscapes.utils.config import AppConfig
from guitarscapes.utils.logger import setup_logging, get_logger
from guitarscapes.utils.threading_utils import SafeQueue, ThreadHealthMonitor

logger = get_logger("main")


def _check_dependencies() -> list[str]:
    """Check that all required dependencies are available.

    Returns:
        List of missing dependency names (empty if all present).
    """
    missing: list[str] = []
    deps = {
        "sounddevice": "sounddevice",
        "numpy": "numpy",
        "scipy": "scipy",
        "numba": "numba",
        "moderngl": "moderngl",
        "pygame": "pygame",
    }
    for display_name, import_name in deps.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(display_name)
    return missing


def _check_permissions(config: AppConfig) -> bool:
    """Check microphone permissions and report status.

    Returns:
        True if microphone access is granted.
    """
    from guitarscapes.audio.permissions import PermissionChecker

    checker = PermissionChecker()
    platform_info = checker.get_platform_info()
    logger.info("Platform: %s", platform_info)

    result = checker.check_microphone_access()
    if result.granted:
        logger.info("Microphone access: GRANTED — %s", result.message)
        return True
    else:
        logger.warning("Microphone access: DENIED — %s", result.message)
        if result.instructions:
            logger.warning("Instructions:\n%s", result.instructions)
        return False


def _select_device(config: AppConfig) -> Optional[int]:
    """Show device selection dialog and return selected device index.

    Falls back to default device if PyQt6 is not available or dialog is
    cancelled.
    """
    from guitarscapes.audio.device_manager import AudioDeviceManager

    device_manager = AudioDeviceManager()
    devices = device_manager.get_input_devices()

    if not devices:
        logger.error("No audio input devices found!")
        return None

    logger.info("Available input devices:")
    for dev in devices:
        default_tag = " [DEFAULT]" if dev.is_default else ""
        logger.info(
            "  [%d] %s (%d ch, %.0f Hz)%s",
            dev.index,
            dev.name,
            dev.channels,
            dev.sample_rate,
            default_tag,
        )

    # Try to use PyQt6 device dialog
    try:
        from PyQt6.QtWidgets import QApplication
        from guitarscapes.ui.device_dialog import DeviceSelectionDialog

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        device_dicts = [
            {
                "index": d.index,
                "name": d.name,
                "channels": d.channels,
                "sample_rate": d.sample_rate,
                "is_default": d.is_default,
            }
            for d in devices
        ]
        default_idx = next(
            (d.index for d in devices if d.is_default), devices[0].index if devices else None
        )

        def refresh_callback():
            device_manager.refresh_devices()
            refreshed = device_manager.get_input_devices()
            return [
                {
                    "index": d.index,
                    "name": d.name,
                    "channels": d.channels,
                    "sample_rate": d.sample_rate,
                    "is_default": d.is_default,
                }
                for d in refreshed
            ]

        dialog = DeviceSelectionDialog(
            devices=device_dicts,
            default_index=default_idx,
            refresh_callback=refresh_callback,
        )
        result = dialog.exec()

        if result and dialog.selected_device_index is not None:
            selected = dialog.selected_device_index
            logger.info("User selected device index: %d", selected)
            return selected
        else:
            logger.info("Dialog cancelled, using default device.")

    except ImportError:
        logger.info("PyQt6 not available, using default audio device.")
    except Exception as exc:
        logger.warning("Device dialog failed: %s. Using default device.", exc)

    # Fallback to default device
    default = device_manager.get_default_device()
    if default:
        logger.info("Using default device: [%d] %s", default.index, default.name)
        return default.index

    # Absolute fallback: first device
    if devices:
        logger.info("Using first available device: [%d] %s", devices[0].index, devices[0].name)
        return devices[0].index

    return None


class DetectionWorker(threading.Thread):
    """Thread that runs the chord detection pipeline.

    Reads audio frames from audio_queue, processes them through FFT → HPCP →
    template matching → neural refinement → smoothing, and puts results into
    chord_queue.
    """

    def __init__(
        self,
        config: AppConfig,
        audio_queue: SafeQueue,
        chord_queue: SafeQueue,
    ) -> None:
        super().__init__(name="DetectionThread", daemon=True)
        self.config = config
        self.audio_queue = audio_queue
        self.chord_queue = chord_queue
        self._stop_event = threading.Event()
        self._fft = None
        self._hpcp = None
        self._templates = None
        self._refiner = None
        self._smoother = None

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        """Main detection loop."""
        from guitarscapes.detection.fft import FFTProcessor
        from guitarscapes.detection.hpcp import HPCPExtractor
        from guitarscapes.detection.templates import ChordTemplateBank
        from guitarscapes.detection.neural_refiner import NeuralRefiner
        from guitarscapes.detection.smoothing import TemporalSmoother

        det_config = self.config.detection

        self._fft = FFTProcessor(
            config=det_config,
            sample_rate=self.config.audio.sample_rate,
        )
        self._hpcp = HPCPExtractor(config=det_config)
        self._templates = ChordTemplateBank(config=det_config)
        self._refiner = NeuralRefiner(
            model_path=self.config.paths.chord_refiner_model
        )
        self._smoother = TemporalSmoother(config=det_config)

        # Sliding window buffer for overlapping FFTs
        self._audio_buffer = np.zeros(det_config.fft_size, dtype=np.float32)

        logger.info(
            "Detection pipeline initialized. Neural refiner: %s",
            "ACTIVE" if self._refiner.is_available else "INACTIVE (template-only)",
        )

        # Warm up numba JIT with a dummy frame
        try:
            fft_result = self._fft.process(self._audio_buffer)
            self._hpcp.extract(fft_result.peak_frequencies, fft_result.peak_magnitudes)
            logger.info("Numba JIT warm-up complete.")
        except Exception as exc:
            logger.warning("JIT warm-up encountered an issue: %s", exc)

        while not self._stop_event.is_set():
            # Get all available audio frames from queue
            frames = []
            while True:
                f = self.audio_queue.get_nowait()
                if f is None:
                    break
                # Ensure mono
                if f.ndim > 1:
                    f = f[:, 0]
                frames.append(f)

            if not frames:
                # No data available, brief sleep
                time.sleep(0.005)
                continue

            # Concatenate new audio
            new_audio = np.concatenate(frames)
            
            # Shift buffer and insert new audio
            n_new = len(new_audio)
            fft_size = self.config.detection.fft_size
            
            if n_new >= fft_size:
                self._audio_buffer[:] = new_audio[-fft_size:]
            else:
                self._audio_buffer[:-n_new] = self._audio_buffer[n_new:]
                self._audio_buffer[-n_new:] = new_audio

            try:
                self._process_frame(self._audio_buffer.copy(), n_new)
            except Exception as exc:
                logger.error("Detection error: %s", exc, exc_info=True)

    def _process_frame(self, frame: np.ndarray, n_new: int) -> None:
        """Process a single audio frame through the full pipeline."""
        # Compute RMS for intensity based only on the NEW audio to be responsive
        rms = float(np.sqrt(np.mean(frame[-n_new:] ** 2)))

        # Silence check
        if rms < self.config.detection.silence_threshold:
            result = self._smoother.smooth("—", 0.0)
            self.chord_queue.put_nowait((result.chord_name, result.confidence, rms))
            return

        # FFT
        fft_result = self._fft.process(frame)

        # HPCP extraction
        hpcp_vector = self._hpcp.extract(
            fft_result.peak_frequencies, fft_result.peak_magnitudes
        )

        # Template matching — get top K candidates
        candidates = self._templates.match(hpcp_vector)

        if not candidates:
            result = self._smoother.smooth("—", 0.0)
            self.chord_queue.put_nowait((result.chord_name, result.confidence, rms))
            return

        # Neural refinement (if model available)
        if self._refiner.is_available:
            candidates = self._refiner.refine(
                hpcp_vector, candidates, self._templates.get_chord_names()
            )

        # Temporal smoothing
        best = candidates[0]
        result = self._smoother.smooth(best.chord_name, best.confidence)

        # Send to render queue
        self.chord_queue.put_nowait((result.chord_name, result.confidence, rms))


def main() -> int:
    """Application entry point.

    Returns:
        Exit code (0 for success).
    """
    config = AppConfig()

    # Setup logging
    log_file = config.paths.logs_dir / "guitarscapes.log"
    setup_logging(level=config.log_level, log_file=log_file)

    logger.info("=" * 60)
    logger.info("  GuitarScapes Pro")
    logger.info("  Transform your guitar into living landscapes")
    logger.info("=" * 60)

    # Check dependencies
    missing = _check_dependencies()
    if missing:
        logger.error(
            "Missing dependencies: %s. Install with: pip install %s",
            ", ".join(missing),
            " ".join(missing),
        )
        return 1

    # Check permissions
    if not _check_permissions(config):
        logger.warning(
            "Microphone access may be restricted. "
            "The application will attempt to continue."
        )

    # Select audio device
    device_index = _select_device(config)
    if device_index is None:
        logger.error("No audio device available. Cannot continue.")
        return 1

    config.audio.device_index = device_index

    # Create inter-thread queues
    audio_queue: SafeQueue = SafeQueue(maxsize=32, name="AudioQueue")
    chord_queue: SafeQueue = SafeQueue(maxsize=16, name="ChordQueue")
    command_queue: SafeQueue = SafeQueue(maxsize=16, name="CommandQueue")

    # Start audio capture
    from guitarscapes.audio.audio_capture import AudioCapture

    audio_capture = AudioCapture(
        config=config.audio,
        output_queue=audio_queue,
    )

    # Start detection pipeline
    detection_worker = DetectionWorker(
        config=config,
        audio_queue=audio_queue,
        chord_queue=chord_queue,
    )

    # Setup signal handler for graceful shutdown
    shutdown_event = threading.Event()

    def _signal_handler(signum, frame):
        logger.info("Received signal %d, shutting down...", signum)
        shutdown_event.set()
        command_queue.put_nowait("quit")

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        # Start background threads
        audio_capture.start()
        detection_worker.start()
        logger.info("Audio capture and detection threads started.")

        # Start renderer in the main thread (pygame requires main thread on macOS)
        from guitarscapes.visuals.renderer import Renderer

        renderer = Renderer(
            config=config.visual,
            chord_queue=chord_queue,
            command_queue=command_queue,
        )

        # Get device name for HUD display
        from guitarscapes.audio.device_manager import AudioDeviceManager

        dm = AudioDeviceManager()
        devices = dm.get_input_devices()
        device_name = "Unknown"
        for d in devices:
            if d.index == device_index:
                device_name = d.name
                break

        renderer.device_name = device_name
        
        # Wait briefly for detection_worker to initialize its components
        for _ in range(50):  # Wait up to 500ms
            if hasattr(detection_worker, '_refiner') and detection_worker._refiner is not None:
                break
            time.sleep(0.01)
            
        if hasattr(detection_worker, '_refiner') and detection_worker._refiner is not None:
            renderer.ai_active = detection_worker._refiner.is_available
        else:
            renderer.ai_active = False
        logger.info("Starting visual renderer...")
        logger.info("♪ Toque seu violão e veja a música ganhar vida. ♪")

        # Run renderer in main thread (blocking)
        renderer.run_main_thread()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received.")
    except Exception as exc:
        logger.error("Fatal error: %s", exc, exc_info=True)
        return 1
    finally:
        logger.info("Shutting down GuitarScapes Pro...")

        # Stop all threads
        audio_capture.stop()
        detection_worker.stop()

        # Wait for threads to finish
        if audio_capture.is_alive():
            audio_capture.join(timeout=3.0)
        if detection_worker.is_alive():
            detection_worker.join(timeout=3.0)

        logger.info("Shutdown complete. Goodbye!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
