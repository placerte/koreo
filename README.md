# Koreo

Koreo is an early-stage concept for a lightweight choreography-planning editor.
It aims to make the structure of a song visible on a grid so a user can plan
sections, counts, and moves without the overhead of a full video editor.

## Initial proof of concept

The first version is intended to let a user:

- load a song, such as an MP3 or WAV file;
- place it against a time- or beat-based grid;
- describe the song structure manually, for example `A A B A`;
- describe repeated counts or phrases, for example eight groups of eight;
- attach short text notes to grid regions; and
- subdivide a region to write down individual moves.

Automatic structure detection is not part of this initial concept.

## Possible later work

Ideas beyond the proof of concept include:

- synchronizing video clips with the grid;
- changing video playback speed to match musical tempo;
- tapping along to audio or video to record tempo;
- defining custom snap markers, such as every first beat;
- maintaining a reusable move library; and
- associating move examples and beat signatures with library entries.

These are directions rather than committed requirements.

## Project status

This repository is currently being initialized. The product brief lives in
`scratch-prompt.md`, and contributor instructions are indexed in `AGENTS.md`.
No application stack or runnable implementation has been selected yet.

Before implementation starts, the project still needs explicit decisions on:

- the first user interface (CLI, TUI, desktop, or web);
- how beat and time grids relate;
- how projects, annotations, and subdivisions are stored;
- which audio formats and playback platforms are supported; and
- concrete proof-of-concept acceptance tests.

## Development

The local project guidance currently favors Python with `uv`, a `src/` layout,
pytest, Black, mypy, and Hatchling. Exact setup and run commands will be added
when the first executable handoff defines the application stack.

