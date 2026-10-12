# Koreo V1 framework-neutral UI behavior

This specification preserves approved interaction behavior independently of
the current GUI toolkit. A future rewrite may change widgets, styling, and
layout, but should retain these observable rules unless the owner explicitly
revises them.

## Interaction principles

- Musical beat positions are authoritative; display notation and media-time
  calibration must not rewrite regions or choreography.
- Temporary modal work is transactional: Cancel or window close discards it
  and stops resources owned by that modal.
- Dynamic labels reserve stable geometry so their contents never move adjacent
  controls. `current / duration` time text is fixed-width and right-aligned.
- Long-running work provides immediate visible activity feedback and never
  requires playback to begin.

## Song selection and tempo

- Song selection belongs to the main project UI, not the Tap BPM modal.
- A new song becomes active only after its decoder yields real audio. Failure
  preserves the previously valid song.
- Manual BPM entry belongs to the main UI.
- Tap BPM opens a focused modal for tapping only; it contains no numeric BPM
  override.
- The selected song starts automatically when Tap BPM appears. The modal is
  immediately ready for Space taps.
- Two taps produce the first estimate; later taps refine it from the first to
  last tap. Three seconds of inactivity starts a new session. Key auto-repeat
  is ignored.
- Accept applies the estimate. Cancel or close discards it. Every exit stops
  modal playback.

## Main playback and keyboard ownership

- Main playback provides Play/Pause, Stop, seek, position, and duration.
- Stop returns to media start; Pause retains position.
- In the active main window, Space always toggles Play/Pause regardless of
  focused child control and never activates that control. Auto-repeat is
  ignored.
- A modal may explicitly own Space. Tap BPM owns it for taps while open.

## Waveform

- Waveform extraction starts immediately after successful song selection and
  is independent of playback.
- While extracting, show an indeterminate `Processing song…` state.
- The waveform remains dynamically rendered from approximately 10 ms min/max
  peak windows rather than a pre-scaled image.
- A faint constant-tempo beat grid appears behind the waveform. Before a grid
  Anchor exists it starts at media time zero; setting the Anchor shifts it
  immediately to that media position.
- A plain left click seeks to the clicked media time.
- A left drag pans after crossing the platform drag threshold. A completed pan
  must not also seek on release. Middle-button panning is not used.
- Wheel zoom is centered under the pointer. Zoom in, zoom out, and fit controls
  are also available.
- Waveform, beat grid, Anchor, structure backgrounds, and playhead always use
  the same time transform.
- Follow mode holds the playhead near 35% of the viewport while zoomed and
  moves the waveform beneath it. Wheel zoom or drag-pan suspends Follow; an
  explicit control resumes it.

## Calibration staging

- Anchor and optional later-point refinement belong in the waveform-backed
  song-structure workflow, not the Tap BPM modal.
- The waveform may set a provisional grid Anchor. In Structure, anchoring a
  selected section start at the playhead also establishes the structural
  origin and is the preferred final workflow.

## Song structure panel

- The song reads vertically with one sequential top-level section per row.
- Rows display local beat grids but retain exact absolute song-beat intervals.
- A normal AABA section defaults to 32 beats displayed as four 8-count blocks.
- The first AABA generator creates `Intro, A, A, B, A, Outro`; all rows are
  independent and contiguous, and defaults remain editable.
- Adjacent rows rotate through a predefined accessible palette. Consecutive
  8-count blocks alternate the row base color and a lighter derived shade.
- A persistent blank row supports drag-to-create. Selection exposes exact
  label, duration, and color editing plus deletion.
- Row labels use the section color and enter an in-place text editor on double
  click. Hovering the section endpoint shows a horizontal-resize cursor.
- Right-clicking a section selects it and exposes palette colors and deletion
  in a contextual menu.
- Palette choices show a rendered color swatch before the precise hex value.
- An explicit **Selection moves playhead** toggle controls whether clicking a
  section row/label or count block seeks to that exact item's start. With the
  toggle off, selection changes editing focus only.
- The block whose start is aligned to the waveform Anchor has a distinct,
  heavier Anchor-colored left border.
- A plain click selects one section; Ctrl-click toggles sections into or out
  of a multi-selection. Shift-click fills the contiguous range from the
  selection anchor. Ctrl+C snapshots selected sections and all their child
  blocks. Ctrl+V inserts independent copies after the latest selected row,
  preserves copied song order, and ripples later structure.
- Ctrl+Z restores the project state before the latest Structure command.
  Delete removes the selected block when one has focus, otherwise all selected
  section rows. Enter inserts an 8-count block after the selected block, or at
  the end of the current row when only a row is selected. Text-entry controls
  retain their normal editing interpretation of these keys.
- Each visible count block is a real child region. The section total is the
  sum of its children; adding, deleting, or resizing a child ripples all later
  sections by the exact duration delta.
- Right-click supports inserting a new top-level section below the selected
  row, shifting every later row forward.
- The waveform is the sole source of truth for the grid **Anchor** media time.
  Selecting an exact block on the Structure board and aligning it to the
  Anchor rebases only structure beat coordinates; it never moves the waveform
  Anchor. Earlier structure remains available at negative backend beats, while
  dancer-facing local counts continue as ordinary 1–8 counts.
- When calibrated, a play cursor traverses the structure blocks and section
  colors form faint aligned backgrounds behind the waveform.
- The complete Structure workspace scrolls vertically when waveform or window
  height leaves too little room; controls must never overlap the section grid.
- Variable lengths and incomplete blocks are valid. Visual centering of short
  rows carries no timing meaning.
- Reusable named template libraries and palette themes are future work.

## Count presentation

- Local dance counts are primary. Continuous beat numbers are optional
  secondary labels controlled once for both Timeline and Sheet.
- Count origin is independent of the audio anchor.
- Counts before the origin show the ending counts of the preceding group.
- The project supplies a positive default group size; the deepest active region
  with an override supplies the local group size.
- Entering a region restarts at `1` by default. A region marked Continue keeps
  the preceding sequence. Leaving a nested region does not count as re-entering
  its parent.
- Partial final groups retain their true duration.
- Count display changes never alter beats, audio, regions, or choreography.

## Portability acceptance

For any future GUI framework, replay the behavioral review documents under
`docs/reviews/`. Equivalent behavior matters; matching current widget classes,
pixel styling, or internal event APIs does not.
