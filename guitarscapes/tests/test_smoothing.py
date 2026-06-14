"""Tests for temporal smoothing and hysteresis."""

from __future__ import annotations

import pytest

from guitarscapes.utils.config import DetectionConfig
from guitarscapes.detection.smoothing import TemporalSmoother


class TestTemporalSmoother:
    """Test suite for TemporalSmoother.

    The smoother uses hysteresis, requiring N consecutive frames of the
    same chord before switching. So the first prediction is NOT immediately
    accepted — it starts as empty and transitions after enough frames.
    """

    @pytest.fixture
    def smoother(self) -> TemporalSmoother:
        config = DetectionConfig(smoothing_window=5, hysteresis_frames=3)
        return TemporalSmoother(config=config)

    def test_first_prediction_is_pending(self, smoother):
        """The first chord should be pending (hysteresis not yet met)."""
        result = smoother.smooth("C", 0.9)
        # Current chord is empty because hysteresis hasn't been met yet
        assert result.chord_name == ""
        assert result.raw_chord == "C"

    def test_chord_accepted_after_hysteresis(self, smoother):
        """Chord should be accepted after N consecutive hysteresis frames."""
        # Feed the same chord multiple times to exceed hysteresis threshold
        for _ in range(5):
            result = smoother.smooth("C", 0.9)
        assert result.chord_name == "C"

    def test_consistent_predictions_stabilize(self, smoother):
        """Repeated same chord should become stable."""
        for _ in range(5):
            result = smoother.smooth("Am", 0.85)
        assert result.chord_name == "Am"
        assert result.is_stable

    def test_hysteresis_prevents_fast_switching(self, smoother):
        """Single different prediction shouldn't switch the chord."""
        # Establish Am
        for _ in range(5):
            smoother.smooth("Am", 0.85)

        # One blip of G
        result = smoother.smooth("G", 0.7)
        # Should NOT switch to G due to hysteresis
        assert result.chord_name == "Am"

    def test_sustained_change_switches(self, smoother):
        """Sustained new chord should eventually switch."""
        # Establish Am
        for _ in range(5):
            smoother.smooth("Am", 0.85)

        # Sustained G
        for _ in range(10):
            result = smoother.smooth("G", 0.9)

        assert result.chord_name == "G"

    def test_reset_clears_history(self, smoother):
        """Reset should clear all state."""
        for _ in range(5):
            smoother.smooth("Am", 0.85)

        smoother.reset()

        # After reset, chord needs hysteresis frames again
        result = smoother.smooth("C", 0.9)
        assert result.chord_name == ""  # Not yet accepted

        # Feed more frames
        for _ in range(5):
            result = smoother.smooth("C", 0.9)
        assert result.chord_name == "C"

    def test_raw_chord_preserved(self, smoother):
        """SmoothedResult should preserve the raw (unsmoothed) chord name."""
        for _ in range(5):
            smoother.smooth("Am", 0.85)

        result = smoother.smooth("G", 0.7)
        assert result.raw_chord == "G"

    def test_confidence_averaging(self, smoother):
        """Confidence should reflect an average of the window."""
        for conf in [0.6, 0.7, 0.8, 0.9, 1.0]:
            result = smoother.smooth("C", conf)

        # Average confidence should be reasonable
        assert 0.5 < result.confidence < 1.0

    def test_stability_with_varied_confidence(self, smoother):
        """Low confidence predictions should not destabilize easily."""
        # High confidence Am
        for _ in range(5):
            smoother.smooth("Am", 0.95)

        # Low confidence different chords
        result1 = smoother.smooth("G", 0.2)
        result2 = smoother.smooth("F", 0.1)

        # Should stay on Am due to low confidence of alternatives
        assert result1.chord_name == "Am"
        assert result2.chord_name == "Am"
