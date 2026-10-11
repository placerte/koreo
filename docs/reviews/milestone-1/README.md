# Milestone 1 review evidence

Status: **approved by the owner on 2026-10-11**

Approval note: “Looks good enough for now.” The owner expects to provide
additional comments while exercising the official workflows. This approval
closes the Milestone 1 visual checkpoint; it does not freeze prototype layout
choices or pre-approve later milestone behavior.

The screenshots in this directory are captures of the actual PySide6
application rendering the same deterministic `Project` instance. They are not
design mockups.

- [`timeline.png`](timeline.png) — continuous beat-aligned Timeline view.
- [`sheet.png`](sheet.png) — wrapped 16-beat Sheet view.

Regenerate both captures with:

```console
QT_QPA_PLATFORM=offscreen uv run python scripts/capture_screenshots.py
```

## Automated evidence

Run from the repository root:

```console
uv run pytest
uv run black --check .
uv run mypy .
uv build
```

The suite covers exact fractional timing, hierarchy and overlap validation,
fixture integrity, wrap segmentation, cross-view identity/interval parity,
and offscreen rendering and tab switching.

## Manual review procedure

1. Run `uv run koreo` on a Linux desktop.
2. Confirm the Timeline shows a continuous ruler, nested musical regions, the
   unassigned gap, two colored tracks, and aligned move intervals.
3. Switch to Sheet and confirm the same sections and moves are arranged on
   wrapped count lines.
4. Confirm `Cross-line turn` has visible continuation cues on both sides of
   the line break.
5. Confirm switching tabs does not expose editing controls or change data.

## Known limitations

- The fixture is in code and the application has no project open/save flow.
- Layout uses fixed prototype dimensions and a fixed 16-beat Sheet wrap.
- There is no audio, editing, undo/redo, export, packaging, or production
  accessibility pass in Milestone 1.
- Offscreen smoke tests verify rendering and behavior, not visual quality;
  owner review remains mandatory.
