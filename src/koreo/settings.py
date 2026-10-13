"""Small validated application settings loaded from packaged TOML defaults."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True, slots=True)
class AppearanceSettings:
    block_alternate_shade_factor: float = 0.8
    waveform_region_transparency: float = 0.7
    structure_grid_alpha: float = 0.12
    structure_primary_grid_alpha: float = 0.3
    structure_grid_label_alpha: float = 0.24
    structure_primary_grid_label_alpha: float = 0.6
    selection_moves_playhead: bool = True
    show_waveform_section_labels: bool = True


@dataclass(frozen=True, slots=True)
class CreationSheetSettings:
    page_size: str = "Letter"
    playground_opacity: float = 0.25


def load_appearance_settings() -> AppearanceSettings:
    """Load and validate the packaged appearance configuration."""

    path = Path(__file__).with_name("defaults.toml")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    factor = float(data["appearance"]["block_alternate_shade_factor"])
    transparency = float(data["appearance"]["waveform_region_transparency"])
    grid_alpha = float(data["appearance"]["structure_grid_alpha"])
    primary_grid_alpha = float(data["appearance"]["structure_primary_grid_alpha"])
    grid_label_alpha = float(data["appearance"]["structure_grid_label_alpha"])
    primary_grid_label_alpha = float(
        data["appearance"]["structure_primary_grid_label_alpha"]
    )
    selection_moves_playhead = bool(data["interaction"]["selection_moves_playhead"])
    show_waveform_section_labels = bool(
        data["interaction"]["show_waveform_section_labels"]
    )
    if not 0.0 <= factor <= 1.0:
        raise ValueError("block_alternate_shade_factor must be between 0 and 1")
    if not 0.0 <= transparency <= 1.0:
        raise ValueError("waveform_region_transparency must be between 0 and 1")
    if not 0.0 <= grid_alpha <= 1.0:
        raise ValueError("structure_grid_alpha must be between 0 and 1")
    if not 0.0 <= primary_grid_alpha <= 1.0:
        raise ValueError("structure_primary_grid_alpha must be between 0 and 1")
    if not 0.0 <= grid_label_alpha <= 1.0:
        raise ValueError("structure_grid_label_alpha must be between 0 and 1")
    if not 0.0 <= primary_grid_label_alpha <= 1.0:
        raise ValueError("structure_primary_grid_label_alpha must be between 0 and 1")
    return AppearanceSettings(
        factor,
        transparency,
        grid_alpha,
        primary_grid_alpha,
        grid_label_alpha,
        primary_grid_label_alpha,
        selection_moves_playhead,
        show_waveform_section_labels,
    )


APPEARANCE = load_appearance_settings()


def load_creation_sheet_settings() -> CreationSheetSettings:
    """Load validated printable creation-sheet defaults."""

    path = Path(__file__).with_name("defaults.toml")
    data = tomllib.loads(path.read_text(encoding="utf-8"))["creation_sheet"]
    page_size = str(data["page_size"])
    opacity = float(data["playground_opacity"])
    if page_size not in {"Letter", "A4"}:
        raise ValueError("creation_sheet.page_size must be Letter or A4")
    if not 0.0 <= opacity <= 1.0:
        raise ValueError("creation_sheet.playground_opacity must be between 0 and 1")
    return CreationSheetSettings(page_size, opacity)


CREATION_SHEET = load_creation_sheet_settings()
