"""Harmonic Pitch Class Profile (HPCP) extraction from spectral peaks.

Computes a 12-element HPCP vector from detected spectral peaks, using
harmonic series weighting (1/h²), squared cosine bin assignment, and
unit-max normalization. Core computation is Numba-accelerated.
"""

from __future__ import annotations

import numpy as np
from numba import njit

from guitarscapes.utils.config import DetectionConfig
from guitarscapes.utils.logger import get_logger


logger = get_logger("detection.hpcp")

_PITCH_CLASSES: tuple[str, ...] = (
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
)


@njit(cache=True)
def _compute_hpcp_numba(
    peak_frequencies: np.ndarray,
    peak_magnitudes: np.ndarray,
    reference_frequency: float,
    n_harmonics: int,
    min_frequency: float,
    max_frequency: float,
    n_bins: int,
) -> np.ndarray:
    """Compute HPCP vector from spectral peaks (Numba-accelerated).

    For each spectral peak, considers harmonics 1 through n_harmonics. Each
    harmonic's fundamental frequency is computed, then mapped to a pitch class.
    Contributions are weighted by 1/h² (harmonic weighting) and by squared
    cosine distance to the nearest bin center.

    Args:
        peak_frequencies: Detected peak frequencies in Hz.
        peak_magnitudes: Corresponding peak magnitudes.
        reference_frequency: Reference tuning frequency in Hz.
        n_harmonics: Number of harmonics to consider (1 = fundamental only).
        min_frequency: Lower frequency bound in Hz.
        max_frequency: Upper frequency bound in Hz.
        n_bins: Number of HPCP bins (12 for standard pitch classes).

    Returns:
        n_bins-element HPCP vector (unnormalized).
    """
    hpcp = np.zeros(n_bins, dtype=np.float64)

    for i in range(len(peak_frequencies)):
        freq = peak_frequencies[i]
        mag = peak_magnitudes[i]

        if freq < min_frequency or freq > max_frequency:
            continue

        for h in range(1, n_harmonics + 1):
            # Compute the fundamental frequency for this harmonic interpretation
            fundamental = freq / h
            if fundamental < min_frequency:
                continue

            # Harmonic weighting: 1/h²
            harmonic_weight = 1.0 / (h * h)

            # Map fundamental to continuous semitone value
            # A4 = 440 Hz => pitch class index 9 (A)
            semitones = 12.0 * np.log2(fundamental / reference_frequency) + 9.0
            continuous_bin = semitones % n_bins
            if continuous_bin < 0.0:
                continuous_bin += n_bins

            # Distribute energy to the two nearest bins using squared cosine
            bin_lower = int(np.floor(continuous_bin)) % n_bins
            bin_upper = (bin_lower + 1) % n_bins

            fractional = continuous_bin - np.floor(continuous_bin)

            # Squared cosine weighting for smooth bin assignment
            weight_upper = np.cos((1.0 - fractional) * np.pi / 2.0) ** 2
            weight_lower = np.cos(fractional * np.pi / 2.0) ** 2

            contribution = mag * mag * harmonic_weight
            hpcp[bin_lower] += contribution * weight_lower
            hpcp[bin_upper] += contribution * weight_upper

    return hpcp


class HPCPExtractor:
    """Harmonic Pitch Class Profile extractor from spectral peaks.

    Unlike standard chroma features which use all spectral bins, HPCP
    operates on detected spectral peaks, considering multiple harmonics
    with decreasing weight (1/h²) and using squared cosine weighting for
    smooth bin assignment.

    Args:
        config: Detection configuration parameters.
    """

    def __init__(self, config: DetectionConfig) -> None:
        self._config = config
        self._reference_frequency = config.reference_frequency
        self._n_harmonics = config.n_harmonics
        self._min_frequency = config.min_frequency
        self._max_frequency = config.max_frequency
        self._n_bins = config.hpcp_bins

        logger.info(
            "HPCPExtractor initialized: reference=%.1f Hz, harmonics=%d, "
            "bins=%d, range=[%.1f, %.1f] Hz",
            self._reference_frequency,
            self._n_harmonics,
            self._n_bins,
            self._min_frequency,
            self._max_frequency,
        )

    def extract(
        self,
        peak_frequencies: np.ndarray,
        peak_magnitudes: np.ndarray,
    ) -> np.ndarray:
        """Extract a 12-element HPCP vector from spectral peaks.

        Considers harmonics 1 through n_harmonics for each peak, applying
        1/h² harmonic weighting and squared cosine bin assignment, followed
        by unit-max normalization.

        Args:
            peak_frequencies: Frequencies of detected spectral peaks in Hz.
            peak_magnitudes: Corresponding magnitudes of the peaks.

        Returns:
            Unit-max-normalized 12-element numpy array representing the
            Harmonic Pitch Class Profile across C, C#, D, ..., B.
        """
        hpcp = _compute_hpcp_numba(
            np.asarray(peak_frequencies, dtype=np.float64),
            np.asarray(peak_magnitudes, dtype=np.float64),
            self._reference_frequency,
            self._n_harmonics,
            self._min_frequency,
            self._max_frequency,
            self._n_bins,
        )

        # Unit-max normalization
        max_val = np.max(hpcp)
        if max_val > 1e-10:
            hpcp /= max_val
        else:
            logger.debug("HPCP vector near-zero; skipping normalization")

        logger.debug(
            "HPCP extracted: %d peaks -> dominant=%s (%.3f)",
            len(peak_frequencies),
            _PITCH_CLASSES[int(np.argmax(hpcp))],
            float(np.max(hpcp)),
        )

        return hpcp
