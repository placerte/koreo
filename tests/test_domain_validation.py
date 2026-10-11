"""Tests for centralized project validation."""

# [GH-5] [T-02] [T-03] [T-04] [T-05]

from fractions import Fraction
from collections.abc import Callable
from typing import cast

import pytest

from koreo.domain.models import ChoreographyTrack, Move, MusicalRegion, Project
from koreo.domain.validation import ProjectValidationError, validate_project

from conftest import make_project


def assert_issue(project_error: ProjectValidationError, code: str) -> None:
    """Assert that a collected validation error contains ``code``."""

    assert code in {issue.code for issue in project_error.issues}


def test_valid_nested_adjacent_and_gapped_regions_pass() -> None:
    regions = (
        MusicalRegion("song", "Song", Fraction(0), Fraction(32)),
        MusicalRegion("a", "A", Fraction(0), Fraction(8), "song"),
        MusicalRegion("b", "B", Fraction(8), Fraction(8), "song"),
        MusicalRegion("a-2", "A", Fraction(20), Fraction(8), "song"),
    )

    validate_project(make_project(regions=regions))


@pytest.mark.parametrize(
    ("regions", "code"),
    [
        (
            (MusicalRegion("child", "Child", Fraction(0), Fraction(4), "missing"),),
            "missing_region_parent",
        ),
        (
            (
                MusicalRegion("one", "One", Fraction(0), Fraction(8), "two"),
                MusicalRegion("two", "Two", Fraction(0), Fraction(8), "one"),
            ),
            "region_cycle",
        ),
        (
            (
                MusicalRegion("parent", "Parent", Fraction(0), Fraction(8)),
                MusicalRegion("child", "Child", Fraction(7), Fraction(2), "parent"),
            ),
            "region_outside_parent",
        ),
        (
            (
                MusicalRegion("one", "One", Fraction(0), Fraction(8)),
                MusicalRegion("two", "Two", Fraction(7), Fraction(8)),
            ),
            "overlapping_regions",
        ),
    ],
)
def test_invalid_region_hierarchies_fail(
    regions: tuple[MusicalRegion, ...], code: str
) -> None:
    with pytest.raises(ProjectValidationError) as caught:
        validate_project(make_project(regions=regions))

    assert_issue(caught.value, code)
    assert caught.value.issues[0].message


def test_adjacent_and_gapped_moves_on_one_track_pass() -> None:
    moves = (
        Move("one", "track-1", Fraction(0), Fraction(2), "One"),
        Move("two", "track-1", Fraction(2), Fraction(1), "Two"),
        Move("three", "track-1", Fraction(5), Fraction(2), "Three"),
    )

    validate_project(make_project(moves=moves))


def test_same_track_overlap_fails_but_cross_track_overlap_passes() -> None:
    tracks = (
        ChoreographyTrack("lead", "Lead", 0, "#3366cc"),
        ChoreographyTrack("follow", "Follow", 1, "#cc6633"),
    )
    valid_moves = (
        Move("lead-one", "lead", Fraction(0), Fraction(4), "Lead"),
        Move("follow-one", "follow", Fraction(1), Fraction(4), "Follow"),
    )
    validate_project(make_project(tracks=tracks, moves=valid_moves))

    invalid_moves = valid_moves + (
        Move("lead-two", "lead", Fraction(3), Fraction(2), "Overlap"),
    )
    with pytest.raises(ProjectValidationError) as caught:
        validate_project(make_project(tracks=tracks, moves=invalid_moves))

    assert_issue(caught.value, "overlapping_moves")


@pytest.mark.parametrize(
    ("project_factory", "code"),
    [
        (
            lambda: make_project(
                tracks=(
                    ChoreographyTrack("duplicate", "One", 0, "#111111"),
                    ChoreographyTrack("duplicate", "Two", 1, "#222222"),
                )
            ),
            "duplicate_track_id",
        ),
        (
            lambda: make_project(
                regions=(
                    MusicalRegion("duplicate", "A", Fraction(0), Fraction(1)),
                    MusicalRegion("duplicate", "A", Fraction(2), Fraction(1)),
                )
            ),
            "duplicate_region_id",
        ),
        (
            lambda: make_project(
                moves=(
                    Move("duplicate", "track-1", Fraction(0), Fraction(1), "One"),
                    Move("duplicate", "track-1", Fraction(2), Fraction(1), "Two"),
                )
            ),
            "duplicate_move_id",
        ),
        (
            lambda: make_project(
                moves=(Move("move", "missing", Fraction(0), Fraction(1), "Move"),)
            ),
            "unknown_move_track",
        ),
        (
            lambda: make_project(
                moves=(Move("move", "track-1", Fraction(0), Fraction(0), "Move"),)
            ),
            "non_positive_move_duration",
        ),
        (
            lambda: make_project(
                regions=(MusicalRegion("region", "Region", Fraction(0), Fraction(-1)),)
            ),
            "non_positive_region_duration",
        ),
        (
            lambda: make_project(
                regions=(
                    MusicalRegion(
                        "region",
                        "Region",
                        cast(Fraction, 0.5),
                        Fraction(1),
                    ),
                )
            ),
            "invalid_region_timing",
        ),
    ],
)
def test_invalid_identity_references_and_fields_fail(
    project_factory: Callable[[], Project], code: str
) -> None:
    with pytest.raises(ProjectValidationError) as caught:
        validate_project(project_factory())

    assert_issue(caught.value, code)
