# Koreo decision log

This append-only log records owner-approved product decisions that refine an
active handoff without changing its milestone boundary.

## KOR-DEC-001 — Separate import, tempo, and waveform calibration UI

- **Date:** 2026-10-11
- **Context:** The first Milestone 2 test build combined file selection,
  transport, tempo tapping, anchor capture, and refinement in one setup modal.
  Owner review found that this did not represent the intended production
  workflow.
- **Decision:** Song selection belongs to project creation/import. The BPM
  modal contains only manual BPM entry plus tap/reset controls. Primary anchor
  capture and the optional later calibration point belong in the main song
  structure UI, where the waveform is visible. Time readouts reserve stable
  width so digit changes cannot move the play bar or cursor.
- **Rationale:** Anchor and calibration choices require visual waveform
  context, while tempo tapping is a small focused operation. Stable transport
  geometry avoids distracting motion during playback.
- **Impact:** Replace the combined `SetupDialog` before the next owner review.
  Keep the already verified audio-decoder and exact calibration domain code,
  but recompose them across import, BPM, and structure-view UI. The current
  combined test build is not an accepted UX baseline.

## KOR-DEC-002 — Tap modal owns a disposable playback session

- **Date:** 2026-10-11
- **Context:** Owner review refined the focused BPM interaction after the
  import and tempo interfaces were separated.
- **Decision:** The Tap BPM modal contains no editable numeric BPM field. It
  starts the selected song automatically when shown, immediately accepts
  Space taps, and displays a non-interactive playhead with stable-width time
  text. Closing or canceling the modal stops playback and discards the tap
  session; accepting applies its estimate. Manual BPM entry remains in the
  main application UI.
- **Rationale:** Tapping should be a focused listen-and-react task. Numeric
  correction is a separate interaction, and modal playback must not outlive
  the temporary tapping session.
- **Impact:** The main window enables Tap BPM only after a song validates and
  owns manual BPM entry. The modal owns its temporary media player and always
  stops it on exit.

## KOR-DEC-003 — Stabilize dynamic time-label geometry

- **Date:** 2026-10-11
- **Context:** Human review of the Tap BPM modal found that a changing current
  time made the label text visibly jiggle even after the neighboring playhead
  width had been stabilized.
- **Decision:** Every dynamic time label must reserve a width based on its
  longest expected representation and use deliberate alignment. For the
  common `current / duration` form, use a fixed-width, right-aligned label so
  the duration remains anchored and current-time digits grow leftward.
- **Rationale:** Playback updates should not move the label itself, adjacent
  playheads, buttons, or other neighboring UI components.
- **Impact:** Reuse this rule for main transport, waveform, calibration,
  preview, and export-progress time displays. Tests should verify fixed
  geometry and alignment where practical.

## KOR-DEC-004 — Waveform navigation must remain dynamic

- **Date:** 2026-10-11
- **Context:** Monkey testing identified that full-song waveform scale was too
  coarse for placing beat 0 and questioned whether the display was a static
  image generated on playback.
- **Decision:** Keep the waveform as a dynamically painted widget generated
  asynchronously immediately after file selection. Provide pointer-centered
  wheel zoom, middle-button horizontal pan, and explicit zoom in/out/fit
  controls. Waveform peaks, playhead, and anchor share the same visible-time
  transform.
- **Rationale:** Precise calibration needs inspectable waveform detail without
  raster scaling drift or coupling extraction to playback.
- **Impact:** File selection starts extraction and visibly reports progress.
  Playback does not generate the waveform. Navigation changes presentation
  state only and preserves song, calibration, and playback position.

## KOR-DEC-005 — Waveform detail, grid, processing, and following

- **Date:** 2026-10-11
- **Context:** A second monkey-testing pass approved zoom but found the
  full-song envelope visually coarse, requested processing feedback and a BPM
  grid, and proposed a fixed playhead while the waveform moves.
- **Decision:** Extract approximately 10 ms peak windows (bounded to 30,000
  buckets), show an indeterminate Processing song indicator, and paint a faint
  constant-tempo grid behind the waveform. Before calibration the grid is
  provisionally offset from media time zero; setting beat 0 immediately moves
  it to the anchor. Follow mode keeps the red playhead at a stable 35% offset
  while zoomed. Wheel zoom or middle-drag suspends following, and a visible
  Follow toggle resumes it.
- **Rationale:** Higher-resolution source peaks remain useful under zoom,
  visible progress explains asynchronous decoding, and a moving waveform
  makes beat alignment easier to inspect without removing manual navigation.
- **Impact:** Waveform, BPM grid, anchor, and playhead continue to share one
  time transform. Follow state is presentation-only and never changes media
  position or calibration.

## KOR-DEC-006 — Primary-pointer waveform navigation and global Space

- **Date:** 2026-10-11
- **Context:** Monkey testing requested direct waveform seeking, primary-button
  panning, and predictable playback control regardless of focused main-window
  widget.
- **Decision:** A left click on the waveform seeks to its mapped media time.
  Left-drag pans only after crossing Qt's platform drag threshold; releasing a
  drag never also seeks. Middle-button panning is removed. In the main window,
  Space is a non-auto-repeating Play/Pause shortcut across the entire widget
  hierarchy instead of activating the focused control. The modal Tap BPM
  session remains the intentional exception and owns Space while open.
- **Rationale:** Click and drag can share the primary pointer safely when
  movement is classified using the platform convention. A window-level
  shortcut prevents accidental button activation during playback work.
- **Impact:** Waveform pointer tests must distinguish click from drag. Future
  main-window controls must not override Space; modal tools must explicitly
  define whether they temporarily own it.

## KOR-DEC-007 — Preserve UX independently of GUI framework

- **Date:** 2026-10-11
- **Context:** The current prototype may be rewritten in another GUI framework
  before official V1.0.
- **Decision:** Maintain `docs/specifications/ui_behavior_v1.md` as the
  framework-neutral source for approved interaction behavior. Record observable
  inputs, state transitions, geometry invariants, cancellation semantics, and
  acceptance checks rather than toolkit-specific mechanisms.
- **Rationale:** A framework rewrite must not silently discard behavior refined
  through human testing.
- **Impact:** Every accepted UI adjustment updates the behavior specification
  and relevant review evidence. Framework-specific implementation remains
  replaceable.

## KOR-DEC-008 — Defer final calibration UX until song structure

- **Date:** 2026-10-11
- **Context:** Waveform calibration was usable, but owner review determined
  that final anchor/refinement interaction will benefit from the song-structure
  workflow.
- **Decision:** Preserve the exact calibration domain and prototype controls,
  but defer final UX approval until structure authoring exists. Continue with
  count presentation first.
- **Rationale:** Calibration points can then be placed and understood against
  meaningful structural regions instead of an isolated waveform.
- **Impact:** Tap BPM remains approved. Anchor/refinement are not considered
  final and must be revisited during the structure milestone.
