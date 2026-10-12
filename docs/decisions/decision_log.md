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
