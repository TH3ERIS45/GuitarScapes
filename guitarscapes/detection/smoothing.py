"""Temporal smoothing for stable chord predictions.

Applies a sliding window with confidence-weighted majority voting and
hysteresis to prevent rapid chord switching, producing stable predictions
suitable for driving visual transitions.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass

from guitarscapes.utils.config import DetectionConfig
from guitarscapes.utils.logger import get_logger


logger = get_logger("detection.smoothing")


@dataclass(frozen=True, slots=True)
class SmoothedResult:
    """Result of temporal smoothing for a single frame.

    Attributes:
        chord_name: The smoothed chord prediction (may differ from raw input).
        confidence: Weighted confidence of the smoothed prediction.
        is_stable: Whether the prediction has met the hysteresis threshold
            (i.e., been consistent for enough consecutive frames).
        raw_chord: The unsmoothed chord name from the current frame.
    """

    chord_name: str
    confidence: float
    is_stable: bool
    raw_chord: str


class TemporalSmoother:
    """Sliding-window temporal smoother with hysteresis for chord predictions.

    Maintains a fixed-size window of recent predictions and applies
    confidence-weighted majority voting to determine the most likely chord.
    A hysteresis mechanism requires a new chord to appear in N consecutive
    frames before the output switches, preventing rapid flickering.

    Args:
        config: Detection configuration parameters.
    """

    def __init__(self, config: DetectionConfig) -> None:
        self._window_size = config.smoothing_window
        self._hysteresis_frames = config.hysteresis_frames
        self._confidence_threshold = config.confidence_threshold

        # Sliding window of (chord_name, confidence) pairs
        self._window: deque[tuple[str, float]] = deque(maxlen=self._window_size)

        # Current stable output
        self._current_chord: str = ""
        self._current_confidence: float = 0.0

        # Hysteresis tracking
        self._pending_chord: str = ""
        self._pending_count: int = 0

        # Transition timing
        self._last_change_time: float = 0.0

        logger.info(
            "TemporalSmoother initialized: window=%d, hysteresis=%d, "
            "confidence_threshold=%.2f",
            self._window_size,
            self._hysteresis_frames,
            self._confidence_threshold,
        )

    @property
    def history(self) -> list[tuple[str, float]]:
        """Recent prediction history as a list of (chord_name, confidence) tuples.

        Returns:
            Copy of the sliding window contents, oldest first.
        """
        return list(self._window)

    @property
    def last_change_time(self) -> float:
        """Timestamp (monotonic) of the most recent chord transition.

        Returns:
            Time of last chord change, or 0.0 if no change has occurred.
        """
        return self._last_change_time

    @property
    def time_since_change(self) -> float:
        """Seconds elapsed since the last chord transition.

        Returns:
            Elapsed time in seconds, or 0.0 if no change has occurred.
        """
        if self._last_change_time == 0.0:
            return 0.0
        return time.monotonic() - self._last_change_time

    def reset(self) -> None:
        """Reset the smoother to its initial state.

        Clears the sliding window, resets hysteresis counters, and clears
        the current chord output.
        """
        self._window.clear()
        self._current_chord = ""
        self._current_confidence = 0.0
        self._pending_chord = ""
        self._pending_count = 0
        self._last_change_time = 0.0

        logger.debug("TemporalSmoother reset")

    def smooth(self, chord_name: str, confidence: float) -> SmoothedResult:
        """Process a new chord prediction and return the smoothed result.

        Adds the prediction to the sliding window, performs confidence-weighted
        majority voting, and applies hysteresis to determine whether to switch
        the output chord.

        Args:
            chord_name: Detected chord name for the current frame (may be
                empty string for silence/no detection).
            confidence: Confidence score for the detection in [0, 1].

        Returns:
            SmoothedResult with the current stable chord, confidence,
            stability flag, and the raw input chord.
        """
        raw_chord = chord_name

        # Handle silence or very low-confidence detections
        if confidence < self._confidence_threshold:
            chord_name = "—"
            confidence = 1.0  # Weight the "no chord" state highly so it outvotes noise

        # Add to sliding window
        self._window.append((chord_name, confidence))

        # Confidence-weighted majority voting across the window
        vote_scores: dict[str, float] = {}
        for name, conf in self._window:
            if name:  # Skip empty strings
                vote_scores[name] = vote_scores.get(name, 0.0) + conf

        if not vote_scores:
            # No valid chords in window
            winner = "—"
            winner_confidence = 1.0
        else:
            # Select chord with highest weighted vote total
            winner = max(vote_scores, key=vote_scores.get)  # type: ignore[arg-type]
            # Normalize confidence by window size for a meaningful average, cap at 1.0
            winner_confidence = min(1.0, vote_scores[winner] / self._window_size)
            
            # If the overall window confidence is still below threshold, reject it!
            if winner_confidence < self._confidence_threshold and winner != "—":
                winner = "—"
                winner_confidence = 1.0

        # Hysteresis: track consecutive frames of the same winning chord
        is_stable = False

        if winner == self._current_chord:
            # Same as current output — it's stable
            self._pending_chord = ""
            self._pending_count = 0
            is_stable = True
            self._current_confidence = winner_confidence

        elif winner == self._pending_chord:
            # Same as pending candidate — increment counter
            self._pending_count += 1

            if self._pending_count >= self._hysteresis_frames:
                # Transition: new chord has persisted long enough
                old_chord = self._current_chord
                self._current_chord = winner
                self._current_confidence = winner_confidence
                self._pending_chord = ""
                self._pending_count = 0
                self._last_change_time = time.monotonic()
                is_stable = True

                logger.info(
                    "Chord transition: '%s' -> '%s' (confidence=%.3f)",
                    old_chord or "(none)",
                    winner,
                    winner_confidence,
                )
            else:
                # Still waiting for hysteresis threshold
                is_stable = False

        else:
            # New candidate different from both current and pending — reset
            self._pending_chord = winner
            self._pending_count = 1

            if self._pending_count >= self._hysteresis_frames:
                # Immediate transition if hysteresis is 1
                old_chord = self._current_chord
                self._current_chord = winner
                self._current_confidence = winner_confidence
                self._pending_chord = ""
                self._pending_count = 0
                self._last_change_time = time.monotonic()
                is_stable = True

                logger.info(
                    "Chord transition: '%s' -> '%s' (confidence=%.3f)",
                    old_chord or "(none)",
                    winner,
                    winner_confidence,
                )
            else:
                is_stable = False

        return SmoothedResult(
            chord_name=self._current_chord,
            confidence=self._current_confidence,
            is_stable=is_stable,
            raw_chord=raw_chord,
        )
