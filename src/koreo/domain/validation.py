"""Central validation for complete Koreo project states."""

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Protocol

from koreo.domain.models import Move, MusicalRegion, Project


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One actionable project validation diagnostic."""

    code: str
    message: str
    entity_id: str | None = None


class ProjectValidationError(ValueError):
    """Raised when one or more project invariants are violated."""

    def __init__(self, issues: Iterable[ValidationIssue]) -> None:
        self.issues = tuple(issues)
        detail = "; ".join(issue.message for issue in self.issues)
        super().__init__(f"Project validation failed: {detail}")


class _TimedEntity(Protocol):
    @property
    def id(self) -> str: ...

    @property
    def start(self) -> Fraction: ...

    @property
    def duration(self) -> Fraction: ...


def validate_project(project: Project) -> None:
    """Validate ``project`` and raise one error containing all diagnostics."""

    # [GH-5] [S-M1-03] Domain invariants are enforced independently of Qt.
    issues: list[ValidationIssue] = []
    _check_project_metadata(project, issues)
    _check_duplicate_ids("track", (track.id for track in project.tracks), issues)
    _check_duplicate_ids("region", (region.id for region in project.regions), issues)
    _check_duplicate_ids("move", (move.id for move in project.moves), issues)
    _check_timing("region", project.regions, issues)
    _check_timing("move", project.moves, issues)
    _check_region_hierarchy(project, issues)
    _check_region_counts(project, issues)
    _check_region_overlaps(project, issues)
    _check_moves(project, issues)
    if issues:
        raise ProjectValidationError(issues)


def _check_project_metadata(project: Project, issues: list[ValidationIssue]) -> None:
    if not isinstance(project.count_origin, Fraction):
        issues.append(
            ValidationIssue(
                "invalid_count_origin",
                "Project count_origin must be a Fraction",
                project.id,
            )
        )
    if isinstance(project.default_count_group, bool) or not isinstance(
        project.default_count_group, int
    ):
        issues.append(
            ValidationIssue(
                "invalid_count_group",
                "Project default_count_group must be a positive integer",
                project.id,
            )
        )
    elif project.default_count_group <= 0:
        issues.append(
            ValidationIssue(
                "invalid_count_group",
                "Project default_count_group must be positive",
                project.id,
            )
        )


def _check_duplicate_ids(
    kind: str, ids: Iterable[str], issues: list[ValidationIssue]
) -> None:
    seen: set[str] = set()
    reported: set[str] = set()
    for entity_id in ids:
        if entity_id in seen and entity_id not in reported:
            issues.append(
                ValidationIssue(
                    f"duplicate_{kind}_id",
                    f"Duplicate {kind} ID: {entity_id!r}",
                    entity_id,
                )
            )
            reported.add(entity_id)
        seen.add(entity_id)


def _check_timing(
    kind: str,
    entities: Iterable[_TimedEntity],
    issues: list[ValidationIssue],
) -> None:
    for entity in entities:
        if not isinstance(entity.start, Fraction) or not isinstance(
            entity.duration, Fraction
        ):
            issues.append(
                ValidationIssue(
                    f"invalid_{kind}_timing",
                    f"{kind.title()} {entity.id!r} timing must use Fraction values",
                    entity.id,
                )
            )
            continue
        if entity.duration <= 0:
            issues.append(
                ValidationIssue(
                    f"non_positive_{kind}_duration",
                    f"{kind.title()} {entity.id!r} duration must be positive",
                    entity.id,
                )
            )


def _check_region_hierarchy(project: Project, issues: list[ValidationIssue]) -> None:
    regions_by_id = {region.id: region for region in project.regions}
    for region in project.regions:
        if region.parent_id is not None and region.parent_id not in regions_by_id:
            issues.append(
                ValidationIssue(
                    "missing_region_parent",
                    f"Region {region.id!r} references missing parent {region.parent_id!r}",
                    region.id,
                )
            )
    for region in project.regions:
        visited = {region.id}
        cursor = region
        while cursor.parent_id is not None and cursor.parent_id in regions_by_id:
            if cursor.parent_id in visited:
                issues.append(
                    ValidationIssue(
                        "region_cycle",
                        f"Region hierarchy contains a cycle involving {cursor.parent_id!r}",
                        region.id,
                    )
                )
                break
            visited.add(cursor.parent_id)
            cursor = regions_by_id[cursor.parent_id]

    for region in project.regions:
        if region.parent_id is None or region.parent_id not in regions_by_id:
            continue
        if not _has_valid_timing(region) or not _has_valid_timing(
            regions_by_id[region.parent_id]
        ):
            continue
        parent = regions_by_id[region.parent_id]
        if region.start < parent.start or region.end > parent.end:
            issues.append(
                ValidationIssue(
                    "region_outside_parent",
                    f"Region {region.id!r} extends outside parent {parent.id!r}",
                    region.id,
                )
            )


def _check_region_counts(project: Project, issues: list[ValidationIssue]) -> None:
    for region in project.regions:
        if region.count_group is not None and (
            isinstance(region.count_group, bool)
            or not isinstance(region.count_group, int)
            or region.count_group <= 0
        ):
            issues.append(
                ValidationIssue(
                    "invalid_region_count_group",
                    f"Region {region.id!r} count_group must be a positive integer",
                    region.id,
                )
            )
        if not isinstance(region.count_restart, bool):
            issues.append(
                ValidationIssue(
                    "invalid_region_count_restart",
                    f"Region {region.id!r} count_restart must be boolean",
                    region.id,
                )
            )


def _check_region_overlaps(project: Project, issues: list[ValidationIssue]) -> None:
    siblings: dict[str | None, list[MusicalRegion]] = defaultdict(list)
    for region in project.regions:
        if _has_valid_timing(region):
            siblings[region.parent_id].append(region)
    for group in siblings.values():
        _check_overlaps("region", sorted(group, key=lambda item: item.start), issues)


def _check_moves(project: Project, issues: list[ValidationIssue]) -> None:
    track_ids = {track.id for track in project.tracks}
    moves_by_track: dict[str, list[Move]] = defaultdict(list)
    for move in project.moves:
        if move.track_id not in track_ids:
            issues.append(
                ValidationIssue(
                    "unknown_move_track",
                    f"Move {move.id!r} references unknown track {move.track_id!r}",
                    move.id,
                )
            )
        if _has_valid_timing(move):
            moves_by_track[move.track_id].append(move)
    for moves in moves_by_track.values():
        _check_overlaps("move", sorted(moves, key=lambda item: item.start), issues)


def _check_overlaps(
    kind: str,
    entities: list[_TimedEntity],
    issues: list[ValidationIssue],
) -> None:
    if not entities:
        return
    previous = entities[0]
    for current in entities[1:]:
        if current.start < previous.start + previous.duration:
            issues.append(
                ValidationIssue(
                    f"overlapping_{kind}s",
                    f"{kind.title()} {current.id!r} overlaps {previous.id!r}",
                    current.id,
                )
            )
        if current.start + current.duration > previous.start + previous.duration:
            previous = current


def _has_valid_timing(entity: _TimedEntity) -> bool:
    return (
        isinstance(entity.start, Fraction)
        and isinstance(entity.duration, Fraction)
        and entity.duration > 0
    )
