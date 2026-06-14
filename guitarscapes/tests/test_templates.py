"""Tests for chord template bank and matching."""

from __future__ import annotations

import numpy as np
import pytest

from guitarscapes.utils.config import DetectionConfig
from guitarscapes.detection.templates import ChordTemplateBank
from guitarscapes.tests.conftest import generate_ideal_hpcp, CHORD_INTERVALS


class TestChordTemplateBank:
    """Test suite for ChordTemplateBank."""

    @pytest.fixture
    def bank(self) -> ChordTemplateBank:
        config = DetectionConfig()
        return ChordTemplateBank(config=config)

    def test_has_108_chords(self, bank):
        """Should have exactly 108 chord templates (12 roots × 9 types)."""
        names = bank.get_chord_names()
        assert len(names) == 108

    def test_all_chord_types_present(self, bank):
        """Every root should have all 9 chord types."""
        names = bank.get_chord_names()
        expected_suffixes = ["", "m", "7", "m7", "maj7", "sus2", "sus4", "dim", "aug"]
        for note in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]:
            for suffix in expected_suffixes:
                chord_name = f"{note}{suffix}"
                assert chord_name in names, f"Missing chord: {chord_name}"

    def test_templates_are_normalized(self, bank):
        """All templates should be L2-normalized."""
        names = bank.get_chord_names()
        for i, name in enumerate(names):
            template = bank._templates[i]
            norm = np.linalg.norm(template)
            assert abs(norm - 1.0) < 0.01, f"Template {name} norm={norm}"

    def test_c_major_match(self, bank):
        """Ideal C major HPCP should match C major template."""
        hpcp = generate_ideal_hpcp(0, [0, 4, 7])
        candidates = bank.match(hpcp)

        assert len(candidates) > 0
        assert candidates[0].chord_name == "C"
        assert candidates[0].confidence > 0.8

    def test_am_match(self, bank):
        """Ideal Am HPCP should match Am template."""
        hpcp = generate_ideal_hpcp(9, [0, 3, 7])
        candidates = bank.match(hpcp)

        assert candidates[0].chord_name == "Am"
        assert candidates[0].confidence > 0.8

    def test_g7_match(self, bank):
        """Ideal G7 HPCP should match G7 template."""
        hpcp = generate_ideal_hpcp(7, [0, 4, 7, 10])
        candidates = bank.match(hpcp)

        assert candidates[0].chord_name == "G7"
        assert candidates[0].confidence > 0.7

    def test_silence_returns_low_confidence(self, bank):
        """Zero HPCP should return no candidates (near-zero vector)."""
        hpcp = np.zeros(12, dtype=np.float64)
        candidates = bank.match(hpcp)

        # Should return empty list for near-zero input
        assert len(candidates) == 0

    def test_get_chord_index_round_trip(self, bank):
        """get_chord_index and chord_names should be consistent."""
        names = bank.get_chord_names()
        for i, name in enumerate(names):
            assert bank.get_chord_index(name) == i

    def test_noisy_hpcp_still_matches(self, bank):
        """Chord matching should be robust to moderate noise."""
        rng = np.random.default_rng(42)
        hpcp = generate_ideal_hpcp(0, [0, 4, 7])  # C major
        noise = rng.normal(0, 0.1, 12)
        noisy_hpcp = np.clip(hpcp + noise, 0, None)

        candidates = bank.match(noisy_hpcp)

        # C major should still be in the top 3
        top3_names = [c.chord_name for c in candidates[:3]]
        assert "C" in top3_names
