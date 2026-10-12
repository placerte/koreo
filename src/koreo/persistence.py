"""Versioned, atomic native project persistence."""

from dataclasses import dataclass
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile
from typing import Any
from zipfile import ZIP_DEFLATED, ZIP_STORED, BadZipFile, ZipFile

from koreo.audio import AudioSource
from koreo.domain.calibration import BeatCalibration
from koreo.domain.models import ChoreographyTrack, Move, MusicalRegion, Project
from koreo.domain.validation import ProjectValidationError, validate_project

FORMAT_VERSION = "0.1"
METADATA_NAME = "project.json"


class ProjectFileError(ValueError):
    """Raised when a native project cannot be saved or opened safely."""


@dataclass(frozen=True, slots=True)
class LoadedProject:
    project: Project
    tempo_bpm: Fraction
    audio_source: AudioSource | None
    waveform_peaks: tuple[tuple[float, float], ...] = ()


def save_project(
    path: Path,
    project: Project,
    tempo_bpm: Fraction,
    audio_source: AudioSource | None,
    waveform_peaks: tuple[tuple[float, float], ...] = (),
) -> None:
    """Atomically save a self-contained ``.kro`` archive."""

    validate_project(project)
    destination = path.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    audio_member = None
    if audio_source is not None:
        if not audio_source.path.is_file():
            raise ProjectFileError("The selected audio file is no longer available.")
        audio_member = f"audio/{_safe_name(audio_source.display_name)}"
    waveform_member = "waveform.json" if waveform_peaks else None
    metadata = _encode(project, tempo_bpm, audio_source, audio_member, waveform_member)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with ZipFile(temporary, "w") as archive:
            archive.writestr(
                METADATA_NAME, json.dumps(metadata, indent=2), ZIP_DEFLATED
            )
            if audio_source is not None and audio_member is not None:
                archive.write(audio_source.path, audio_member, ZIP_STORED)
            if waveform_member is not None:
                archive.writestr(
                    waveform_member,
                    json.dumps(waveform_peaks, separators=(",", ":")),
                    ZIP_DEFLATED,
                )
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        directory_fd = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except (OSError, BadZipFile) as error:
        raise ProjectFileError(f"Could not save project: {error}") from error
    finally:
        temporary.unlink(missing_ok=True)


def load_project(path: Path, extraction_root: Path) -> LoadedProject:
    """Validate a complete archive before returning replacement app state."""

    try:
        with ZipFile(path, "r") as archive:
            bad_member = archive.testzip()
            if bad_member is not None:
                raise ProjectFileError(f"Corrupt archive member: {bad_member}")
            try:
                raw = json.loads(archive.read(METADATA_NAME))
            except KeyError as error:
                raise ProjectFileError("Project metadata is missing.") from error
            loaded = _decode(raw)
            waveform_member = raw.get("waveform_member")
            if waveform_member is not None:
                if waveform_member not in archive.namelist():
                    raise ProjectFileError("Saved waveform cache is missing.")
                waveform_raw = json.loads(archive.read(waveform_member))
                if not isinstance(waveform_raw, list):
                    raise ProjectFileError("Saved waveform cache is invalid.")
                peaks = _decode_peaks(waveform_raw)
                loaded = LoadedProject(
                    loaded.project, loaded.tempo_bpm, loaded.audio_source, peaks
                )
            audio = raw.get("audio")
            if audio is not None:
                member = _text(audio, "member")
                if member not in archive.namelist() or not member.startswith("audio/"):
                    raise ProjectFileError("Embedded project audio is missing.")
                payload = archive.read(member)
                if not payload:
                    raise ProjectFileError("Embedded project audio is empty.")
                extraction_root.mkdir(parents=True, exist_ok=True)
                target = extraction_root / _safe_name(_text(audio, "display_name"))
                target.write_bytes(payload)
                source = AudioSource(
                    display_name=_text(audio, "display_name"),
                    path=target,
                    duration_seconds=_fraction(audio["duration_seconds"]),
                    sample_rate=_integer(audio, "sample_rate"),
                    channel_count=_integer(audio, "channel_count"),
                    sample_format=_text(audio, "sample_format"),
                )
                loaded = LoadedProject(
                    loaded.project,
                    loaded.tempo_bpm,
                    source,
                    loaded.waveform_peaks,
                )
            return loaded
    except (OSError, BadZipFile, json.JSONDecodeError, KeyError, TypeError) as error:
        if isinstance(error, ProjectFileError):
            raise
        raise ProjectFileError(f"Could not open project: {error}") from error


def _encode(
    project: Project,
    tempo_bpm: Fraction,
    audio: AudioSource | None,
    audio_member: str | None,
    waveform_member: str | None,
) -> dict[str, Any]:
    calibration = project.calibration
    return {
        "format_version": FORMAT_VERSION,
        "waveform_member": waveform_member,
        "tempo_bpm": _encode_fraction(tempo_bpm),
        "project": {
            "id": project.id,
            "name": project.name,
            "default_count_group": project.default_count_group,
            "count_origin": _encode_fraction(project.count_origin),
            "calibration": (
                None
                if calibration is None
                else {
                    "bpm": _encode_fraction(calibration.bpm),
                    "anchor_seconds": _encode_fraction(calibration.anchor_seconds),
                    "anchor_beat": _encode_fraction(calibration.anchor_beat),
                    "calibration_beat": _encode_optional(calibration.calibration_beat),
                    "calibration_seconds": _encode_optional(
                        calibration.calibration_seconds
                    ),
                }
            ),
            "regions": [
                {
                    "id": item.id,
                    "label": item.label,
                    "start": _encode_fraction(item.start),
                    "duration": _encode_fraction(item.duration),
                    "parent_id": item.parent_id,
                    "count_group": item.count_group,
                    "count_restart": item.count_restart,
                    "color": item.color,
                }
                for item in project.regions
            ],
            "tracks": [
                {
                    "id": item.id,
                    "name": item.name,
                    "display_order": item.display_order,
                    "color": item.color,
                }
                for item in project.tracks
            ],
            "moves": [
                {
                    "id": item.id,
                    "track_id": item.track_id,
                    "start": _encode_fraction(item.start),
                    "duration": _encode_fraction(item.duration),
                    "label": item.label,
                    "notes": item.notes,
                }
                for item in project.moves
            ],
        },
        "audio": (
            None
            if audio is None
            else {
                "member": audio_member,
                "display_name": audio.display_name,
                "duration_seconds": _encode_fraction(audio.duration_seconds),
                "sample_rate": audio.sample_rate,
                "channel_count": audio.channel_count,
                "sample_format": audio.sample_format,
            }
        ),
    }


def _decode(raw: Any) -> LoadedProject:
    if not isinstance(raw, dict):
        raise ProjectFileError("Project metadata must be an object.")
    version = raw.get("format_version")
    if version != FORMAT_VERSION:
        raise ProjectFileError(
            f"Unsupported project format {version!r}; this build supports {FORMAT_VERSION}."
        )
    data = raw["project"]
    calibration_data = data.get("calibration")
    calibration = None
    if calibration_data is not None:
        calibration = BeatCalibration(
            bpm=_fraction(calibration_data["bpm"]),
            anchor_seconds=_fraction(calibration_data["anchor_seconds"]),
            anchor_beat=_fraction(calibration_data["anchor_beat"]),
            calibration_beat=_optional_fraction(calibration_data["calibration_beat"]),
            calibration_seconds=_optional_fraction(
                calibration_data["calibration_seconds"]
            ),
        )
    project = Project(
        id=_text(data, "id"),
        name=_text(data, "name"),
        tracks=tuple(ChoreographyTrack(**item) for item in data["tracks"]),
        regions=tuple(
            MusicalRegion(
                id=_text(item, "id"),
                label=_text(item, "label"),
                start=_fraction(item["start"]),
                duration=_fraction(item["duration"]),
                parent_id=item.get("parent_id"),
                count_group=item.get("count_group"),
                count_restart=item.get("count_restart", True),
                color=item.get("color"),
            )
            for item in data["regions"]
        ),
        moves=tuple(
            Move(
                id=_text(item, "id"),
                track_id=_text(item, "track_id"),
                start=_fraction(item["start"]),
                duration=_fraction(item["duration"]),
                label=_text(item, "label"),
                notes=item.get("notes"),
            )
            for item in data["moves"]
        ),
        default_count_group=_integer(data, "default_count_group"),
        count_origin=_fraction(data["count_origin"]),
        calibration=calibration,
    )
    try:
        validate_project(project)
    except ProjectValidationError as error:
        raise ProjectFileError(str(error)) from error
    return LoadedProject(project, _fraction(raw["tempo_bpm"]), None)


def _encode_fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _encode_optional(value: Fraction | None) -> dict[str, int] | None:
    return None if value is None else _encode_fraction(value)


def _fraction(value: Any) -> Fraction:
    if not isinstance(value, dict):
        raise ProjectFileError("Exact number must contain numerator and denominator.")
    return Fraction(_integer(value, "numerator"), _integer(value, "denominator"))


def _optional_fraction(value: Any) -> Fraction | None:
    return None if value is None else _fraction(value)


def _text(data: Any, key: str) -> str:
    value = data[key]
    if not isinstance(value, str):
        raise ProjectFileError(f"{key} must be text.")
    return value


def _integer(data: Any, key: str) -> int:
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProjectFileError(f"{key} must be an integer.")
    return value


def _safe_name(name: str) -> str:
    safe = Path(name).name
    if not safe or safe in {".", ".."}:
        raise ProjectFileError("Audio filename is invalid.")
    return safe


def _decode_peaks(value: list[Any]) -> tuple[tuple[float, float], ...]:
    peaks: list[tuple[float, float]] = []
    for pair in value:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ProjectFileError("Saved waveform cache is invalid.")
        try:
            minimum, maximum = float(pair[0]), float(pair[1])
        except (TypeError, ValueError) as error:
            raise ProjectFileError("Saved waveform cache is invalid.") from error
        if not -1.0 <= minimum <= maximum <= 1.0:
            raise ProjectFileError("Saved waveform cache is invalid.")
        peaks.append((minimum, maximum))
    return tuple(peaks)
