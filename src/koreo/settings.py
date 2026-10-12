"""Small validated application settings loaded from packaged TOML defaults."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True, slots=True)
class AppearanceSettings:
    block_alternate_shade_factor: float = 0.9


def load_appearance_settings() -> AppearanceSettings:
    """Load and validate the packaged appearance configuration."""

    path = Path(__file__).with_name("defaults.toml")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    factor = float(data["appearance"]["block_alternate_shade_factor"])
    if not 0.0 <= factor <= 1.0:
        raise ValueError("block_alternate_shade_factor must be between 0 and 1")
    return AppearanceSettings(factor)


APPEARANCE = load_appearance_settings()
