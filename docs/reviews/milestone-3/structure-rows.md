# Milestone 3 structure-row review

This checkpoint implements only the approved top-level song-structure slice
from `docs/handoffs/handoff_261011_3.md`.

## Run it

```console
uv sync
uv run koreo
```

Open the **Structure** tab, leave **Section beats** at 32, and click
**Generate AABA**.

## What to assess

1. Confirm the vertical order is `Intro, A, A, B, A, Outro`.
2. Confirm each section is an independent row containing four alternating
   8-beat blocks and that adjacent rows rotate through distinct base colors.
3. Click a row. Change its label, beat duration, or hex color and click
   **Apply**. An edit that would overlap the next row is rejected rather than
   silently moving other rows.
4. Drag horizontally across an existing row to request a whole-beat resize.
5. Drag horizontally on **New section** to append a positive whole-beat row.
6. Select a row and click **Delete**. Later sections retain their exact beat
   positions, so any resulting gap remains explicit.
7. Double-click a colored row label to rename it in place. Hover the right
   edge of a row to see the resize cursor. Right-click a row to choose a
   palette color or delete it.
8. Switch to Timeline or Sheet and back. All tabs should continue rendering
   the same immutable project state.
9. Reduce the window height while the waveform is visible. The Structure tab
   should gain a vertical scrollbar, with its editor controls remaining below
   the grid instead of overlapping it.

## Deliberate boundary

This is not the complete Milestone 3 editor. Arbitrary insertion with ripple,
nested phrases, choreography conflict handling, undo/redo, and reusable custom
templates are deferred. Please assess the vertical reading model, block rhythm,
selection/editing behavior, and whether it captures the useful qualities of
the spreadsheet reference.
