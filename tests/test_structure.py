"""Tests for top-level song-structure operations."""

from dataclasses import replace
from fractions import Fraction

import pytest

from koreo.domain.structure import (
    AABA_LABELS,
    StructureEditError,
    append_section,
    delete_section,
    generate_aaba,
    update_section,
)
from koreo.fixtures import representative_project


def test_aaba_generator_creates_independent_contiguous_rows() -> None:
    project = generate_aaba(representative_project())

    assert tuple(region.label for region in project.regions) == AABA_LABELS
    assert tuple(region.start for region in project.regions) == tuple(
        Fraction(index * 32) for index in range(6)
    )
    assert all(region.duration == 32 for region in project.regions)
    assert len({region.id for region in project.regions}) == 6
    assert project.regions[1].id != project.regions[2].id


def test_append_update_and_delete_preserve_unrelated_state() -> None:
    original = replace(representative_project(), regions=())
    appended = append_section(original, 16)
    updated = update_section(
        appended,
        appended.regions[0].id,
        label="Break",
        duration=12,
        color="#123456",
    )
    deleted = delete_section(updated, updated.regions[0].id)

    assert updated.regions[0].label == "Break"
    assert updated.regions[0].duration == 12
    assert updated.regions[0].color == "#123456"
    assert deleted.regions == ()
    assert deleted.moves is original.moves
    assert deleted.tracks is original.tracks


@pytest.mark.parametrize("duration", [0, -1])
def test_non_positive_structure_duration_fails_atomically(duration: int) -> None:
    project = representative_project()
    with pytest.raises(StructureEditError, match="positive"):
        generate_aaba(project, duration)
    assert project == representative_project()


def test_unknown_section_edits_fail_atomically() -> None:
    project = representative_project()

    with pytest.raises(StructureEditError, match="Unknown top-level section"):
        update_section(
            project,
            "missing",
            label="Missing",
            duration=8,
            color="#123456",
        )
    with pytest.raises(StructureEditError, match="Unknown top-level section"):
        delete_section(project, "missing")

    assert project == representative_project()
