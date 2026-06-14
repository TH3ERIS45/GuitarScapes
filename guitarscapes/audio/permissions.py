"""Cross-platform microphone permission detection.

Probes whether the application can open an audio input stream and, when
access is denied, returns human-readable remediation instructions tailored
to the user's operating system and audio backend.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import sounddevice as sd

from guitarscapes.utils.logger import get_logger

logger = get_logger(__name__)

# Short probe stream parameters — kept minimal to avoid latency on startup.
_PROBE_SAMPLERATE: int = 22050
_PROBE_BLOCKSIZE: int = 512
_PROBE_CHANNELS: int = 1
_PROBE_DTYPE: str = "float32"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class PermissionResult:
    """Outcome of a microphone permission check."""

    granted: bool
    message: str
    instructions: str

    def __str__(self) -> str:
        status = "✓ granted" if self.granted else "✗ denied"
        parts = [f"Microphone access: {status} — {self.message}"]
        if self.instructions:
            parts.append(f"  → {self.instructions}")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Platform-specific instruction templates
# ---------------------------------------------------------------------------

_WINDOWS_INSTRUCTIONS: str = (
    "Open Settings → Privacy & Security → Microphone and ensure "
    "microphone access is enabled for this application."
)

_MACOS_INSTRUCTIONS: str = (
    "Open System Settings → Privacy & Security → Microphone and "
    "grant this application permission to access the microphone."
)

_LINUX_INSTRUCTIONS_TEMPLATE: str = (
    "Detected audio backend: {backend}. "
    "Ensure your user is in the 'audio' group (`sudo usermod -aG audio $USER` "
    "then log out/in), and that libportaudio2 is installed "
    "(`sudo apt install libportaudio2` on Debian/Ubuntu)."
)


# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------

class PermissionChecker:
    """Test microphone accessibility and provide platform-aware guidance."""

    # -- public API ---------------------------------------------------------

    def check_microphone_access(self) -> PermissionResult:
        """Probe for microphone access on the current platform.

        This method **never** raises.  Any failure is captured and returned as
        a :class:`PermissionResult` with ``granted=False``.

        Returns
        -------
        PermissionResult
        """
        platform = sys.platform
        logger.info("Checking microphone access on platform '%s'.", platform)

        try:
            self._probe_stream()
        except sd.PortAudioError as exc:
            logger.warning("Microphone probe failed: %s", exc)
            return self._denied_result(platform, str(exc))
        except Exception as exc:
            logger.warning("Unexpected error during microphone probe: %s", exc)
            return self._denied_result(platform, str(exc))

        logger.info("Microphone access granted.")
        return PermissionResult(
            granted=True,
            message="Microphone is accessible.",
            instructions="",
        )

    def get_platform_info(self) -> str:
        """Return a human-readable summary of the OS and audio backend.

        Returns
        -------
        str
        """
        platform = sys.platform
        parts: list[str] = [f"Platform: {platform} ({sys.version})"]

        if platform.startswith("linux"):
            backend = self._detect_linux_backend()
            parts.append(f"Audio backend: {backend}")

        try:
            pa_info = sd.query_hostapis()
            for api in pa_info:
                parts.append(f"Host API: {api.get('name', 'unknown')}")
        except Exception:
            parts.append("Host API: unavailable")

        return " | ".join(parts)

    # -- internal -----------------------------------------------------------

    @staticmethod
    def _probe_stream() -> None:
        """Open and immediately close a minimal input stream."""
        with sd.InputStream(
            samplerate=_PROBE_SAMPLERATE,
            blocksize=_PROBE_BLOCKSIZE,
            channels=_PROBE_CHANNELS,
            dtype=_PROBE_DTYPE,
        ):
            pass  # Success — stream opened and closed without error.

    def _denied_result(self, platform: str, error_detail: str) -> PermissionResult:
        """Build a platform-specific denial result."""
        if platform == "win32":
            instructions = _WINDOWS_INSTRUCTIONS
        elif platform == "darwin":
            instructions = _MACOS_INSTRUCTIONS
        elif platform.startswith("linux"):
            backend = self._detect_linux_backend()
            instructions = _LINUX_INSTRUCTIONS_TEMPLATE.format(backend=backend)
        else:
            instructions = (
                f"Unsupported platform '{platform}'. "
                "Please ensure your audio driver is installed and microphone access is allowed."
            )

        return PermissionResult(
            granted=False,
            message=f"Microphone access denied ({error_detail}).",
            instructions=instructions,
        )

    @staticmethod
    def _detect_linux_backend() -> str:
        """Best-effort detection of the active Linux audio backend."""
        # PipeWire
        if shutil.which("pipewire"):
            try:
                result = subprocess.run(
                    ["pipewire", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if result.returncode == 0:
                    version = result.stdout.strip().splitlines()[-1]
                    return f"PipeWire ({version})"
            except Exception:
                pass

        # PulseAudio
        if shutil.which("pactl"):
            try:
                result = subprocess.run(
                    ["pactl", "info"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if "server name" in line.lower():
                            return f"PulseAudio ({line.split(':', 1)[1].strip()})"
                    return "PulseAudio"
            except Exception:
                pass

        # ALSA fallback
        if Path("/proc/asound/version").exists():
            try:
                version = Path("/proc/asound/version").read_text().strip()
                return f"ALSA ({version})"
            except Exception:
                return "ALSA"

        return "Unknown"
