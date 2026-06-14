"""Shared test fixtures for GuitarScapes Pro test suite."""

from __future__ import annotations

import numpy as np
import pytest


# ── Constants ──────────────────────────────────────────────────────────────

SAMPLE_RATE = 22050
FFT_SIZE = 4096
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Standard tuning frequencies (A4 = 440 Hz)
NOTE_FREQUENCIES = {
    "C4": 261.63, "C#4": 277.18, "D4": 293.66, "D#4": 311.13,
    "E4": 329.63, "F4": 349.23, "F#4": 369.99, "G4": 392.00,
    "G#4": 415.30, "A4": 440.00, "A#4": 466.16, "B4": 493.88,
    "C3": 130.81, "E3": 164.81, "G3": 196.00, "A3": 220.00,
    "C5": 523.25, "E5": 659.25,
}

CHORD_INTERVALS = {
    "major": [0, 4, 7],
    "m": [0, 3, 7],
    "7": [0, 4, 7, 10],
    "m7": [0, 3, 7, 10],
    "maj7": [0, 4, 7, 11],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
}


# ── Helpers ────────────────────────────────────────────────────────────────

def generate_sine_wave(
    frequency: float,
    duration: float = 0.2,
    sample_rate: int = SAMPLE_RATE,
    amplitude: float = 0.5,
) -> np.ndarray:
    """Generate a pure sine wave at the given frequency."""
    t = np.arange(int(duration * sample_rate)) / sample_rate
    return (amplitude * np.sin(2 * np.pi * frequency * t)).astype(np.float32)


def generate_chord_signal(
    root_freq: float,
    intervals: list[int],
    duration: float = 0.2,
    sample_rate: int = SAMPLE_RATE,
    amplitude: float = 0.3,
    n_harmonics: int = 3,
) -> np.ndarray:
    """Generate a synthetic chord signal with harmonics.

    Creates a sum of sine waves for each note in the chord, each with
    a few harmonics to simulate a guitar-like timbre.
    """
    t = np.arange(int(duration * sample_rate)) / sample_rate
    signal = np.zeros_like(t, dtype=np.float32)

    for interval in intervals:
        # Frequency of this chord tone
        freq = root_freq * (2 ** (interval / 12.0))
        for h in range(1, n_harmonics + 1):
            harmonic_amp = amplitude / (h ** 1.5)
            signal += harmonic_amp * np.sin(2 * np.pi * freq * h * t).astype(
                np.float32
            )

    # Normalize
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * amplitude

    return signal


def generate_ideal_hpcp(root_index: int, intervals: list[int]) -> np.ndarray:
    """Generate an ideal 12-element HPCP vector for a chord.

    Args:
        root_index: Index of the root note (0=C, 1=C#, ..., 11=B).
        intervals: Semitone intervals from the root.

    Returns:
        A 12-element normalized HPCP vector.
    """
    hpcp = np.zeros(12, dtype=np.float64)
    for interval in intervals:
        bin_idx = (root_index + interval) % 12
        hpcp[bin_idx] = 1.0

    # Normalize
    max_val = np.max(hpcp)
    if max_val > 0:
        hpcp /= max_val
    return hpcp


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def sample_rate() -> int:
    """Default sample rate for tests."""
    return SAMPLE_RATE


@pytest.fixture
def fft_size() -> int:
    """Default FFT size for tests."""
    return FFT_SIZE


@pytest.fixture
def sine_440() -> np.ndarray:
    """A 440 Hz sine wave (A4), 0.2 seconds."""
    return generate_sine_wave(440.0)


@pytest.fixture
def sine_261() -> np.ndarray:
    """A 261.63 Hz sine wave (C4), 0.2 seconds."""
    return generate_sine_wave(261.63)


@pytest.fixture
def c_major_signal() -> np.ndarray:
    """Synthetic C major chord (C-E-G) signal."""
    return generate_chord_signal(
        root_freq=261.63,
        intervals=[0, 4, 7],
        duration=0.2,
    )


@pytest.fixture
def am_chord_signal() -> np.ndarray:
    """Synthetic A minor chord (A-C-E) signal."""
    return generate_chord_signal(
        root_freq=220.0,
        intervals=[0, 3, 7],
        duration=0.2,
    )


@pytest.fixture
def g_major_signal() -> np.ndarray:
    """Synthetic G major chord signal."""
    return generate_chord_signal(
        root_freq=196.0,
        intervals=[0, 4, 7],
        duration=0.2,
    )


@pytest.fixture
def silence() -> np.ndarray:
    """A silent audio frame."""
    return np.zeros(FFT_SIZE, dtype=np.float32)


@pytest.fixture
def noise_signal() -> np.ndarray:
    """Random white noise signal."""
    rng = np.random.default_rng(42)
    return (rng.standard_normal(FFT_SIZE) * 0.01).astype(np.float32)


@pytest.fixture
def c_major_hpcp() -> np.ndarray:
    """Ideal HPCP vector for C major chord."""
    return generate_ideal_hpcp(0, [0, 4, 7])


@pytest.fixture
def am_hpcp() -> np.ndarray:
    """Ideal HPCP vector for A minor chord."""
    return generate_ideal_hpcp(9, [0, 3, 7])
