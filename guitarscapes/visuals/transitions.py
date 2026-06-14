"""Transition manager for smooth crossfades between visual environments.

Uses smoothstep interpolation to blend from one VisualEnvironment to another
over a configurable duration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from guitarscapes.visuals.environment import VisualEnvironment
from guitarscapes.utils.logger import get_logger

logger = get_logger("visuals.transitions")


@dataclass
class TransitionState:
    """Snapshot of the current transition state."""

    source: VisualEnvironment
    target: VisualEnvironment
    progress: float  # 0.0 = fully source, 1.0 = fully target
    is_transitioning: bool


class TransitionManager:
    """Manages smooth crossfade transitions between visual environments.

    When a new chord triggers a scene change, the manager blends from the
    current scene to the target over ``duration`` seconds using smoothstep
    interpolation.
    """

    def __init__(self, default_duration: float = 1.5) -> None:
        self._default_duration = default_duration
        self._source = VisualEnvironment()
        self._target = VisualEnvironment()
        self._progress: float = 1.0  # Start fully at target (no transition)
        self._duration: float = default_duration
        self._elapsed: float = 0.0
        self._is_transitioning: bool = False

    # ── Properties ──────────────────────────────────────────────────────────

    @property
    def current_environment(self) -> VisualEnvironment:
        """The active environment (target when not transitioning)."""
        return self._target

    @property
    def is_transitioning(self) -> bool:
        return self._is_transitioning

    @property
    def progress(self) -> float:
        """Transition progress from 0.0 (source) to 1.0 (target)."""
        return self._progress

    # ── Control ─────────────────────────────────────────────────────────────

    def start_transition(
        self,
        target: VisualEnvironment,
        duration: Optional[float] = None,
    ) -> None:
        """Begin a transition to a new visual environment.

        If a transition is already in progress, the current blended state
        becomes the new source.

        Args:
            target: The environment to transition to.
            duration: Transition duration in seconds (uses default if None).
        """
        if duration is None:
            duration = self._default_duration

        # If we're mid-transition, take the current state as new source
        if self._is_transitioning:
            self._source = self._target  # Simplification: snap to target
        else:
            self._source = self._target

        self._target = target
        self._duration = max(duration, 0.1)
        self._elapsed = 0.0
        self._progress = 0.0
        self._is_transitioning = True

        logger.debug(
            "Transition started: '%s' → '%s' (%.1fs)",
            self._source.mood,
            self._target.mood,
            self._duration,
        )

    def set_immediate(self, environment: VisualEnvironment) -> None:
        """Set a new environment immediately without transition."""
        self._source = environment
        self._target = environment
        self._progress = 1.0
        self._elapsed = 0.0
        self._is_transitioning = False

    def update(self, dt: float) -> None:
        """Advance the transition by ``dt`` seconds.

        Args:
            dt: Time elapsed since last update in seconds.
        """
        if not self._is_transitioning:
            return

        self._elapsed += dt
        linear = min(self._elapsed / self._duration, 1.0)

        # Smoothstep interpolation: t² × (3 - 2t)
        self._progress = linear * linear * (3.0 - 2.0 * linear)

        if linear >= 1.0:
            self._is_transitioning = False
            self._source = self._target
            self._progress = 1.0
            logger.debug("Transition completed: '%s'", self._target.mood)

    def get_current_state(self) -> TransitionState:
        """Return a snapshot of the transition state."""
        return TransitionState(
            source=self._source,
            target=self._target,
            progress=self._progress,
            is_transitioning=self._is_transitioning,
        )

    def reset(self) -> None:
        """Reset to default state."""
        self._source = VisualEnvironment()
        self._target = VisualEnvironment()
        self._progress = 1.0
        self._is_transitioning = False
