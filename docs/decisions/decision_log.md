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
