"""Tests for top-level song-structure operations."""

from dataclasses import replace
from fractions import Fraction

import pytest

from koreo.domain.structure import (
    AABA_LABELS,
    StructureEditError,
    add_block,
    append_section,
    delete_block,
    delete_section,
    generate_aaba,
    insert_section_after,
    paste_sections,
    resize_block,
    section_patterns,
    update_section,
)
from koreo.fixtures import representative_project


def test_aaba_generator_creates_independent_contiguous_rows() -> None:
    project = generate_aaba(representative_project())

    sections = tuple(region for region in project.regions if region.parent_id is None)
    assert tuple(region.label for region in sections) == AABA_LABELS
    assert tuple(region.start for region in sections) == tuple(
        Fraction(index * 32) for index in range(6)
    )
    assert all(region.duration == 32 for region in sections)
    assert len({region.id for region in project.regions}) == 30
    assert sections[1].id != sections[2].id
    for section in sections:
        blocks = tuple(r for r in project.regions if r.parent_id == section.id)
        assert len(blocks) == 4
        assert all(block.duration == 8 for block in blocks)


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


def test_block_edits_derive_section_duration_and_ripple_later_rows() -> None:
    project = generate_aaba(representative_project())
    sections = tuple(region for region in project.regions if region.parent_id is None)
    intro = sections[0]
    first_a = sections[1]
    blocks = tuple(region for region in project.regions if region.parent_id == intro.id)

    resized = resize_block(project, blocks[0].id, 4)
    resized_intro = next(region for region in resized.regions if region.id == intro.id)
    resized_a = next(region for region in resized.regions if region.id == first_a.id)
    assert resized_intro.duration == 28
    assert resized_a.start == 28

    added = add_block(resized, intro.id, 8)
    assert (
        next(region for region in added.regions if region.id == intro.id).duration == 36
    )
    removed = delete_block(added, blocks[1].id)
    assert (
        next(region for region in removed.regions if region.id == intro.id).duration
        == 28
    )


def test_insert_section_shifts_later_rows() -> None:
    project = generate_aaba(representative_project())
    sections = tuple(region for region in project.regions if region.parent_id is None)

    inserted = insert_section_after(project, sections[0].id, 16)

    shifted_a = next(
        region for region in inserted.regions if region.id == sections[1].id
    )
    assert shifted_a.start == 48


def test_copy_paste_sections_preserves_order_and_independent_blocks() -> None:
    project = generate_aaba(representative_project())
    sections = tuple(region for region in project.regions if region.parent_id is None)
    patterns = section_patterns(project, (sections[1].id, sections[2].id))

    pasted = paste_sections(project, patterns, sections[2].id)
    pasted_sections = tuple(
        sorted(
            (region for region in pasted.regions if region.parent_id is None),
            key=lambda region: region.start,
        )
    )

    assert [region.label for region in pasted_sections[3:5]] == ["A", "A"]
    assert pasted_sections[3].id not in {sections[1].id, sections[2].id}
    assert pasted_sections[5].start == sections[3].start + 64


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
