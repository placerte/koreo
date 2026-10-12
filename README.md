# Koreo

Koreo is a lightweight desktop editor for planning choreography against the
musical structure of a song. It is designed to show the same project in two
complementary forms: a continuous timeline for detailed timing work and a
wrapped choreography sheet for rehearsal and review.

The V1 roadmap is defined and tracked on GitHub. Milestone 1 is complete,
Milestone 2 audio/grid work is under review, and the first approved Milestone
3 song-structure slice is available for assessment.

## Intended V1 workflow

V1 is planned to support a choreographer who wants to:

- import an audio track and calibrate it with a BPM and anchor beat;
- play and navigate the track against a beat-aligned waveform;
- describe musical sections, phrases, counts, and subdivisions;
- add and edit choreography moves in either the Timeline or Sheet view;
- see changes reflected consistently in both views;
- save and recover a portable, versioned project; and
- export readable choreography sheets to PDF and Excel.

Automatic song analysis, variable-tempo mapping, video synchronization, and a
video-backed move library are outside the committed V1 scope.

## Current status

The repository currently provides:

- the product interview has been distilled into a reviewed specification
  checkpoint;
- approved execution handoffs for Milestones 1, 2, and the initial Milestone 3
  slice;
- all six V1 milestones and their work items are tracked as GitHub issues;
- dependencies and parent/sub-issue relationships are recorded; and
- the local progress tracker mirrors the hosted roadmap.

- the completed Milestone 1 domain model and read-only dual-view prototype;
- exact constant-tempo calibration and tap-tempo logic; and
- an application shell with MP3/WAV song selection, waveform playback,
  manual/tap BPM, and shared count presentation; and
- an initial Structure panel that generates and directly edits vertical,
  beat-aligned AABA section rows.

Milestone 2 work is coordinated under
[issue #11](https://github.com/placerte/koreo/issues/11). The current
Milestone 3 slice is tracked by [issue #20](https://github.com/placerte/koreo/issues/20).

## Milestone 1

Milestone 1 delivers the smallest reviewable vertical slice: a tested,
GUI-independent domain model and a read-only PySide6 prototype. The prototype
will render one representative project in both a continuous Timeline view and
a wrapped Sheet view, with an explicit view switch and evidence for human
review.

Milestone 1 intentionally excludes audio, editing, persistence, export, and
packaging. Its sole execution contract is
[`docs/handoffs/handoff_261011_1.md`](docs/handoffs/handoff_261011_1.md).

## V1 roadmap

| Milestone | Outcome | Tracking issue |
| --- | --- | --- |
| 1 | Domain model and read-only dual-view prototype | [#2](https://github.com/placerte/koreo/issues/2) |
| 2 | Audio setup and calibrated beat grid | [#11](https://github.com/placerte/koreo/issues/11) |
| 3 | Musical structure authoring | [#17](https://github.com/placerte/koreo/issues/17) |
| 4 | Choreography authoring | [#24](https://github.com/placerte/koreo/issues/24) |
| 5 | Project persistence and recovery | [#32](https://github.com/placerte/koreo/issues/32) |
| 6 | Choreography sheet exports and integrated workflow | [#38](https://github.com/placerte/koreo/issues/38) |

Milestone 2 and the initial Milestone 3 structure-row slice have approved
handoffs. Further Milestone 3 work and Milestones 4–6 require focused approved
handoffs before implementation begins.

## Architecture and toolchain

The implementation direction is:

- Python and PySide6, with Linux as the first supported development platform;
- exact beat positions represented with `fractions.Fraction` and half-open
  intervals;
- domain logic kept independent from GUI, audio, and file I/O;
- one shared project model rendered by both Timeline and Sheet views;
- `uv` for dependency management and task execution;
- a `src/` package layout with Hatchling; and
- pytest, Black, and mypy for tests, formatting, and type checking.

## Development

Install the locked development environment and launch the prototype:

```console
uv sync
uv run koreo
```

The app opens directly into its main window. Use **Choose song…** to select an
MP3 or WAV and wait for decoder confirmation. Manual BPM is entered beside the
song controls. **Tap BPM** then opens a focused modal that starts the song
automatically, shows its playhead, and is immediately ready for Space taps.
Accepting applies the estimate; canceling or closing stops playback and
discards the tap session. Key auto-repeat is ignored and three seconds of
inactivity starts a new tapping session.

Open the **Structure** tab and choose **Generate AABA** to create the approved
`Intro, A, A, B, A, Outro` starter. Each section begins with real 8-beat child
blocks; resize their edges or use the row context menu to add/delete blocks and
insert sections. Section totals are derived from their children, and timing
changes ripple later rows. A selected section start can become the waveform
grid Anchor, after which the Structure play cursor and waveform backgrounds
share the calibrated mapping.

Run the complete automated checks:

```console
uv run pytest
uv run black --check .
uv run mypy .
uv build
```

The GUI tests select Qt's offscreen platform automatically. To regenerate the
actual application screenshots used for Milestone 1 review in a headless
environment:

```console
QT_QPA_PLATFORM=offscreen uv run python scripts/capture_screenshots.py
```

The editor views remain read-only while Milestone 2 is in progress. Playback,
seeking, waveform display, and waveform-context anchor/refinement controls are
available in the main window. Integration of the calibrated grid and shared
playhead directly into both editor canvases is still pending.

## Project artifacts

Repository artifacts are the source of truth:

- [`docs/handoffs/handoff_261011_1.md`](docs/handoffs/handoff_261011_1.md) — authoritative Milestone 1
  execution contract;
- [`docs/handoffs/handoff_261011_2.md`](docs/handoffs/handoff_261011_2.md) — authoritative Milestone 2
  execution contract;
- [`docs/handoffs/handoff_261011_3.md`](docs/handoffs/handoff_261011_3.md) — authoritative contract for
  the initial Milestone 3 structure-row slice;
- [`docs/progress_tracker.csv`](docs/progress_tracker.csv) — local mirror of
  milestone and issue progress;
- [`docs/specifications/ui_behavior_v1.md`](docs/specifications/ui_behavior_v1.md) —
  framework-neutral interaction behavior to preserve through a GUI rewrite;
- [`docs/specifications/koreo_specs_v1.md`](docs/specifications/koreo_specs_v1.md) — reviewed V1 specification
  checkpoint, not an execution contract;
- [`docs/references/chatgpt-spec-interview-2026-10-11.md`](docs/references/chatgpt-spec-interview-2026-10-11.md)
  — archived product-interview context;
- [`docs/references/display-a.xlsx`](docs/references/display-a.xlsx) — non-binding UX reference;
- [`docs/archive/scratch-prompt.md`](docs/archive/scratch-prompt.md) — superseded
  project-intake notes retained for provenance; and
- [`AGENTS.md`](AGENTS.md) — contributor workflow and instruction index.

Important product decisions should be recorded in the repository. Future
milestones must be translated into focused handoffs rather than implemented
directly from the historical interview or specification checkpoint.

## Contributing

For the active milestone, start with its handoff and follow its ordering, scope limits,
acceptance criteria, and stop conditions. Keep behavior changes tested and
preserve the separation between domain, presentation, and GUI layers. If a
choice would materially change product behavior and is not settled by an
artifact, stop and record the decision before proceeding.

