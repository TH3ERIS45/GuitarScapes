"""Chroma feature extraction from FFT magnitude spectra.

Maps spectral energy to 12 pitch classes (C through B) using log-frequency
mapping, with L2 normalization and Numba-accelerated computation.
"""

from __future__ import annotations

import numpy as np
from numba import njit

from guitarscapes.utils.config import DetectionConfig
from guitarscapes.utils.logger import get_logger


logger = get_logger("detection.chroma")

# Pitch class names for logging
_PITCH_CLASSES: tuple[str, ...] = (
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
)


@njit(cache=True)
def _compute_chroma_numba(
    magnitudes: np.ndarray,
    frequencies: np.ndarray,
    reference_frequency: float,
    min_frequency: float,
    max_frequency: float,
) -> np.ndarray:
    """Map spectral magnitudes to 12 chroma bins (Numba-accelerated).

    For each frequency bin within the valid range, computes the
    corresponding pitch class via log-frequency mapping and accumulates
    the squared magnitude into the appropriate chroma bin.

    Args:
        magnitudes: Magnitude spectrum array.
        frequencies: Frequency values in Hz for each magnitude bin.
        reference_frequency: Reference tuning frequency in Hz (e.g., 440.0 for A4).
        min_frequency: Lower frequency bound in Hz.
        max_frequency: Upper frequency bound in Hz.

    Returns:
        12-element chroma vector (unnormalized).
    """
    chroma = np.zeros(12, dtype=np.float64)

    for i in range(len(frequencies)):
        freq = frequencies[i]
        if freq < min_frequency or freq > max_frequency:
            continue

        # Map frequency to pitch class via log2 ratio from reference
        # A4 = 440 Hz = pitch class 9 (A)
        semitones = 12.0 * np.log2(freq / reference_frequency) + 9.0
        pitch_class = int(np.round(semitones)) % 12
        # Ensure positive modulus
        if pitch_class < 0:
            pitch_class += 12

        # Accumulate energy (squared magnitude for power)
        chroma[pitch_class] += magnitudes[i] * magnitudes[i]

    return chroma


class ChromaExtractor:
    """Standard chroma feature extractor from FFT magnitude spectra.

    Computes a 12-element chroma vector by mapping spectral energy to pitch
    classes using log-frequency relationships, then applying L2 normalization.

    Args:
        config: Detection configuration parameters.
    """

    def __init__(self, config: DetectionConfig) -> None:
        self._config = config
        self._reference_frequency = config.reference_frequency
        self._min_frequency = config.min_frequency
        self._max_frequency = config.max_frequency

        logger.info(
            "ChromaExtractor initialized: reference=%.1f Hz, range=[%.1f, %.1f] Hz",
            self._reference_frequency,
            self._min_frequency,
            self._max_frequency,
        )

    def extract(self, magnitudes: np.ndarray, frequencies: np.ndarray) -> np.ndarray:
        """Extract a 12-element chroma vector from an FFT magnitude spectrum.

        Maps each frequency bin's energy to one of 12 pitch classes based on
        its log-frequency distance from the reference frequency, then applies
        L2 normalization to produce a unit-norm feature vector.

        Args:
            magnitudes: Magnitude spectrum array (positive frequencies).
            frequencies: Corresponding frequency values in Hz.

        Returns:
            L2-normalized 12-element numpy array representing chroma energy
            distribution across pitch classes C, C#, D, ..., B.
        """
        chroma = _compute_chroma_numba(
            np.asarray(magnitudes, dtype=np.float64),
            np.asarray(frequencies, dtype=np.float64),
            self._reference_frequency,
            self._min_frequency,
            self._max_frequency,
        )

        # L2 normalization
        norm = np.linalg.norm(chroma)
        if norm > 1e-10:
            chroma /= norm
        else:
            logger.debug("Chroma vector near-zero; skipping normalization")

        logger.debug(
            "Chroma extracted: dominant=%s (%.3f)",
            _PITCH_CLASSES[int(np.argmax(chroma))],
            float(np.max(chroma)),
        )

        return chroma
