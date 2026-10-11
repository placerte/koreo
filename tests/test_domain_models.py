"""Tests for exact musical coordinates and immutable entities."""

# [GH-4] [T-01] [T-05]

from dataclasses import FrozenInstanceError
from fractions import Fraction

import pytest

from koreo.domain.models import Move, MusicalRegion


def test_fractional_timing_is_exact() -> None:
    region = MusicalRegion(
        id="pickup",
        label="Pickup",
        start=Fraction(-1, 2),
        duration=Fraction(5, 2),
    )

    assert region.end == Fraction(2)
    assert region.start + Fraction(1, 3) == Fraction(-1, 6)


def test_entity_identity_is_independent_from_label() -> None:
    first = MusicalRegion("a-1", "A", Fraction(0), Fraction(8))
    second = MusicalRegion("a-2", "A", Fraction(8), Fraction(8))

    assert first.label == second.label
    assert first.id != second.id


def test_entities_are_immutable() -> None:
    move = Move("move-1", "track-1", Fraction(0), Fraction(1), "Step")

    with pytest.raises(FrozenInstanceError):
        move.label = "Changed"  # type: ignore[misc]
