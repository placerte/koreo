"""Tests for framework-independent count presentation."""

# [GH-16] [S-M2-06] [T-M2-08]

from fractions import Fraction

from koreo.domain.models import MusicalRegion, Project
from koreo.presentation.counting import map_counts


def _project(*regions: MusicalRegion, origin: Fraction = Fraction(0)) -> Project:
    return Project("counts", "Counts", (), regions, (), 8, origin)


def test_pickups_end_the_group_before_independent_count_origin() -> None:
    labels = map_counts(_project(origin=Fraction(2)), -2, 4)

    assert [label.local for label in labels] == ["5", "6", "7", "8", "1", "2"]
    assert [label.continuous for label in labels] == ["-3", "-2", "-1", "0", "1", "2"]


def test_region_restart_continue_and_group_override_are_deterministic() -> None:
    project = _project(
        MusicalRegion("a", "A", Fraction(0), Fraction(4)),
        MusicalRegion(
            "b", "B", Fraction(4), Fraction(4), count_group=6, count_restart=False
        ),
        MusicalRegion("c", "C", Fraction(8), Fraction(3)),
    )

    labels = map_counts(project, 0, 11)

    assert [label.local for label in labels] == [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "1",
        "2",
        "1",
        "2",
        "3",
    ]
    assert labels[4].group_size == 6
    assert not labels[4].restarted
    assert labels[8].restarted


def test_deepest_region_supplies_group_and_restart() -> None:
    project = _project(
        MusicalRegion("section", "Section", Fraction(0), Fraction(12)),
        MusicalRegion(
            "phrase",
            "Phrase",
            Fraction(3),
            Fraction(6),
            "section",
            6,
        ),
    )

    labels = map_counts(project, 0, 10)

    assert labels[3].region_id == "phrase"
    assert labels[3].local == "1"
    assert labels[3].group_size == 6
    assert labels[9].region_id == "section"
    assert labels[9].local == "7"
