# Milestone 3 structure-row review

This checkpoint implements only the approved top-level song-structure slice
from `docs/handoffs/handoff_261011_3.md`.

## Run it

```console
uv sync
uv run koreo
```

In the Structure workspace, click the main face of the template split button.
Template section lengths are encoded in each preset rather than supplied by a
separate control.

## What to assess

1. Confirm the default vertical order is
   `Intro, A, A, B, A, Interlude, A, A, B, A, Outro`.
   Open the split-button arrow and verify the grouped form alternatives. Choose
   ABAB, then AAB blues; blues should create three 16-beat sections.
2. Confirm each section is an independent row containing four alternating
   8-beat blocks and that adjacent rows rotate through distinct base colors.
3. Double-click a row label to rename it in place. Right-click the row and
   choose a color swatch. Confirm its total beats remains derived from its
   child blocks without a separate property form.
4. Drag an internal block edge to resize that child by whole beats. Confirm
   the parent total and every later row shift by the same delta.
5. Drag horizontally on **New section** to append a positive whole-beat row.
6. Right-click a row to add/delete a count block or insert a section below.
   Confirm later rows shift to preserve a contiguous song structure.
7. Double-click a colored row label to rename it in place. Hover the right
   edge of a row to see the resize cursor. Right-click a row to choose a
   palette color or delete it. Palette entries should show both a color swatch
   and its hex value.
8. Confirm Structure is the sole visible workspace; stale read-only Timeline
   and Sheet tabs should not consume space.
9. Reduce the window height while the waveform is visible. The Structure tab
   should gain a vertical scrollbar without controls overlapping the grid.
10. Set the grid Anchor on the waveform at a recognizable musical one. Then
    select the exact Structure block that starts there and click the **Align
    selected block to grid Anchor** icon. Confirm the waveform Anchor does not
    move, the Intro stays visible, a red play cursor traverses the blocks, and
    section colors appear faintly behind the waveform.
11. Enable **Selection moves playhead**. Click a section label and then a count
    block; each should seek to that exact item's start. Disable the toggle and
    confirm the same clicks only select for editing.
12. Confirm the block aligned to the waveform Anchor has a heavy green left
    edge. Ctrl-click several section rows, press Ctrl+C, select a destination
    row, and press Ctrl+V. Independent copies with the same child-block
    patterns should appear immediately after the destination in original
    order, shifting later rows forward.
13. Plain-click a row, then Shift-click a later row and confirm the complete
    range is selected. Ctrl-click another row to toggle it independently.
14. With a row selected, press Enter to insert a new section after it. With a
    block selected, press Ctrl+Enter to insert an 8-count block after it;
    Ctrl+Enter appends to the current row when only a row is selected. Delete
    removes the focused block or all selected rows. Ctrl+Z should reverse the
    latest Structure command each time. Inline editors should still use Enter
    to accept their text.
15. Drag a block edge without releasing. Its snapped beat total and all later
    block positions should preview live. Confirm discreet beat ticks appear
    inside blocks and alternating shades differ only subtly.
16. Confirm the aligned block shows both the heavy green edge and anchor glyph.
17. Double-click a count block and enter `4: break`. Confirm its count total
    remains at the top, “break” is centered, and count 4 has a stronger ruler
    tick. Save and reopen the project to confirm the annotation persists.
18. With calibration active, confirm row labels show whole-second start/end
    timestamps and waveform section backgrounds show their names at each
    section beginning. Toggle **Section labels** off and on; names should hide
    and return without changing the colored regions. The backgrounds should
    remain faint enough for the waveform to dominate.
19. Confirm **Selection moves playhead** starts enabled. Verify the beat ruler
    and aligned grid span the Structure canvas. Every tick should have its
    local dance count above it, with each 8-count boundary stronger than the
    intervening beat lines. Toggle **Continuous ruler numbers** and confirm the
    labels change from repeating 1–8 to 1 through the longest section. Labels
    should be darker than their grid lines, and no vertical grid line should
    pass through the label area.
20. While editing a section or block annotation, Space should enter whitespace,
    Enter should accept, and Escape should discard. A marked annotation such
    as `4: break` should have an elbow connector to count 4. When that count is
    beneath the text, the connector should originate at the label's
    bottom-center and have three segments and two bends. Ticks outside the text
    should use its nearest side-center anchor and one bend.
21. Confirm the waveform has a media-time ruler above and a beat ruler below,
    and that both adapt when zooming.
22. Scroll the Structure board vertically and confirm its View/Edit toolbar
    remains fixed. Ordinary wheel input should continue vertical scrolling;
    Ctrl+wheel should zoom the beat grid horizontally. Verify the matching
    zoom out, zoom in, and fit icons.
23. Confirm the Edit group exposes template generation, add section, add
    8-count block, undo, copy, paste, delete, and align-to-Anchor. The buttons
    should invoke the same commands as their existing shortcuts and contextual
    actions. Hover the controls and confirm established shortcuts appear in
    parentheses in their tooltips.

## Deliberate boundary

This is not the complete Milestone 3 editor. Deeper user-created nesting,
choreography conflict handling, undo/redo, and reusable custom templates are
deferred. Please assess the vertical reading model, block rhythm,
selection/editing behavior, and whether it captures the useful qualities of
the spreadsheet reference.
