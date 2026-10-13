"""Tests for top-level song-structure operations."""

from dataclasses import replace
from fractions import Fraction

import pytest

from koreo.domain.structure import (
    AABA_LABELS,
    DEFAULT_STRUCTURE_TEMPLATE,
    STRUCTURE_TEMPLATES,
    StructureEditError,
    add_block,
    append_section,
    delete_block,
    delete_section,
    delete_sections,
    generate_aaba,
    generate_structure_template,
    insert_section_after,
    insert_block_after,
    paste_sections,
    resize_block,
    section_patterns,
    update_section,
    update_block_label,
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


def test_structure_templates_expand_arrangements_and_blues_phrase_lengths() -> None:
    project = representative_project()
    arrangement = generate_structure_template(project, DEFAULT_STRUCTURE_TEMPLATE)
    sections = tuple(
        region for region in arrangement.regions if region.parent_id is None
    )
    assert tuple(region.label for region in sections) == (
        "Intro",
        "A",
        "A",
        "B",
        "A",
        "Interlude",
        "A",
        "A",
        "B",
        "A",
        "Outro",
    )

    blues = next(
        template for template in STRUCTURE_TEMPLATES if template.key == "aab-blues"
    )
    generated = generate_structure_template(project, blues)
    blues_sections = tuple(
        region for region in generated.regions if region.parent_id is None
    )
    assert [region.label for region in blues_sections] == ["A", "A", "B"]
    assert all(region.duration == 16 for region in blues_sections)


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


def test_insert_block_after_and_multi_delete_ripple_exactly() -> None:
    project = generate_aaba(representative_project())
    sections = tuple(region for region in project.regions if region.parent_id is None)
    blocks = tuple(r for r in project.regions if r.parent_id == sections[0].id)

    inserted = insert_block_after(project, blocks[0].id)
    inserted_sections = sorted(
        (r for r in inserted.regions if r.parent_id is None), key=lambda r: r.start
    )
    assert inserted_sections[0].duration == 40
    assert inserted_sections[1].start == 40

    deleted = delete_sections(inserted, (sections[1].id, sections[3].id))
    remaining = sorted(
        (r for r in deleted.regions if r.parent_id is None), key=lambda r: r.start
    )
    assert [r.label for r in remaining] == ["Intro", "A", "A", "Outro"]
    assert [r.start for r in remaining] == [0, 40, 72, 104]


def test_block_note_edit_preserves_exact_timing() -> None:
    project = generate_aaba(representative_project())
    block = next(region for region in project.regions if region.parent_id is not None)

    updated = update_block_label(project, block.id, "4: break")
    changed = next(region for region in updated.regions if region.id == block.id)

    assert changed.label == "4: break"
    assert changed.start == block.start
    assert changed.duration == block.duration


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
