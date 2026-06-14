"""CPU-side particle system with NumPy-vectorized updates.

Manages particle emission, physics simulation, lifetime, and color fading.
Particle data is uploaded to the GPU each frame for rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from guitarscapes.utils.logger import get_logger

logger = get_logger("visuals.particles")


class ParticleSystem:
    """Pool-based particle system using NumPy arrays for fast batch updates.

    All particles live in pre-allocated arrays.  Dead particles (lifetime ≤ 0)
    are recycled when new particles are emitted.
    """

    def __init__(self, max_particles: int = 5000) -> None:
        self.max_particles = max_particles

        # Position (x, y) in NDC [-1, 1]
        self.positions = np.zeros((max_particles, 2), dtype=np.float32)
        # Velocity (vx, vy) per second
        self.velocities = np.zeros((max_particles, 2), dtype=np.float32)
        # RGBA color
        self.colors = np.zeros((max_particles, 4), dtype=np.float32)
        # Base colors (before lifetime fade)
        self._base_colors = np.zeros((max_particles, 4), dtype=np.float32)
        # Point size in pixels
        self.sizes = np.zeros(max_particles, dtype=np.float32)
        # Remaining lifetime in seconds
        self.lifetimes = np.zeros(max_particles, dtype=np.float32)
        # Maximum lifetime (for computing fade ratio)
        self.max_lifetimes = np.ones(max_particles, dtype=np.float32)

        self._alive_mask = np.zeros(max_particles, dtype=bool)
        logger.debug("ParticleSystem created with capacity %d", max_particles)

    # ── Properties ──────────────────────────────────────────────────────────

    @property
    def alive_count(self) -> int:
        """Number of currently alive particles."""
        return int(np.count_nonzero(self._alive_mask))

    # ── Emission ────────────────────────────────────────────────────────────

    def emit(
        self,
        count: int,
        position: Tuple[float, float] = (0.0, 0.0),
        velocity_range: Tuple[Tuple[float, float], Tuple[float, float]] = (
            (-0.1, 0.1),
            (0.1, 0.5),
        ),
        color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.8),
        size_range: Tuple[float, float] = (2.0, 6.0),
        lifetime_range: Tuple[float, float] = (1.0, 3.0),
    ) -> int:
        """Spawn new particles, recycling dead slots.

        Args:
            count: Number of particles to emit.
            position: Spawn center (x, y) in NDC.
            velocity_range: ((vx_min, vx_max), (vy_min, vy_max)).
            color: Base RGBA color.
            size_range: (min_size, max_size) in pixels.
            lifetime_range: (min_life, max_life) in seconds.

        Returns:
            Number of particles actually emitted (limited by pool size).
        """
        # Find dead slots
        dead_indices = np.where(~self._alive_mask)[0]
        n = min(count, len(dead_indices))
        if n == 0:
            return 0

        idx = dead_indices[:n]

        # Position with slight randomness around center
        self.positions[idx, 0] = position[0] + np.random.uniform(-0.02, 0.02, n)
        self.positions[idx, 1] = position[1] + np.random.uniform(-0.02, 0.02, n)

        # Velocity
        vx_min, vx_max = velocity_range[0]
        vy_min, vy_max = velocity_range[1]
        self.velocities[idx, 0] = np.random.uniform(vx_min, vx_max, n)
        self.velocities[idx, 1] = np.random.uniform(vy_min, vy_max, n)

        # Color
        self._base_colors[idx] = color
        self.colors[idx] = color

        # Size
        self.sizes[idx] = np.random.uniform(size_range[0], size_range[1], n)

        # Lifetime
        lt = np.random.uniform(lifetime_range[0], lifetime_range[1], n).astype(
            np.float32
        )
        self.lifetimes[idx] = lt
        self.max_lifetimes[idx] = lt

        self._alive_mask[idx] = True
        return n

    # ── Update ──────────────────────────────────────────────────────────────

    def update(
        self,
        dt: float,
        gravity: Tuple[float, float] = (0.0, 0.0),
        wind: Tuple[float, float] = (0.0, 0.0),
    ) -> None:
        """Advance all alive particles by dt seconds.

        Args:
            dt: Time step in seconds.
            gravity: (gx, gy) acceleration.
            wind: (wx, wy) constant velocity offset.
        """
        alive = self._alive_mask

        if not np.any(alive):
            return

        # Apply gravity to velocity
        if gravity[0] != 0.0 or gravity[1] != 0.0:
            self.velocities[alive, 0] += gravity[0] * dt
            self.velocities[alive, 1] += gravity[1] * dt

        # Apply wind to velocity
        if wind[0] != 0.0 or wind[1] != 0.0:
            self.velocities[alive, 0] += wind[0] * dt
            self.velocities[alive, 1] += wind[1] * dt

        # Update positions
        self.positions[alive] += self.velocities[alive] * dt

        # Decrease lifetime
        self.lifetimes[alive] -= dt

        # Fade alpha based on remaining lifetime ratio
        ratios = np.clip(
            self.lifetimes[alive] / self.max_lifetimes[alive], 0.0, 1.0
        )
        self.colors[alive, 3] = self._base_colors[alive, 3] * ratios

        # Kill expired particles
        expired = alive & (self.lifetimes <= 0.0)
        self._alive_mask[expired] = False

    # ── Data Access ─────────────────────────────────────────────────────────

    def get_live_data(
        self,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return data arrays for alive particles only.

        Returns:
            (positions, colors, sizes) — contiguous arrays for GPU upload.
        """
        alive = self._alive_mask
        return (
            np.ascontiguousarray(self.positions[alive]),
            np.ascontiguousarray(self.colors[alive]),
            np.ascontiguousarray(self.sizes[alive]),
        )

    def clear(self) -> None:
        """Kill all particles."""
        self._alive_mask[:] = False
        self.lifetimes[:] = 0.0
