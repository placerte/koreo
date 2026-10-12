"""Pure hierarchical song-structure generation and editing."""

from dataclasses import replace
from fractions import Fraction

from koreo.domain.models import MusicalRegion, Project
from koreo.domain.validation import ProjectValidationError, validate_project

SECTION_PALETTE = ("#bfdbfe", "#bbf7d0", "#fde68a", "#fecaca", "#ddd6fe")
AABA_LABELS = ("Intro", "A", "A", "B", "A", "Outro")


class StructureEditError(ValueError):
    """Raised when a structure edit cannot produce a valid project."""


def generate_aaba(project: Project, duration: int = 32) -> Project:
    """Replace structure with AABA rows prepopulated by count-block children."""

    if duration <= 0:
        raise StructureEditError("Section duration must be positive")
    cursor = Fraction(0)
    regions: list[MusicalRegion] = []
    for index, label in enumerate(AABA_LABELS):
        section_id = f"section-{index + 1}"
        color = SECTION_PALETTE[index % len(SECTION_PALETTE)]
        section = MusicalRegion(
            section_id, label, cursor, Fraction(duration), color=color
        )
        regions.append(section)
        regions.extend(_new_blocks(section, duration, project, regions))
        cursor += duration
    return _validated(replace(project, regions=tuple(regions)))


def append_section(project: Project, duration: int = 32) -> Project:
    """Append one contiguous top-level section with count-block children."""

    sections = _sections(project)
    return insert_section_after(
        project, sections[-1].id if sections else None, duration
    )


def insert_section_after(
    project: Project, after_id: str | None, duration: int = 32
) -> Project:
    """Insert a section and shift all later structure forward exactly."""

    if duration <= 0:
        raise StructureEditError("Section duration must be positive")
    sections = _sections(project)
    if after_id is None:
        start = sections[0].start if sections else Fraction(0)
        index = 0
    else:
        after = _section(project, after_id)
        start = after.end
        index = sections.index(after) + 1
    shifted = _shift_from(project.regions, start, Fraction(duration))
    section_id = _available_id(project, index + 1)
    section = MusicalRegion(
        section_id,
        "Section",
        start,
        Fraction(duration),
        color=SECTION_PALETTE[index % len(SECTION_PALETTE)],
    )
    blocks = _new_blocks(section, duration, project, list(shifted) + [section])
    return _validated(replace(project, regions=shifted + (section,) + tuple(blocks)))


def add_block(project: Project, section_id: str, duration: int = 8) -> Project:
    """Append a block and extend its parent, shifting later sections."""

    if duration <= 0:
        raise StructureEditError("Block duration must be positive")
    section = _section(project, section_id)
    shifted = _shift_from(project.regions, section.end, Fraction(duration))
    shifted = tuple(
        (
            replace(region, duration=region.duration + duration)
            if region.id == section_id
            else region
        )
        for region in shifted
    )
    block_id = _available_id(project, 1, f"{section_id}-block-")
    block = MusicalRegion(
        block_id,
        "8 count",
        section.end,
        Fraction(duration),
        parent_id=section_id,
        count_restart=False,
    )
    return _validated(replace(project, regions=shifted + (block,)))


def resize_block(project: Project, block_id: str, duration: int) -> Project:
    """Resize one block and ripple following boundaries."""

    if duration <= 0:
        raise StructureEditError("Block duration must be positive")
    block = _block(project, block_id)
    parent = _section(project, block.parent_id or "")
    delta = Fraction(duration) - block.duration
    if not delta:
        return project
    regions: list[MusicalRegion] = []
    for region in project.regions:
        if region.id == block.id:
            regions.append(replace(region, duration=Fraction(duration)))
        elif region.id == parent.id:
            regions.append(replace(region, duration=region.duration + delta))
        elif region.parent_id == parent.id and region.start >= block.end:
            regions.append(replace(region, start=region.start + delta))
        elif region.parent_id is None and region.start >= parent.end:
            regions.append(replace(region, start=region.start + delta))
        elif _belongs_to_later_section(project, region, parent.end):
            regions.append(replace(region, start=region.start + delta))
        else:
            regions.append(region)
    return _validated(replace(project, regions=tuple(regions)))


def delete_block(project: Project, block_id: str) -> Project:
    """Delete one block and contract its parent and later structure."""

    block = _block(project, block_id)
    parent = _section(project, block.parent_id or "")
    if len(_blocks(project, parent.id)) == 1:
        raise StructureEditError("A section must retain at least one block")
    regions: list[MusicalRegion] = []
    for region in project.regions:
        if region.id == block.id:
            continue
        if region.id == parent.id:
            regions.append(replace(region, duration=region.duration - block.duration))
        elif region.parent_id == parent.id and region.start >= block.end:
            regions.append(replace(region, start=region.start - block.duration))
        elif region.parent_id is None and region.start >= parent.end:
            regions.append(replace(region, start=region.start - block.duration))
        elif _belongs_to_later_section(project, region, parent.end):
            regions.append(replace(region, start=region.start - block.duration))
        else:
            regions.append(region)
    return _validated(replace(project, regions=tuple(regions)))


def update_section(
    project: Project, region_id: str, *, label: str, duration: int, color: str
) -> Project:
    """Update a section; duration changes resize its final child block."""

    if not label.strip():
        raise StructureEditError("Section label must not be empty")
    section = _section(project, region_id)
    delta = Fraction(duration) - section.duration
    updated = project
    if delta:
        final = _blocks(project, region_id)[-1]
        new_duration = final.duration + delta
        if new_duration <= 0:
            raise StructureEditError("Resize would remove the final count block")
        updated = resize_block(project, final.id, int(new_duration))
    regions = tuple(
        (
            replace(region, label=label.strip(), color=color)
            if region.id == region_id
            else region
        )
        for region in updated.regions
    )
    return _validated(replace(updated, regions=regions))


def delete_section(project: Project, region_id: str) -> Project:
    """Delete a section and shift later sections backward."""

    section = _section(project, region_id)
    removed = {section.id} | {block.id for block in _blocks(project, section.id)}
    kept = tuple(region for region in project.regions if region.id not in removed)
    return _validated(
        replace(project, regions=_shift_from(kept, section.end, -section.duration))
    )


def rebase_structure(project: Project, anchor_beat: Fraction) -> Project:
    """Move ``anchor_beat`` to zero while preserving every interval."""

    regions = tuple(
        replace(region, start=region.start - anchor_beat) for region in project.regions
    )
    return _validated(replace(project, regions=regions))


def _new_blocks(
    section: MusicalRegion,
    duration: int,
    project: Project,
    pending: list[MusicalRegion],
) -> list[MusicalRegion]:
    blocks: list[MusicalRegion] = []
    existing = {r.id for r in project.regions} | {r.id for r in pending}
    cursor = section.start
    remaining = duration
    number = 1
    while remaining:
        length = min(8, remaining)
        block_id = f"{section.id}-block-{number}"
        while block_id in existing:
            number += 1
            block_id = f"{section.id}-block-{number}"
        blocks.append(
            MusicalRegion(
                block_id,
                "8 count",
                cursor,
                Fraction(length),
                parent_id=section.id,
                count_restart=False,
            )
        )
        existing.add(block_id)
        cursor += length
        remaining -= length
        number += 1
    return blocks


def _sections(project: Project) -> list[MusicalRegion]:
    return sorted(
        (r for r in project.regions if r.parent_id is None),
        key=lambda r: (r.start, r.id),
    )


def _blocks(project: Project, section_id: str) -> list[MusicalRegion]:
    blocks = sorted(
        (r for r in project.regions if r.parent_id == section_id),
        key=lambda r: (r.start, r.id),
    )
    if not blocks:
        raise StructureEditError(f"Section has no count blocks: {section_id}")
    return blocks


def _section(project: Project, section_id: str) -> MusicalRegion:
    try:
        return next(
            r for r in project.regions if r.id == section_id and r.parent_id is None
        )
    except StopIteration as error:
        raise StructureEditError(f"Unknown top-level section: {section_id}") from error


def _block(project: Project, block_id: str) -> MusicalRegion:
    try:
        return next(
            r for r in project.regions if r.id == block_id and r.parent_id is not None
        )
    except StopIteration as error:
        raise StructureEditError(f"Unknown count block: {block_id}") from error


def _shift_from(
    regions: tuple[MusicalRegion, ...], boundary: Fraction, delta: Fraction
) -> tuple[MusicalRegion, ...]:
    return tuple(
        (
            replace(region, start=region.start + delta)
            if region.start >= boundary
            else region
        )
        for region in regions
    )


def _belongs_to_later_section(
    project: Project, region: MusicalRegion, boundary: Fraction
) -> bool:
    if region.parent_id is None:
        return False
    parent = next((r for r in project.regions if r.id == region.parent_id), None)
    return parent is not None and parent.start >= boundary


def _available_id(project: Project, number: int, prefix: str = "section-") -> str:
    existing = {region.id for region in project.regions}
    while f"{prefix}{number}" in existing:
        number += 1
    return f"{prefix}{number}"


def _validated(project: Project) -> Project:
    try:
        validate_project(project)
    except ProjectValidationError as error:
        raise StructureEditError(str(error)) from error
    return project
