"""Application configuration using dataclasses.

Centralizes all configurable parameters for audio, detection, visuals, and paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple


@dataclass
class AudioConfig:
    """Audio capture configuration."""

    sample_rate: int = 22050
    block_size: int = 2048
    channels: int = 1
    dtype: str = "float32"
    device_index: int | None = None

    @property
    def block_duration_ms(self) -> float:
        """Duration of one audio block in milliseconds."""
        return (self.block_size / self.sample_rate) * 1000.0


@dataclass
class DetectionConfig:
    """Chord detection pipeline configuration."""

    fft_size: int = 4096
    n_harmonics: int = 6
    min_frequency: float = 60.0
    max_frequency: float = 5000.0
    reference_frequency: float = 440.0
    hpcp_bins: int = 12
    peak_threshold: float = 0.01
    silence_threshold: float = 0.005
    smoothing_window: int = 7
    hysteresis_frames: int = 3
    confidence_threshold: float = 0.4
    top_k_candidates: int = 3


@dataclass
class VisualConfig:
    """Visual rendering configuration."""

    window_width: int = 1280
    window_height: int = 720
    target_fps: int = 60
    fullscreen: bool = False
    transition_duration: float = 1.5
    max_particles: int = 5000
    background_color: Tuple[float, float, float] = (0.02, 0.02, 0.05)
    vsync: bool = True


@dataclass
class PathConfig:
    """File path configuration."""

    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    @property
    def models_dir(self) -> Path:
        return self.base_dir / "models"

    @property
    def assets_dir(self) -> Path:
        return self.base_dir / "assets"

    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"

    @property
    def chord_refiner_model(self) -> Path:
        return self.models_dir / "chord_refiner.onnx"


@dataclass
class AppConfig:
    """Root application configuration combining all sub-configs."""

    audio: AudioConfig = field(default_factory=AudioConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    visual: VisualConfig = field(default_factory=VisualConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    debug: bool = False
    log_level: str = "INFO"
