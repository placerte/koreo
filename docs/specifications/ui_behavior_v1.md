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
- A faint constant-tempo beat grid appears behind the waveform. Before an
  anchor exists it starts at media time zero; setting beat 0 shifts it
  immediately to the anchor.
- A plain left click seeks to the clicked media time.
- A left drag pans after crossing the platform drag threshold. A completed pan
  must not also seek on release. Middle-button panning is not used.
- Wheel zoom is centered under the pointer. Zoom in, zoom out, and fit controls
  are also available.
- Waveform, beat grid, anchor, and playhead always use the same time transform.
- Follow mode holds the playhead near 35% of the viewport while zoomed and
  moves the waveform beneath it. Wheel zoom or drag-pan suspends Follow; an
  explicit control resumes it.

## Calibration staging

- Anchor and optional later-point refinement belong in the waveform-backed
  song-structure workflow, not the Tap BPM modal.
- Final calibration UX is deferred until song-structure authoring exists.

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
