"""Tests for packaged appearance defaults."""

from koreo.settings import APPEARANCE


def test_default_block_shade_factor_is_subtle() -> None:
    assert APPEARANCE.block_alternate_shade_factor == 0.8
    assert APPEARANCE.waveform_region_transparency == 0.7
    assert APPEARANCE.structure_grid_alpha == 0.12
    assert APPEARANCE.structure_primary_grid_alpha == 0.3
    assert APPEARANCE.structure_grid_label_alpha == 0.24
    assert APPEARANCE.structure_primary_grid_label_alpha == 0.6
    assert APPEARANCE.selection_moves_playhead is True
    assert APPEARANCE.show_waveform_section_labels is True
