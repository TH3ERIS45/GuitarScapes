"""Tests for HPCP extraction."""

from __future__ import annotations

import numpy as np
import pytest

from guitarscapes.utils.config import DetectionConfig
from guitarscapes.detection.hpcp import HPCPExtractor


class TestHPCPExtractor:
    """Test suite for HPCPExtractor.

    The HPCP implementation uses C=0, C#=1, D=2, ..., A=9, B=11.
    """

    @pytest.fixture
    def hpcp(self) -> HPCPExtractor:
        config = DetectionConfig()
        return HPCPExtractor(config=config)

    def test_returns_12_bins(self, hpcp):
        """HPCP should always return a 12-element vector."""
        freqs = np.array([440.0, 554.37, 659.25], dtype=np.float64)
        mags = np.array([1.0, 0.8, 0.6], dtype=np.float64)
        result = hpcp.extract(freqs, mags)
        assert result.shape == (12,)

    def test_a440_peak_activates_correct_bin(self, hpcp):
        """A single 440 Hz peak should activate bin 9 (A)."""
        freqs = np.array([440.0], dtype=np.float64)
        mags = np.array([1.0], dtype=np.float64)
        result = hpcp.extract(freqs, mags)

        # A = bin 9
        assert np.argmax(result) == 9
        assert result[9] > 0.5

    def test_c_major_chord_peaks(self, hpcp):
        """C major (C-E-G) should activate expected bins in HPCP.

        C=0, E=4, G=7.
        """
        freqs = np.array([261.63, 329.63, 392.00], dtype=np.float64)
        mags = np.array([1.0, 0.9, 0.8], dtype=np.float64)
        result = hpcp.extract(freqs, mags)

        # C=0, E=4, G=7 should be the three highest bins
        top3 = np.argsort(result)[-3:]
        assert 0 in top3   # C
        assert 4 in top3   # E
        assert 7 in top3   # G

    def test_empty_input_returns_zeros(self, hpcp):
        """No peaks should return a zero vector."""
        freqs = np.array([], dtype=np.float64)
        mags = np.array([], dtype=np.float64)
        result = hpcp.extract(freqs, mags)
        assert np.allclose(result, 0.0)

    def test_normalization(self, hpcp):
        """HPCP should be normalized to max = 1.0."""
        freqs = np.array([440.0, 554.37], dtype=np.float64)
        mags = np.array([1.0, 0.5], dtype=np.float64)
        result = hpcp.extract(freqs, mags)

        if np.max(result) > 0:
            assert abs(np.max(result) - 1.0) < 0.01

    def test_harmonic_weighting(self, hpcp):
        """A single peak should primarily activate the fundamental's bin."""
        freqs = np.array([440.0], dtype=np.float64)
        mags = np.array([1.0], dtype=np.float64)
        result = hpcp.extract(freqs, mags)

        # Bin 9 (A) should be the highest
        assert np.argmax(result) == 9
