# Repository instructions

### LLM Context Blocks

These files contain reusable instructions and workflows
that may be relevant when working in this repository.

<!-- agmod:start -->

- llm/agent_executor_instructions_v_1.md
- llm/app_dev_execution_starter_v1.md
- llm/code_style.md
- llm/curated_llm_workflow_v_1.md
- llm/decision_log.md
- llm/general_executor_instructions_v1.md
- llm/general_project_starter_v1.md
- llm/git_hosting_toolbox.md
- llm/gotchas.md
- llm/progress_tracker.md
- llm/project_handoff_standard_v1.md
- llm/project_intake_v1.md
- llm/project_operating_model_v1.md
- llm/python_toolbox.md
- llm/user-persona.md
- llm/webclient_project_instructions_v_1.md

<!-- agmod:end -->


Koreo has completed project intake and is ready for Milestone 1 execution.
Treat written repository artifacts as the source of truth and keep the first
implementation small, local, and easy to inspect.

## Working rules

- Use `docs/handoffs/handoff_261011_1.md` as the sole execution contract for
  Milestone 1. The original scratch prompt is archived for provenance and is
  no longer authoritative.
- Follow the active instructions in `llm/` in the order documented below.
- Stop and ask when a decision would materially affect product behavior and
  is not specified in an artifact. Record important approved decisions using
  the format in `llm/decision_log.md`.
- Keep domain logic separate from UI and file/audio IO.
- Use Python, type hints, simple explicit control flow, and small modules.
- Use `uv` for environments, dependencies, running, testing, and builds. Do
  not introduce `pip`, `venv`, or Conda workflows.
- Use a `src/` package layout, Hatchling, pytest, Black, and mypy when Python
  implementation begins.
- Add or update tests for every behavior change. Run all relevant tests before
  declaring work complete.
- Do not publish packages, create releases, or make forge-visible changes
  unless the user explicitly asks.
- Preserve unrelated user changes in the working tree.

## Instruction index

Read these files according to the task rather than loading every reference by
default.

### Core workflow (active)

- `llm/project_operating_model_v1.md` — highest-level authority, roles,
  artifact-driven lifecycle, and completion rules.
- `llm/project_intake_v1.md` — required project-intake information and output.
- `llm/project_handoff_standard_v1.md` — required handoff sections and
  execution contract.
- `llm/general_executor_instructions_v1.md` — execution flow, ambiguity, and
  completion rules.
- `llm/decision_log.md` — append-only format for important decisions.

### Application development (active)

- `llm/app_dev_execution_starter_v1.md` — ordered app-development instruction
  preset.
- `llm/agent_executor_instructions_v_1.md` — app-development execution and
  Definition of Done rules.
- `llm/python_toolbox.md` — authoritative Python toolchain, project layout,
  typing, formatting, testing, packaging, and release defaults.

### Task-specific references

- `docs/handoffs/handoff_261011_1.md` — sole execution contract for Milestone
  1, including scope, implementation order, tests, and Definition of Done.
- `docs/handoffs/handoff_261011_2.md` — approved sole execution contract for
  Milestone 2 audio import, calibration, playback, waveform, and counts.
- `docs/specifications/koreo_specs_v1.md` — historical S-001–S-030 product
  checkpoint. It is planning context, not an execution contract.
- `docs/references/display-a.xlsx` — non-binding UX reference for the wrapped
  choreography-sheet concept.
- `docs/references/chatgpt-spec-interview-2026-10-11.md` — complete
  browser-visible transcript of the product-specification interview. Use only
  for historical background and rationale; it does not override a handoff or
  other authoritative repository artifact. The companion `.json` file
  preserves normalized message IDs, ordering, timestamps, and source metadata.
- `llm/curated_llm_workflow_v_1.md` — historical description of the full
  web-client design interview, handoff generation, local execution, and review
  loop. It is deprecated but remains useful workflow context.
- `llm/webclient_project_instructions_v_1.md` — historical rules for the web
  client as design authority, including phase transitions and handoff content.
  It is deprecated and does not override active workflow instructions.
- `llm/git_hosting_toolbox.md` — use for GitHub/Gitea issues, labels, hosted
  repository operations, and explicitly requested releases.
- `llm/gotchas.md` — consult when diagnosing Python packaging or PyInstaller
  import failures. This document is deprecated, so use it as troubleshooting
  context rather than governing policy.
- `llm/code_style.md` — additional readability, documentation, and testing
  guidance. This document is deprecated; active instructions take priority.
- `llm/user-persona.md` — historical user preferences for direct, pragmatic,
  low-bloat Python solutions. This document is deprecated and is context only.
- `llm/general_project_starter_v1.md` — ordered preset for general projects;
  the app-development preset is more specific for this repository.
- `docs/archive/scratch-prompt.md` — superseded intake notes retained only for
  provenance.

## Current product boundary

The initial concept is a lightweight choreography-planning editor. A user
places an audio track on a time- or beat-based grid, manually describes song
structure, adds short notes, and subdivides grid regions to describe moves.

Video synchronization, tempo detection by tapping, custom snap markers, and a
video-backed move library are future ideas, not current implementation scope,
until a handoff explicitly includes them.
