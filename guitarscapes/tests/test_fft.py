"""Tests for FFT processing and peak detection."""

from __future__ import annotations

import numpy as np
import pytest

from guitarscapes.utils.config import DetectionConfig
from guitarscapes.detection.fft import FFTProcessor
from guitarscapes.tests.conftest import generate_sine_wave, SAMPLE_RATE, FFT_SIZE


class TestFFTProcessor:
    """Test suite for FFTProcessor."""

    @pytest.fixture
    def fft_processor(self) -> FFTProcessor:
        config = DetectionConfig()
        return FFTProcessor(config=config, sample_rate=SAMPLE_RATE)

    def test_process_returns_correct_shape(self, fft_processor):
        """FFT result should have correct array shapes."""
        signal = generate_sine_wave(440.0, duration=0.2)
        frame = np.zeros(FFT_SIZE, dtype=np.float32)
        frame[: len(signal)] = signal[: FFT_SIZE]

        result = fft_processor.process(frame)

        assert result.magnitudes.ndim == 1
        assert result.frequencies.ndim == 1
        assert len(result.magnitudes) == len(result.frequencies)

    def test_detects_440hz_peak(self, fft_processor):
        """Should detect a peak near 440 Hz for a 440 Hz sine wave."""
        signal = generate_sine_wave(440.0, duration=0.2)
        frame = np.zeros(FFT_SIZE, dtype=np.float32)
        frame[: min(len(signal), FFT_SIZE)] = signal[: FFT_SIZE]

        result = fft_processor.process(frame)

        # Should find at least one peak near 440 Hz
        assert len(result.peak_frequencies) > 0
        closest = result.peak_frequencies[
            np.argmin(np.abs(result.peak_frequencies - 440.0))
        ]
        assert abs(closest - 440.0) < 15.0  # Within ~15 Hz

    def test_detects_multiple_frequencies(self, fft_processor):
        """Should detect peaks for a composite signal."""
        t = np.arange(FFT_SIZE) / SAMPLE_RATE
        signal = (
            0.5 * np.sin(2 * np.pi * 440.0 * t)
            + 0.3 * np.sin(2 * np.pi * 880.0 * t)
        ).astype(np.float32)

        result = fft_processor.process(signal)

        assert len(result.peak_frequencies) >= 2

    def test_silence_produces_no_peaks(self, fft_processor):
        """Silent input should produce no significant peaks."""
        signal = np.zeros(FFT_SIZE, dtype=np.float32)
        result = fft_processor.process(signal)

        # May have zero or very few peaks with negligible magnitude
        if len(result.peak_magnitudes) > 0:
            assert np.max(result.peak_magnitudes) < 0.1

    def test_frequency_range_filtering(self, fft_processor):
        """Peaks outside the frequency range should be filtered out."""
        result_data = fft_processor.process(
            generate_sine_wave(440.0, duration=0.2)[: FFT_SIZE].astype(np.float32)
        )

        for freq in result_data.peak_frequencies:
            assert freq >= 60.0
            assert freq <= 5000.0
