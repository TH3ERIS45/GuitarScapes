"""Visual environment and particle configuration dataclasses.

Defines the data structures that describe a visual scene: background colors,
enabled effects, particle emitter configuration, and mood descriptor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class ParticleConfig:
    """Configuration for a particle emitter within a visual scene."""

    emit_rate: float = 50.0
    color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.8)
    size_range: Tuple[float, float] = (2.0, 6.0)
    velocity_range: Tuple[Tuple[float, float], Tuple[float, float]] = (
        (-0.5, 0.5),
        (-0.5, 0.5),
    )
    lifetime_range: Tuple[float, float] = (1.0, 3.0)
    gravity: Tuple[float, float] = (0.0, 0.0)
    wind: Tuple[float, float] = (0.0, 0.0)


@dataclass
class VisualEnvironment:
    """Complete description of a visual scene tied to a chord.

    Each chord maps to a unique VisualEnvironment that controls the
    background gradient, which shader effects are active, particle
    emitter settings, and a mood label.
    """

    bg_color_top: Tuple[float, float, float] = (0.02, 0.02, 0.05)
    bg_color_bottom: Tuple[float, float, float] = (0.05, 0.05, 0.1)
    effect_color: Tuple[float, float, float] = (1.0, 1.0, 1.0)

    enable_stars: bool = False
    enable_fog: bool = False
    enable_rain: bool = False
    enable_fire: bool = False
    enable_aurora: bool = False
    enable_waves: bool = False
    enable_mountains: bool = False
    enable_fireflies: bool = False
    enable_constellations: bool = False
    enable_god_rays: bool = False
    enable_snow: bool = False
    enable_leaves: bool = False
    enable_nebula: bool = False
    enable_fractal: bool = False

    god_ray_position: Tuple[float, float] = (0.5, 0.8)
    particle_config: Optional[ParticleConfig] = None
    mood: str = ""
