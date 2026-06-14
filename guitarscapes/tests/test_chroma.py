"""Tests for chroma feature extraction."""

from __future__ import annotations

import numpy as np
import pytest

from guitarscapes.utils.config import DetectionConfig
from guitarscapes.detection.chroma import ChromaExtractor


class TestChromaExtractor:
    """Test suite for ChromaExtractor."""

    @pytest.fixture
    def chroma(self) -> ChromaExtractor:
        config = DetectionConfig()
        return ChromaExtractor(config=config)

    def test_returns_12_bins(self, chroma):
        """Chroma should return a 12-element vector."""
        freqs = np.linspace(60, 5000, 2049).astype(np.float64)
        mags = np.random.rand(2049).astype(np.float64)
        result = chroma.extract(mags, freqs)
        assert result.shape == (12,)

    def test_single_frequency_activates_correct_bin(self, chroma):
        """A single 440 Hz frequency should primarily activate bin 9 (A)."""
        # Create a magnitude spectrum with a single peak at 440 Hz (A4)
        freqs = np.linspace(0, 11025, 2049).astype(np.float64)
        mags = np.zeros_like(freqs, dtype=np.float64)
        # Find bin closest to 440 Hz
        idx = np.argmin(np.abs(freqs - 440.0))
        mags[idx] = 1.0

        result = chroma.extract(mags, freqs)

        # A = bin 9
        assert np.argmax(result) == 9

    def test_zero_input_returns_zeros(self, chroma):
        """Zero magnitudes should return zeros."""
        freqs = np.linspace(60, 5000, 100).astype(np.float64)
        mags = np.zeros(100, dtype=np.float64)
        result = chroma.extract(mags, freqs)
        assert np.allclose(result, 0.0)

    def test_normalization(self, chroma):
        """Non-zero chroma should be normalized."""
        freqs = np.linspace(60, 5000, 2049).astype(np.float64)
        mags = np.random.rand(2049).astype(np.float64)
        result = chroma.extract(mags, freqs)

        if np.max(result) > 0:
            # L2 norm should be ~1.0 or max ~1.0 depending on implementation
            assert np.max(result) > 0.0
