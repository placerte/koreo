"""Tests for packaged appearance defaults."""

from koreo.settings import APPEARANCE


def test_default_block_shade_factor_is_subtle() -> None:
    assert APPEARANCE.block_alternate_shade_factor == 0.9
