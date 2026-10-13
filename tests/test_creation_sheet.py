"""Creation-sheet PDF planning and export tests."""

from pathlib import Path

from pytestqt.qtbot import QtBot

from koreo.domain.structure import generate_aaba
from koreo.export.creation_sheet import export_creation_sheet_pdf, plan_creation_sheet
from koreo.fixtures import representative_project
from koreo.settings import CREATION_SHEET


def test_creation_sheet_defaults_to_letter_and_faded_playground() -> None:
    assert CREATION_SHEET.page_size == "Letter"
    assert CREATION_SHEET.playground_opacity == 0.25


def test_page_plan_fits_longest_section_and_paginates_rows() -> None:
    project = generate_aaba(representative_project())

    plan = plan_creation_sheet(project, printable_height=216)

    assert plan.maximum_beats == 32
    assert plan.rows_per_page == 2
    assert plan.page_count == 3


def test_creation_sheet_exports_nonempty_pdf(qtbot: QtBot, tmp_path: Path) -> None:
    del qtbot
    project = generate_aaba(representative_project())
    target = tmp_path / "practice.pdf"

    plan = export_creation_sheet_pdf(
        project,
        target,
        project_filename="practice.kro",
    )

    assert plan.page_count >= 1
    assert target.read_bytes().startswith(b"%PDF")
    assert target.stat().st_size > 1_000
