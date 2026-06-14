"""Chord template matching using cosine similarity.

Defines a bank of 108 chord templates (9 types × 12 roots) and provides
vectorized matching against HPCP vectors to identify chord candidates.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from guitarscapes.utils.config import DetectionConfig
from guitarscapes.utils.logger import get_logger


logger = get_logger("detection.templates")


@dataclass(frozen=True, slots=True)
class ChordCandidate:
    """A candidate chord match with confidence score.

    Attributes:
        chord_name: Human-readable chord name (e.g., "Am7", "G", "F#dim").
        confidence: Cosine similarity score in [0, 1].
        chord_index: Index into the template bank (0–107).
    """

    chord_name: str
    confidence: float
    chord_index: int


# Note names in chromatic order starting from C
NOTE_NAMES: tuple[str, ...] = (
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
)

# Chord type definitions: suffix and semitone intervals from root
CHORD_TYPES: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("", (0, 4, 7)),           # major
    ("m", (0, 3, 7)),          # minor
    ("7", (0, 4, 7, 10)),      # dominant 7
    ("m7", (0, 3, 7, 10)),     # minor 7
    ("maj7", (0, 4, 7, 11)),   # major 7
    ("sus2", (0, 2, 7)),       # suspended 2
    ("sus4", (0, 5, 7)),       # suspended 4
    ("dim", (0, 3, 6)),        # diminished
    ("aug", (0, 4, 8)),        # augmented
)


def _build_template(intervals: tuple[int, ...], root: int) -> np.ndarray:
    """Build and L2-normalize a single chord template.

    Args:
        intervals: Semitone intervals relative to the root.
        root: Root note index (0=C, 1=C#, ..., 11=B).

    Returns:
        L2-normalized 12-element template vector.
    """
    template = np.zeros(12, dtype=np.float64)
    for interval in intervals:
        template[(root + interval) % 12] = 1.0

    norm = np.linalg.norm(template)
    if norm > 0:
        template /= norm

    return template


class ChordTemplateBank:
    """Bank of chord templates for matching against HPCP vectors.

    Pre-computes 108 L2-normalized chord templates (9 types × 12 roots)
    and uses vectorized cosine similarity for efficient matching.

    Args:
        config: Detection configuration parameters.
    """

    def __init__(self, config: DetectionConfig) -> None:
        self._config = config
        self._top_k = config.top_k_candidates

        # Build all templates and chord names
        self._chord_names: list[str] = []
        templates: list[np.ndarray] = []

        for root_idx, root_name in enumerate(NOTE_NAMES):
            for suffix, intervals in CHORD_TYPES:
                chord_name = f"{root_name}{suffix}"
                self._chord_names.append(chord_name)
                templates.append(_build_template(intervals, root_idx))

        # Stack into (108, 12) array for vectorized operations
        self._templates = np.array(templates, dtype=np.float64)

        # Build name-to-index lookup
        self._name_to_index: dict[str, int] = {
            name: idx for idx, name in enumerate(self._chord_names)
        }

        logger.info(
            "ChordTemplateBank initialized: %d templates (%d roots × %d types), top_k=%d",
            len(self._chord_names),
            len(NOTE_NAMES),
            len(CHORD_TYPES),
            self._top_k,
        )

    @property
    def num_chords(self) -> int:
        """Total number of chord templates in the bank."""
        return len(self._chord_names)

    def get_chord_names(self) -> list[str]:
        """Return all chord names in template order.

        Returns:
            List of 108 chord name strings.
        """
        return list(self._chord_names)

    def get_chord_index(self, name: str) -> int:
        """Look up the index of a chord by name.

        Args:
            name: Chord name string (e.g., "Am", "C#7").

        Returns:
            Zero-based index into the template bank.

        Raises:
            KeyError: If the chord name is not found.
        """
        return self._name_to_index[name]

    def match(self, hpcp: np.ndarray) -> list[ChordCandidate]:
        """Match an HPCP vector against all chord templates.

        Computes cosine similarity between the input HPCP vector and all
        108 templates, returning the top K candidates sorted by confidence
        (descending).

        Args:
            hpcp: 12-element HPCP vector (should be non-negative).

        Returns:
            List of top K ChordCandidate instances, sorted by descending
            confidence. Returns fewer candidates if the input is near-zero.
        """
        hpcp = np.asarray(hpcp, dtype=np.float64)

        # L2-normalize input for cosine similarity
        hpcp_norm = np.linalg.norm(hpcp)
        if hpcp_norm < 1e-10:
            logger.debug("Near-zero HPCP vector; returning empty candidates")
            return []

        hpcp_unit = hpcp / hpcp_norm

        # Vectorized cosine similarity: templates are already L2-normalized
        similarities = self._templates @ hpcp_unit  # shape: (108,)

        # Clip to [0, 1] — negative similarities are irrelevant
        similarities = np.clip(similarities, 0.0, 1.0)

        # Get top K indices
        top_k = min(self._top_k, len(similarities))
        top_indices = np.argpartition(similarities, -top_k)[-top_k:]
        top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]

        candidates = [
            ChordCandidate(
                chord_name=self._chord_names[idx],
                confidence=float(similarities[idx]),
                chord_index=int(idx),
            )
            for idx in top_indices
        ]

        logger.debug(
            "Template matching: top=%s (%.3f), runner-up=%s (%.3f)",
            candidates[0].chord_name if candidates else "N/A",
            candidates[0].confidence if candidates else 0.0,
            candidates[1].chord_name if len(candidates) > 1 else "N/A",
            candidates[1].confidence if len(candidates) > 1 else 0.0,
        )

        return candidates
