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
3. Click a row. Change its label or hex color and click **Apply**. Total beats
   is read-only because it is derived from that row's child blocks.
4. Drag an internal block edge to resize that child by whole beats. Confirm
   the parent total and every later row shift by the same delta.
5. Drag horizontally on **New section** to append a positive whole-beat row.
6. Right-click a row to add/delete a count block or insert a section below.
   Confirm later rows shift to preserve a contiguous song structure.
7. Double-click a colored row label to rename it in place. Hover the right
   edge of a row to see the resize cursor. Right-click a row to choose a
   palette color or delete it.
8. Switch to Timeline or Sheet and back. All tabs should continue rendering
   the same immutable project state.
9. Reduce the window height while the waveform is visible. The Structure tab
   should gain a vertical scrollbar, with its editor controls remaining below
   the grid instead of overlapping it.
10. Set the grid Anchor on the waveform at a recognizable musical one. Then
    select the exact Structure block that starts there and click **Align
    selected block to grid Anchor**. Confirm the waveform Anchor does not
    move, the Intro stays visible, a red play cursor traverses the blocks, and
    section colors appear faintly behind the waveform.

## Deliberate boundary

This is not the complete Milestone 3 editor. Deeper user-created nesting,
choreography conflict handling, undo/redo, and reusable custom templates are
deferred. Please assess the vertical reading model, block rhythm,
selection/editing behavior, and whether it captures the useful qualities of
the spreadsheet reference.
