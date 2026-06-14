"""Tests for neural refiner ONNX model loading and fallback."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from guitarscapes.detection.neural_refiner import NeuralRefiner
from guitarscapes.detection.templates import ChordCandidate


class TestNeuralRefiner:
    """Test suite for NeuralRefiner."""

    def test_graceful_fallback_when_no_model(self):
        """Should return candidates unchanged when no model file exists."""
        refiner = NeuralRefiner(model_path=Path("/nonexistent/model.onnx"))

        assert not refiner.is_available

        candidates = [
            ChordCandidate(chord_name="C", confidence=0.9, chord_index=0),
            ChordCandidate(chord_name="Am", confidence=0.7, chord_index=9),
            ChordCandidate(chord_name="G", confidence=0.5, chord_index=7),
        ]
        hpcp = np.random.rand(12).astype(np.float32)
        chord_names = [f"chord_{i}" for i in range(108)]

        result = refiner.refine(hpcp, candidates, chord_names)

        # Should return candidates unchanged
        assert len(result) == len(candidates)
        assert result[0].chord_name == "C"
        assert result[0].confidence == 0.9

    def test_none_model_path(self):
        """Should handle None model path gracefully."""
        refiner = NeuralRefiner(model_path=None)
        assert not refiner.is_available

    def test_is_available_with_no_model(self):
        """is_available should be False when model doesn't exist."""
        refiner = NeuralRefiner(model_path=Path("/tmp/nonexistent.onnx"))
        assert refiner.is_available is False

    def test_refine_preserves_candidate_order_on_fallback(self):
        """Fallback should preserve the original candidate ordering."""
        refiner = NeuralRefiner(model_path=None)

        candidates = [
            ChordCandidate(chord_name="Em", confidence=0.85, chord_index=4),
            ChordCandidate(chord_name="Am", confidence=0.6, chord_index=9),
            ChordCandidate(chord_name="C", confidence=0.4, chord_index=0),
        ]
        hpcp = np.zeros(12, dtype=np.float32)
        names = [f"c{i}" for i in range(108)]

        result = refiner.refine(hpcp, candidates, names)

        assert result[0].chord_name == "Em"
        assert result[1].chord_name == "Am"
        assert result[2].chord_name == "C"
