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

- The main project header exposes an editable project name. Accepting a
  non-empty changed value updates authoritative project state, marks it dirty,
  persists through save/load, and supplies the creation-sheet title. Empty
  input restores the current name. It uses a wider, bold title-sized treatment
  so the project identity is visually distinct from ordinary form fields.
- Song selection belongs to the main project UI, not the Tap BPM modal.
- Song selection, filename, numeric BPM input, Tap BPM, waveform display
  toggles, zoom, Follow, and Anchor actions share one waveform toolbar below
  the waveform. Separator-bounded groups appear in this order: song file and
  processing state; view/display controls; BPM, Tap BPM, Anchor action and its
  compact timestamp; Advanced options. Successful waveform preparation needs
  no redundant “ready” suffix because the waveform and processing indicator
  communicate state.
- Manual BPM uses a compact numeric spin box, accepts positive decimal numbers
  only, and displays two decimal places even when tapping produces more precise
  internal measurements. Its arrow controls step by `0.5` BPM. Tap BPM and audio selection are icon buttons
  (`mouse-pointer-click` and `file-music`).
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
- Structure is the sole visible editing workspace in the current prototype;
  the stale read-only Timeline and Sheet tabs are not presented.
- Count origin and default count-group size are infrequently changed advanced
  song settings. They live in a settings dialog opened by a `flask-conical`
  icon alongside the waveform tools and use numeric controls.
- Frequent actions with familiar visual metaphors use compact icon-only
  buttons: choose audio, Play/Pause, Stop, waveform zoom in/out/fit, Follow, set waveform
  Anchor, align a Structure block to the Anchor, and structure-template
  generation. Every icon control has a descriptive tooltip and accessible
  name. Lucide is Koreo's exclusive icon library; use its official icon names,
  outline SVGs displayed at 20 px with a 2 px stroke, rendered in the current palette
  foreground. Verify names against the installed/vendored catalog rather than
  inventing them. Icons are
  selected by semantic role through one replaceable provider so artwork and
  colors are not embedded in individual widgets.
- Stop returns to media start; Pause retains position.
- In the active main window, Space toggles Play/Pause unless a text-entry
  control owns focus. In text entry it inserts an ordinary space and must not
  affect playback. Auto-repeat is ignored.
- Inline text editors accept and close on Enter. Escape closes them and
  discards the current edit. Losing focus accepts the edit.
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
- The displayed seek position updates synchronously even when playback is
  stopped. Setting the grid Anchor immediately after a click uses that exact
  displayed position and never requires briefly starting playback.
- A left drag pans after crossing the platform drag threshold. A completed pan
  must not also seek on release. Middle-button panning is not used.
- Wheel zoom is centered under the pointer. Zoom in, zoom out, and fit controls
  are also available.
- Waveform, beat grid, Anchor, structure backgrounds, and playhead always use
  the same time transform.
- A media-time ruler is shown above the waveform and a calibrated beat ruler
  below it. Their tick density adapts to the current zoom.
- Full-song rendering reduces visible peak buckets to approximately one bucket
  per horizontal pixel while preserving each bucket's extrema. Playhead motion
  must not repaint tens of thousands of redundant points.
- Extracted waveform peaks are an optional cache in native project files.
  Reopening uses a valid cache immediately; absent caches recompute normally.
- Follow mode holds the playhead near 35% of the viewport while zoomed and
  moves the waveform beneath it. Wheel zoom or drag-pan suspends Follow; an
  explicit control resumes it.
- Waveform Section labels is an icon toggle rather than a checkbox. The Anchor
  glyph is painted after the rulers in the lower waveform area so it remains
  legible; the waveform Anchor action uses Lucide's `anchor` icon.

## Calibration staging

- Anchor belongs in the waveform-backed song-structure workflow, not the Tap
  BPM modal. Later-point tempo refinement is deferred and is not exposed in
  the current prototype UI.
- The waveform may set a provisional grid Anchor. In Structure, anchoring a
  selected section start at the playhead also establishes the structural
  origin and is the preferred final workflow.

## Song structure panel

- Call the editable block workspace the **Structure board**. Its toolbar stays
  fixed above the scrollable board rather than disappearing with row content.
- The toolbar has separate View and Edit groups. View contains horizontal zoom
  out/in/fit, selection-to-playhead, and ruler-number mode. Edit exposes
  template generation, add section, add 8-count block, undo, copy, paste,
  delete, and align-to-Anchor using Lucide icons with accessible tooltips.
- An ordinary mouse wheel retains vertical scrolling. Ctrl+wheel changes the
  Structure board's horizontal beat scale; it does not alter beat timing or
  row height.
- The song reads vertically with one sequential top-level section per row.
- Rows display local beat grids but retain exact absolute song-beat intervals.
- A normal AABA section defaults to 32 beats displayed as four 8-count blocks.
- Structure generation uses a true split button. Its main face runs the
  current/default template; its arrow opens grouped full-song arrangements and
  phrase/form templates. The default expands to
  `Intro, A, A, B, A, Interlude, A, A, B, A, Outro`.
- Phrase/form choices include AABA, ABAB, ABAC, ABBA, AAAA, AAB blues, AB,
  ABC, and ABACA rondo. Each preset owns its section length: AAB blues uses
  three 16-beat/four-bar phrases and the other initial presets use 32 beats.
  There is no separate Section beats control. Custom structure continues
  through drawing and adding sections rather than a fake generator.
- Generated rows are independent and contiguous, and defaults remain editable.
- Adjacent rows rotate through a predefined accessible palette. Consecutive
  8-count blocks alternate the row base color and a lighter derived shade.
- Section colors are treated as semantic theme accent roles. The current
  palette is only the default theme's accent set, not permanently fixed
  product colors.
- A persistent blank row supports drag-to-create. Section label editing is
  inline; color and deletion are contextual actions. Section duration remains
  derived from count blocks. There is no duplicated selected-row property
  strip.
- Row labels use the section color and enter an in-place text editor on double
  click. Hovering the section endpoint shows a horizontal-resize cursor.
- Right-clicking a section selects it and exposes palette colors and deletion
  in a contextual menu.
- Palette choices show a rendered color swatch before the precise hex value.
- An explicit **Selection moves playhead** toggle controls whether clicking a
  section row/label or count block seeks to that exact item's start. With the
  toggle off, selection changes editing focus only. It defaults on through the
  `selection_moves_playhead` configuration setting.
- Selection-to-playhead and continuous-ruler-number choices are compact icon
  toggles (`mouse-pointer-2` and `list-ordered`) rather than text checkboxes.
- The block whose start is aligned to the waveform Anchor has a distinct,
  heavier Anchor-colored left border and an anchor glyph. The waveform uses
  the same glyph instead of spelling out “Anchor.”
- A plain click selects one section; Ctrl-click toggles sections into or out
  of a multi-selection. Shift-click fills the contiguous range from the
  selection anchor. Ctrl+C snapshots selected sections and all their child
  blocks. Ctrl+V inserts independent copies after the latest selected row,
  preserves copied song order, and ripples later structure.
- Ctrl+Z restores the project state before the latest Structure command.
  Delete removes the selected block when one has focus, otherwise all selected
  section rows. Enter inserts a new section after the current selection.
  Ctrl+Enter inserts an 8-count block after the selected block, or at the end
  of the current row when only a row is selected. Text-entry controls retain
  their normal editing interpretation of these keys.
- Toolbar tooltips include established keyboard and pointer shortcuts in
  parentheses, including the Structure zoom, creation, clipboard, undo, and
  deletion commands.
- Drag-resizing a count-block boundary previews the snapped duration and
  following block positions continuously before mouse release.
- Count blocks show discreet one-beat ruler ticks along their lower edge.
- The block canvas has a beat ruler across its top and aligned vertical grid
  lines through all rows. Every beat is labeled above its tick using the local
  dance-count cycle by default. A toggle switches to continuous numbering from
  1 through the longest section. Count-group starts are stronger than
  intervening beats. Major and minor label opacities are independently
  configurable and initially twice their corresponding grid-line opacity.
  Vertical grid lines stop below the label area so they never paint through
  ruler text.
- Alternating block shade contrast is configuration-driven. The initial
  `block_alternate_shade_factor` is `0.8`, meaning a subtle 20% blend toward
  white rather than a strongly contrasting shade.
- Each section-row label also shows its calibrated beginning and ending media
  times to whole-second precision. These timestamps are display-only and do
  not alter the underlying exact calibration.
- Double-clicking a count block edits an optional short annotation. The count
  total remains visible above the centered annotation. A leading count marker
  encoded as `N: note` displays only `note` and emphasizes the ruler tick at
  count `N`; for example, `4: break` displays “break” with count 4 marked.
  The mark uses an elbow-style multi-segment leader connecting the specified
  beat to its annotation, similar to a flowchart connector. A tick left of the
  text uses its left-center anchor; a tick right of it uses its right-center
  anchor. Both routes have one bend. A tick horizontally beneath the text uses
  its bottom-center anchor and a three-segment, two-bend route. The top-center
  anchor is never used.

## Project persistence

- File menu and toolbar actions expose Open, Save, and Save As; Ctrl+O and
  Ctrl+S follow desktop conventions.
- The project toolbar is fixed and non-floatable, with no user drag handle.
  Its Open and Save actions use Lucide `folder-open` and `save` icons.
- A trailing `*` in the window title means authoritative state differs from
  the last successful save. Failed or cancelled saves never clear it.
- Opening or closing dirty work offers Save, Discard, and Cancel. Cancel leaves
  the current project untouched.
- Load validation completes before current state is replaced. Reopened embedded
  audio behaves like selected audio without depending on its original path.
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
  colors form faint aligned backgrounds behind the waveform. Those backgrounds
  are 70% transparent by default, controlled by
  `waveform_region_transparency`. A **Section labels** display toggle, enabled
  by default through `show_waveform_section_labels`, shows each section name at
  its beginning. Labels are drawn clear of both waveform rulers.
- The complete Structure workspace scrolls vertically when waveform or window
  height leaves too little room; controls must never overlap the section grid.
- Variable lengths and incomplete blocks are valid. Visual centering of short
  rows carries no timing meaning.
- Reusable named template libraries and palette themes are future work.

## Printable creation sheet

- **File → Export Creation Sheet PDF…** exports the current Structure board as
  a handwriting-friendly reference without mutating or saving the project.
- Letter landscape is the configurable default page format. The longest
  section fits the writable page width; rows paginate vertically.
- Every page repeats `Project.name`, the current `.kro` basename or
  `Unsaved project`, and the repeating dance-count ruler.
- Project headers, ruler labels, and section-row labels retain normal opacity.
  The writable block playground alone uses the configurable
  `playground_opacity`, initially `0.25`.
- Printed blocks retain totals, annotations, count leaders, and calibrated row
  timestamps. Selection, playhead, waveform/grid Anchor, controls, and other
  interactive state never appear.
- This creation sheet is a Structure prototyping aid, not the complete V1
  choreography-sheet PDF export.

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
