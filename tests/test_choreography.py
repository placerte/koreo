"""Tests for GUI-independent choreography editing."""

from fractions import Fraction

import pytest

from koreo.domain.choreography import (
    ChoreographyEditError,
    create_move,
    ripple_later_moves,
    trim_edited_move,
    update_move,
)
from koreo.domain.models import Move
from conftest import make_project


def test_create_update_and_same_track_overlap_validation() -> None:
    project = create_move(
        make_project(), "track-1", Fraction(0), Fraction(8), move_id="first"
    )
    project = update_move(project, "first", label="Swingout", notes="Stretch")
    move = project.moves[0]
    assert (move.label, move.notes) == ("Swingout", "Stretch")

    with pytest.raises(ChoreographyEditError, match="overlaps"):
        create_move(project, "track-1", Fraction(4), Fraction(8))


def test_trim_changes_only_the_edited_move() -> None:
    project = make_project(
        moves=(Move("existing", "track-1", Fraction(8), Fraction(8), "Existing"),)
    )

    result = trim_edited_move(
        project,
        None,
        "track-1",
        Fraction(4),
        Fraction(8),
        Fraction(6),
        label="New",
    )

    existing = next(move for move in result.moves if move.id == "existing")
    created = next(move for move in result.moves if move.id != "existing")
    assert (existing.start, existing.duration) == (Fraction(8), Fraction(8))
    assert (created.start, created.duration) == (Fraction(4), Fraction(4))


def test_shift_ripples_conflicting_and_later_moves_preserving_gaps() -> None:
    project = make_project(
        moves=(
            Move("one", "track-1", Fraction(8), Fraction(4), "One"),
            Move("two", "track-1", Fraction(14), Fraction(2), "Two"),
        )
    )
    edited = Move("new", "track-1", Fraction(10), Fraction(4), "New")

    result = ripple_later_moves(project, edited, original_id=None)
    by_id = {move.id: move for move in result.moves}

    assert by_id["new"].start == 10
    assert by_id["one"].start == 14
    assert by_id["two"].start == 20
    assert by_id["two"].duration == 2
