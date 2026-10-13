# Koreo creation-sheet PDF execution handoff

**Status:** Approved
**Approval:** Owner clarification in chat on 2026-10-12
**Authority:** Sole execution contract for the structure creation-sheet slice

## Problem

The owner needs a printable reference while physically experimenting with
moves. The interactive Structure board is useful context but is too visually
strong and includes state that has no meaning on paper.

## Scope

Export the current top-level Structure rows and their count blocks to a PDF.
Letter landscape is the configurable default. Fit the longest section across
the writable width and paginate rows vertically. Repeat the project title,
project filename, and beat ruler on every page.

Keep page headers, ruler, and section-row labels at normal opacity. Fade only
the block playground through a configuration setting. Include block totals,
annotations, leaders, and calibrated section timestamps. Omit selection,
playhead, waveform/grid Anchor, controls, and all other interactive state.

This slice does not implement print preview, printer output, manual page
breaks, completed choreography-sheet PDF parity, Excel export, or typography
customization.

## Deliverables

- **File → Export Creation Sheet PDF…** with a standard save dialog.
- A separate, deterministic PDF renderer that consumes immutable project
  state, project title, and project filename.
- Configurable page size with `Letter` as the packaged default and a
  configurable faded playground opacity.
- Automated structural tests and a manual review procedure.
- Framework-neutral specification and decision-log updates.

## Constraints

- Domain state must remain independent of PDF and GUI/file-dialog concerns.
- Export must not mutate the project or dirty state.
- Unsaved work displays `Unsaved project` as its project-file label.
- The existing PDF/page-layout roadmap issues remain broader future work.

## Validation

- The renderer produces a valid nonempty PDF with at least one page.
- Page planning fits the longest section horizontally and splits rows without
  clipping them.
- Export receives the project name and `.kro` basename or the unsaved label.
- The Anchor and interactive overlays are absent by construction.
- Cancellation creates no file; failures are reported without clearing dirty
  state.
- `uv run pytest`, `uv run black --check .`, `uv run mypy .`, and `uv build`
  pass.
