"""Framework-independent dance-count presentation."""

from dataclasses import dataclass
from fractions import Fraction

from koreo.domain.models import MusicalRegion, Project

# [GH-16] [S-M2-06] Shared exact count notation for every view.


@dataclass(frozen=True, slots=True)
class CountLabel:
    beat: Fraction
    local: str
    continuous: str
    group_size: int
    region_id: str | None
    restarted: bool


def map_counts(project: Project, start: int, end: int) -> tuple[CountLabel, ...]:
    """Map integer beats in ``[start, end)`` to local and continuous labels."""

    if end < start:
        raise ValueError("count range end must not precede start")
    depths = _region_depths(project)
    previous_regions: tuple[MusicalRegion, ...] = ()
    counter = _floor_fraction(Fraction(start) - project.count_origin)
    labels: list[CountLabel] = []
    for beat_number in range(start, end):
        beat = Fraction(beat_number)
        active = tuple(
            sorted(
                (
                    region
                    for region in project.regions
                    if region.start <= beat < region.end
                ),
                key=lambda region: (depths[region.id], region.id),
            )
        )
        previous_ids = {region.id for region in previous_regions}
        entering = tuple(region for region in active if region.id not in previous_ids)
        restarted = any(region.count_restart for region in entering)
        if labels:
            counter = 0 if restarted else counter + 1
        elif restarted:
            counter = 0
        group = _group_size(project, active)
        relative = _floor_fraction(beat - project.count_origin)
        labels.append(
            CountLabel(
                beat=beat,
                local=str(counter % group + 1),
                continuous=str(relative + 1),
                group_size=group,
                region_id=active[-1].id if active else None,
                restarted=restarted,
            )
        )
        previous_regions = active
    return tuple(labels)


def _group_size(project: Project, active: tuple[MusicalRegion, ...]) -> int:
    for region in reversed(active):
        if region.count_group is not None:
            return region.count_group
    return project.default_count_group


def _region_depths(project: Project) -> dict[str, int]:
    by_id = {region.id: region for region in project.regions}
    depths: dict[str, int] = {}
    for region in project.regions:
        depth = 0
        parent_id = region.parent_id
        while parent_id is not None:
            depth += 1
            parent_id = by_id[parent_id].parent_id
        depths[region.id] = depth
    return depths


def _floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator
