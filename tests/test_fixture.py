"""Tests for the representative Milestone 1 fixture."""

# [GH-6] [T-06]

from fractions import Fraction

from koreo.domain.validation import validate_project
from koreo.fixtures import representative_project, starter_project


def test_representative_fixture_is_valid_and_covers_required_cases() -> None:
    project = representative_project()
    validate_project(project)

    top_labels = [
        region.label for region in project.regions if region.parent_id is None
    ]
    assert len(top_labels) >= 3
    assert top_labels.count("A") == 2
    assert any(region.parent_id is not None for region in project.regions)
    assert len(project.tracks) == 1
    assert project.tracks[0].name == "Choreography"
    assert len({track.color for track in project.tracks}) == len(project.tracks)
    assert any(move.start.denominator > 1 for move in project.moves)
    assert any(region.count_group == 6 for region in project.regions)

    assert any(move.start < Fraction(22) < move.end for move in project.moves)
    assert any(move.start < Fraction(32) < move.end for move in project.moves)


def test_representative_fixture_contains_visible_unassigned_gap() -> None:
    project = representative_project()
    top_regions = [region for region in project.regions if region.parent_id is None]

    assert not any(region.start <= Fraction(23) < region.end for region in top_regions)


def test_starter_project_has_no_programmed_moves() -> None:
    project = starter_project()

    assert project.moves == ()
    assert len(project.tracks) == 1
