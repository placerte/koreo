# Koreo

Koreo is a lightweight desktop editor for planning choreography against the
musical structure of a song. It is designed to show the same project in two
complementary forms: a continuous timeline for detailed timing work and a
wrapped choreography sheet for rehearsal and review.

The project has completed its initial product-specification phase. The V1
roadmap is defined and tracked on GitHub; application implementation has not
started yet.

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

Preparation is complete enough to begin Milestone 1:

- the product interview has been distilled into a reviewed specification
  checkpoint;
- the first executable handoff defines the implementation contract;
- all six V1 milestones and their work items are tracked as GitHub issues;
- dependencies and parent/sub-issue relationships are recorded; and
- the local progress tracker mirrors the hosted roadmap.

There is no runnable application in the repository yet. The next work item is
[issue #3, scaffold the Python package and quality toolchain](https://github.com/placerte/koreo/issues/3),
under the [Milestone 1 parent issue](https://github.com/placerte/koreo/issues/2).

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

Milestones 2–6 describe the agreed roadmap, but each requires its own approved
handoff before implementation begins.

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

Setup, run, and test commands will be documented here when the Milestone 1
scaffold lands. Until then, there are no application commands to run.

## Project artifacts

Repository artifacts are the source of truth:

- [`docs/handoffs/handoff_261011_1.md`](docs/handoffs/handoff_261011_1.md) — authoritative Milestone 1
  execution contract;
- [`docs/progress_tracker.csv`](docs/progress_tracker.csv) — local mirror of
  milestone and issue progress;
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

For Milestone 1, start with the handoff and follow its ordering, scope limits,
acceptance criteria, and stop conditions. Keep behavior changes tested and
preserve the separation between domain, presentation, and GUI layers. If a
choice would materially change product behavior and is not settled by an
artifact, stop and record the decision before proceeding.

