# Handoff — Milestone 4A: first choreography-authoring slice

**Date:** 2026-10-12
**Status:** Approved
**Approval:** Owner approved the decision-complete implementation plan in chat.

## Outcome

Add explicit Setup and Choreography workspaces. Setup retains authoritative
song/tempo/Structure editing. Choreography presents that Structure as a
read-only vertical reference and lets users create and revise independent move
blocks with compact playback controls.

## Architecture contract

- A Qt-independent application session owns the current project, dirty state,
  and shared reversible-command history.
- Domain code owns exact beat timing, move transformations, validation, and
  conflict resolution. GUI code renders state and translates user intent.
- Existing Structure mutations and new choreography mutations use the same
  session. Failed or cancelled operations do not alter state or history.
- Persistence, audio, Qt widgets, and dialogs remain boundary adapters.

## Interaction contract

- Top-level **Setup** and **Choreography** tabs share one project, playback
  session, playhead, and save state.
- Choreography uses a thin seekable waveform strip with Play/Pause, Stop, and
  a stable right-aligned time label. Calibration tools remain in Setup.
- Structure rows/count blocks are read-only backgrounds. Smaller move blocks
  overlay aligned track lanes. Existing tracks are rendered; track management
  is deferred.
- Drag empty time to create; drag a move to reposition; drag its edges to
  resize. Whole beats snap by default and Shift temporarily disables snapping.
- Double-click edits a label inline. A right inspector edits label, notes,
  start, and duration. Delete, Ctrl+Z, and Ctrl+Shift+Z operate globally.
- Cross-row fragments are presentations of one move and select/edit together.
- Same-track overlap offers Cancel, Trim edited move, or ripple later moves.
  An accepted resolution is one atomic command.

## Deliberate boundary

No track creation/reordering, multi-move selection, copy/paste, split/merge,
continuous Timeline editor, or complete editable Sheet parity in this slice.

## Acceptance

- Pure command/session and choreography-domain tests cover success, failure,
  conflict resolution, exact timing, dirty state, undo, and redo.
- GUI tests cover mode separation, read-only Structure reference, compact
  transport, move manipulation, inspector/inline edits, shortcuts, and
  persistence refresh.
- Black, mypy, pytest, build, and human visual/interaction review pass.
