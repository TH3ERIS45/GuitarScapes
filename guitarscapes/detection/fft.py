"""FFT processing with peak detection for chord analysis.

Performs windowed FFT and extracts spectral peaks using parabolic interpolation
for sub-bin frequency accuracy, accelerated with Numba JIT compilation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numba import njit

from guitarscapes.utils.config import DetectionConfig
from guitarscapes.utils.logger import get_logger


logger = get_logger("detection.fft")


@dataclass(frozen=True, slots=True)
class FFTResult:
    """Result of FFT analysis on a single audio frame.

    Attributes:
        magnitudes: Full magnitude spectrum (positive frequencies only).
        frequencies: Corresponding frequency values in Hz for each bin.
        peak_indices: Indices of detected spectral peaks.
        peak_frequencies: Interpolated frequencies of detected peaks in Hz.
        peak_magnitudes: Interpolated magnitudes of detected peaks.
    """

    magnitudes: np.ndarray
    frequencies: np.ndarray
    peak_indices: np.ndarray
    peak_frequencies: np.ndarray
    peak_magnitudes: np.ndarray


@njit(cache=True)
def _detect_peaks_numba(
    magnitudes: np.ndarray,
    frequencies: np.ndarray,
    threshold: float,
    min_freq: float,
    max_freq: float,
    freq_resolution: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Detect spectral peaks with parabolic interpolation (Numba-accelerated).

    Identifies local maxima in the magnitude spectrum that exceed the given
    threshold, then refines their frequency and magnitude estimates using
    parabolic interpolation on the three bins surrounding each peak.

    Args:
        magnitudes: Magnitude spectrum array.
        frequencies: Frequency array corresponding to magnitude bins.
        threshold: Minimum magnitude for a bin to qualify as a peak.
        min_freq: Lower frequency bound in Hz.
        max_freq: Upper frequency bound in Hz.
        freq_resolution: Frequency spacing between adjacent bins in Hz.

    Returns:
        Tuple of (peak_indices, peak_frequencies, peak_magnitudes) arrays.
    """
    n = len(magnitudes)
    # Pre-allocate worst-case arrays
    indices = np.empty(n, dtype=np.int64)
    interp_freqs = np.empty(n, dtype=np.float64)
    interp_mags = np.empty(n, dtype=np.float64)
    count = 0

    for i in range(1, n - 1):
        mag_i = magnitudes[i]

        # Must exceed threshold and be a local maximum
        if mag_i < threshold:
            continue
        if mag_i <= magnitudes[i - 1] or mag_i <= magnitudes[i + 1]:
            continue

        # Parabolic interpolation for sub-bin accuracy
        alpha = magnitudes[i - 1]
        beta = mag_i
        gamma = magnitudes[i + 1]

        denominator = alpha - 2.0 * beta + gamma
        if abs(denominator) < 1e-12:
            p = 0.0
        else:
            p = 0.5 * (alpha - gamma) / denominator

        interpolated_freq = frequencies[i] + p * freq_resolution
        interpolated_mag = beta - 0.25 * (alpha - gamma) * p

        # Filter by frequency range
        if interpolated_freq < min_freq or interpolated_freq > max_freq:
            continue

        indices[count] = i
        interp_freqs[count] = interpolated_freq
        interp_mags[count] = interpolated_mag
        count += 1

    return indices[:count].copy(), interp_freqs[:count].copy(), interp_mags[:count].copy()


class FFTProcessor:
    """Windowed FFT processor with spectral peak detection.

    Uses a Hann window to reduce spectral leakage and Numba-accelerated peak
    detection with parabolic interpolation for sub-bin frequency accuracy.

    Args:
        config: Detection configuration parameters.
        sample_rate: Audio sample rate in Hz.
    """

    def __init__(self, config: DetectionConfig, sample_rate: int = 22050) -> None:
        self._config = config
        self._sample_rate = sample_rate
        self._fft_size = config.fft_size
        self._window = np.hanning(self._fft_size).astype(np.float64)
        self._freq_resolution = sample_rate / self._fft_size

        # Pre-compute frequency axis for positive frequencies
        self._frequencies = np.fft.rfftfreq(self._fft_size, d=1.0 / sample_rate)

        # Absolute threshold derived from config peak_threshold
        self._threshold = config.peak_threshold

        logger.info(
            "FFTProcessor initialized: fft_size=%d, sample_rate=%d, "
            "freq_resolution=%.2f Hz, freq_range=[%.1f, %.1f] Hz",
            self._fft_size,
            sample_rate,
            self._freq_resolution,
            config.min_frequency,
            config.max_frequency,
        )

    def process(self, audio_frame: np.ndarray) -> FFTResult:
        """Compute windowed FFT and detect spectral peaks.

        Applies a Hann window, computes the FFT magnitude spectrum, and
        identifies peaks using parabolic interpolation for sub-bin accuracy.

        Args:
            audio_frame: Input audio samples. If longer than fft_size, only
                the last fft_size samples are used. If shorter, the frame is
                zero-padded to fft_size.

        Returns:
            FFTResult containing magnitude spectrum and detected peaks.
        """
        frame = np.asarray(audio_frame, dtype=np.float64)

        # Ensure correct frame length
        if len(frame) > self._fft_size:
            frame = frame[-self._fft_size :]
        elif len(frame) < self._fft_size:
            padded = np.zeros(self._fft_size, dtype=np.float64)
            padded[: len(frame)] = frame
            frame = padded

        # Apply Hann window
        windowed = frame * self._window

        # Compute FFT — positive frequencies only
        spectrum = np.fft.rfft(windowed)
        magnitudes = np.abs(spectrum) * (2.0 / self._fft_size)

        # Detect peaks with parabolic interpolation via Numba
        peak_indices, peak_frequencies, peak_magnitudes = _detect_peaks_numba(
            magnitudes,
            self._frequencies,
            self._threshold,
            self._config.min_frequency,
            self._config.max_frequency,
            self._freq_resolution,
        )

        logger.debug(
            "FFT processed: %d peaks detected in [%.1f, %.1f] Hz",
            len(peak_indices),
            self._config.min_frequency,
            self._config.max_frequency,
        )

        return FFTResult(
            magnitudes=magnitudes,
            frequencies=self._frequencies,
            peak_indices=peak_indices,
            peak_frequencies=peak_frequencies,
            peak_magnitudes=peak_magnitudes,
        )
