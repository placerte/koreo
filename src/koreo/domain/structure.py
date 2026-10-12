"""Pure top-level song-structure generation and editing."""

from dataclasses import replace
from fractions import Fraction

from koreo.domain.models import MusicalRegion, Project
from koreo.domain.validation import ProjectValidationError, validate_project

# [GH-20] Initial top-level Structure panel operations.

SECTION_PALETTE = ("#bfdbfe", "#bbf7d0", "#fde68a", "#fecaca", "#ddd6fe")
AABA_LABELS = ("Intro", "A", "A", "B", "A", "Outro")


class StructureEditError(ValueError):
    """Raised when a structure edit cannot produce a valid project."""


def generate_aaba(project: Project, duration: int = 32) -> Project:
    """Replace structure with the approved contiguous AABA starter rows."""

    if duration <= 0:
        raise StructureEditError("Section duration must be positive")
    cursor = Fraction(0)
    regions: list[MusicalRegion] = []
    for index, label in enumerate(AABA_LABELS):
        regions.append(
            MusicalRegion(
                id=f"section-{index + 1}",
                label=label,
                start=cursor,
                duration=Fraction(duration),
                color=SECTION_PALETTE[index % len(SECTION_PALETTE)],
            )
        )
        cursor += duration
    return _validated(replace(project, regions=tuple(regions)))


def append_section(project: Project, duration: int = 32) -> Project:
    """Append one contiguous top-level section."""

    if duration <= 0:
        raise StructureEditError("Section duration must be positive")
    top = [region for region in project.regions if region.parent_id is None]
    start = max((region.end for region in top), default=Fraction(0))
    index = len(top)
    region = MusicalRegion(
        id=_available_id(project, index + 1),
        label="Section",
        start=start,
        duration=Fraction(duration),
        color=SECTION_PALETTE[index % len(SECTION_PALETTE)],
    )
    return _validated(replace(project, regions=project.regions + (region,)))


def update_section(
    project: Project,
    region_id: str,
    *,
    label: str,
    duration: int,
    color: str,
) -> Project:
    """Update editable top-level section properties atomically."""

    if not label.strip():
        raise StructureEditError("Section label must not be empty")
    if duration <= 0:
        raise StructureEditError("Section duration must be positive")
    found = False
    regions: list[MusicalRegion] = []
    for region in project.regions:
        if region.id == region_id and region.parent_id is None:
            found = True
            regions.append(
                replace(
                    region,
                    label=label.strip(),
                    duration=Fraction(duration),
                    color=color,
                )
            )
        else:
            regions.append(region)
    if not found:
        raise StructureEditError(f"Unknown top-level section: {region_id}")
    return _validated(replace(project, regions=tuple(regions)))


def delete_section(project: Project, region_id: str) -> Project:
    """Delete one top-level row without shifting other beat positions."""

    matching = tuple(
        region
        for region in project.regions
        if region.id == region_id and region.parent_id is None
    )
    if not matching:
        raise StructureEditError(f"Unknown top-level section: {region_id}")
    descendants = {region_id}
    changed = True
    while changed:
        changed = False
        for region in project.regions:
            if region.parent_id in descendants and region.id not in descendants:
                descendants.add(region.id)
                changed = True
    return _validated(
        replace(
            project,
            regions=tuple(
                region for region in project.regions if region.id not in descendants
            ),
        )
    )


def _available_id(project: Project, number: int) -> str:
    existing = {region.id for region in project.regions}
    while f"section-{number}" in existing:
        number += 1
    return f"section-{number}"


def _validated(project: Project) -> Project:
    try:
        validate_project(project)
    except ProjectValidationError as error:
        raise StructureEditError(str(error)) from error
    return project
