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

## KOR-DEC-009 — Derive sections from blocks and anchor structure to media

- **Date:** 2026-10-11
- **Context:** Structure-board monkey testing refined internal block editing,
  insertion ripple, and calibration against an identifiable musical one.
- **Decision:** Count blocks are real child regions and a section is their
  exact sum. Block edits and inserted sections ripple later structure. A
  selected section start can become the grid Anchor at the current playhead;
  earlier material is retained at negative backend beats. Calibrated structure
  drives both its play cursor and faint waveform section backgrounds.
- **Rationale:** Intros often contain fewer than four 8-count blocks, while a
  recognizable later downbeat is frequently the safest alignment point.
- **Impact:** The AABA template creates four 8-beat children per row. UI labels
  use “Anchor,” not “beat 0.” Dancer-facing local counts never expose negative
  backend coordinates.

## KOR-DEC-010 — Waveform Anchor is authoritative

- **Date:** 2026-10-12
- **Context:** The first structure-calibration implementation let a selected
  section reset the Anchor to the current playhead, reversing the intended
  ownership and lacking exact child-block selection.
- **Decision:** Only the waveform controls the Anchor media time. The Structure
  board selects an exact child block and declares that its start corresponds
  to the existing Anchor. This operation rebases structure beat coordinates
  but must never change the calibration's anchor time or waveform marker.
- **Rationale:** Media alignment is established against the waveform first;
  structure describes which musical boundary occurs there.
- **Impact:** Structure alignment requires an existing waveform Anchor and is
  available through block selection and the block context menu. Regression
  tests preserve the exact anchor timestamp and marker position.

## KOR-DEC-011 — Preserve responsive structure and waveform feedback

- **Date:** 2026-10-12
- **Context:** Monkey testing exposed a stopped-seek race when anchoring,
  redundant full-waveform painting, repeated waveform decoding after reopen,
  and insufficient feedback while sizing count blocks.
- **Decision:** A waveform click synchronously updates the displayed position,
  and Anchor capture uses that position. Native files may carry an optional
  waveform-peak cache. Full-view painting aggregates peaks per pixel. Anchor
  locations use a shared glyph plus the existing strong Structure edge.
  Structure resize previews update continuously, blocks include beat ruler
  ticks, and alternate shading uses the packaged `0.8` appearance setting.
- **Rationale:** Calibration must work without starting playback, transport
  animation should remain smooth at full-song zoom, and direct manipulation
  must communicate its result before commit.
- **Impact:** Cached peaks are disposable derived data and do not change the
  authoritative project model. A future framework must retain these observable
  responsiveness and feedback rules even if its rendering mechanism differs.

## KOR-DEC-012 — Add lightweight structure annotations and timing context

- **Date:** 2026-10-12
- **Context:** Monkey testing showed that the Structure board needed brief
  musical cues without turning count blocks into a full choreography editor,
  plus clearer correspondence between rows and the waveform.
- **Decision:** Count blocks accept inline annotations by double click while
  keeping the count total visible. An optional `N: note` prefix marks count N
  but renders only the note. Calibrated section rows show whole-second start
  and end times. Waveform structure bands show section names and use a
  configuration-driven transparency of `0.7` by default.
- **Rationale:** These additions make musical landmarks quick to record and
  relate the Structure board to audio while keeping exact timing authoritative
  in the domain model.
- **Impact:** Block labels remain ordinary persisted region labels. A future
  GUI may render them differently but must preserve editing, marker syntax,
  whole-second timing context, and configurable waveform transparency.

## KOR-DEC-013 — Give text editing priority and add musical rulers

- **Date:** 2026-10-12
- **Context:** Global Space playback prevented ordinary spaces in text fields,
  and the Structure and waveform canvases lacked sufficient positional context.
- **Decision:** Focused text entry owns Space; inline Enter accepts and Escape
  cancels. Structure selection moves the playhead by default through config.
  Structure gains a beat ruler and configurable minor/primary grid opacities.
  Its labels toggle between repeating local dance counts and continuous beats.
  Major/minor label opacity is configured separately at twice the initial grid
  opacity, and grid lines stop below the labels. The waveform gains adaptive
  time and beat rulers. Annotated beat markers use elbow-style connector lines;
  sources outside a label use the nearest left/right text anchor and one bend,
  while an under-text source uses the bottom-center anchor and two bends. The
  top text anchor is unused.
- **Rationale:** Editing conventions must take priority while typing, while
  persistent musical axes make direct placement and comparison predictable.
- **Impact:** Future UI implementations must preserve this focus ownership and
  ruler behavior even if their widgets and rendering APIs differ.

## KOR-DEC-014 — Make waveform section labels an independent display layer

- **Date:** 2026-10-12
- **Context:** Adding waveform rulers obscured section names that had shared
  the lower ruler area.
- **Decision:** Section names render clear of both rulers and have an explicit
  display toggle enabled by default through `show_waveform_section_labels`.
  Toggling names does not affect structure-region backgrounds or project data.
- **Rationale:** Labels and colored timing bands serve different visual needs
  and should be independently controllable.
- **Impact:** Future waveform renderers must preserve the independent label
  layer and its default-visible toggle.

## KOR-DEC-015 — Export a faded Structure creation sheet for handwriting

- **Date:** 2026-10-12
- **Context:** The owner needs a paper reference while trying choreography in
  practice before the complete choreography-sheet export exists.
- **Decision:** Export a narrow Structure creation-sheet PDF on configurable
  Letter landscape pages. Fit the longest section horizontally, paginate rows,
  and repeat the project title, project filename, and ruler. Keep all header
  content fully opaque while fading only the block playground to `0.25` by
  default. Exclude the Anchor and every other interactive overlay.
- **Rationale:** A faint structural reference leaves physical handwriting
  dominant without losing musical context.
- **Impact:** Creation-sheet rendering is independent from the interactive
  canvas and from the future full choreography PDF tracked by GitHub #42.

## KOR-DEC-016 — Edit the project title in the main header

- **Date:** 2026-10-12
- **Context:** Creation sheets require an owner-controlled project title rather
  than relying on fixture or file-derived names.
- **Decision:** The main header exposes `Project.name` as an editable field.
  Non-empty changes update authoritative state and dirty the project; empty
  edits restore the current value. Save/load preserves the name and PDF export
  consumes it directly.
- **Rationale:** Naming is project metadata and should be established before
  export without a separate settings workflow.
- **Impact:** Future UI frameworks must provide an equally direct project-name
  editor connected to persisted project state.

## KOR-DEC-017 — Separate full-song arrangements from phrase forms

- **Date:** 2026-10-12
- **Context:** AABA describes a chorus form, not necessarily a complete swing
  recording, and a single text generator button could not expose useful
  alternatives compactly.
- **Decision:** Use a split template button with an extended swing arrangement
  as its default and separate menu groups for full-song arrangements and
  phrase/forms. Provide AABA, ABAB, ABAC, ABBA, AAAA, AAB blues, AB, ABC, and
  ABACA. The AAB blues form fixes each phrase at 16 beats. Manual drawing is
  the Custom path. Resolve button artwork through a centralized semantic icon
  role, and treat section colors as theme accent roles.
- **Rationale:** Arrangement and form can now evolve independently, while the
  compact control and semantic visual roles prepare the UI for theme support.
- **Impact:** Future templates should declare whether they are arrangements or
  phrase forms and any fixed musical length instead of embedding UI logic.

## KOR-DEC-018 — Keep the editing surface compact and contextual

- **Date:** 2026-10-12
- **Context:** Prototype growth left long action labels, a duplicated Structure
  property strip, and an exposed calibration-refinement experiment competing
  with the song canvas for space.
- **Decision:** Familiar high-frequency actions use palette-colored Lucide
  outline icons behind semantic roles, with tooltips and accessible
  names. Structure labels edit inline, while
  color and deletion remain contextual; duration is derived from count blocks,
  so the duplicate selected-row form is removed. Later-point calibration
  refinement is deferred and hidden until its workflow is designed alongside
  song structure. Obsolete widget-coupled tests are replaced with tests of the
  current interaction signals and resulting project behavior.
- **Rationale:** The canvas should dominate the workspace, and tests should
  protect user behavior instead of preserving abandoned controls.
- **Impact:** A future GUI must preserve semantic actions, accessibility, and
  contextual editing, but may replace all artwork and widget classes through
  its theme/icon provider.

## KOR-DEC-019 — Consolidate setup around the Structure workspace

- **Date:** 2026-10-12
- **Context:** Monkey testing found that the top-level setup rows, read-only
  Timeline/Sheet tabs, text checkboxes, and status suffixes competed with the
  waveform and Structure canvas without helping the active workflow.
- **Decision:** Structure is the sole visible prototype workspace. Audio,
  decimal BPM, Tap BPM, waveform display toggles, zoom, Follow, and Anchor
  actions share the waveform toolbar. Count origin and default group move to
  an advanced song-settings dialog with numeric controls. Display and
  selection options use accessible Lucide icon toggles. Successful waveform
  loading shows the filename without a redundant “waveform ready” suffix, and
  the Anchor glyph renders above ruler layers in the lower waveform area.
- **Rationale:** The current product workflow is audio-first structure mapping;
  controls should sit beside the object they affect and the canvas should own
  most of the window.
- **Impact:** Timeline and Sheet presentation code may remain as non-visible
  groundwork, but it is not part of the current prototype UI. A future rewrite
  should preserve the consolidated toolbar and advanced-setting hierarchy.

## KOR-DEC-020 — Encode section length in structure templates

- **Date:** 2026-10-12
- **Context:** The standalone Section beats control appeared ineffective and
  duplicated musical knowledge already represented by named presets. Reopening
  a saved project also failed to refresh the visible project-name field.
- **Decision:** Every structure preset owns its section length. Initial forms
  use 32 beats except AAB blues, whose phrases use 16 beats. Remove the
  standalone duration control; manually inserted sections retain a 32-beat
  default and remain editable through their blocks. Loading a project always
  synchronizes its persisted name into the main project-name editor. Advanced
  song settings use Lucide's `flask-conical` icon alongside waveform tools.
- **Rationale:** Presets should be complete musical definitions, and reopening
  must visibly reproduce authoritative project metadata.
- **Impact:** New templates must declare their section length explicitly.
  Project persistence regression coverage includes the displayed title.

## KOR-DEC-021 — Group waveform tools by task

- **Date:** 2026-10-12
- **Context:** The consolidated waveform toolbelt contained the right actions
  but mixed song, display, calibration, and advanced controls in an unclear
  order. Raw tapped BPM precision and verbose Anchor status added noise.
- **Decision:** Order separator-bounded groups as song file, view/display,
  BPM/Anchor, then Advanced options. BPM is a compact numeric spin box showing
  two decimals while internal tap measurement may retain higher precision.
  Anchor status shows only its media timestamp because the waveform marker
  already identifies it.
- **Rationale:** Spatial grouping communicates scope faster than labels, while
  two BPM decimals are enough for deliberate human adjustment.
- **Impact:** Future toolbars must preserve this grouping and concise display,
  though exact widget geometry may change.

## KOR-DEC-022 — Stabilize the project header and file toolbar

- **Date:** 2026-10-12
- **Context:** The project toolbar exposed an unnecessary drag handle and used
  platform-dependent artwork, while the project name read like an ordinary
  small input. BPM arrow adjustment was finer than useful for manual work.
- **Decision:** Make the project toolbar fixed and non-floatable, using Lucide
  `folder-open` and `save`. Present the editable project name as a wider bold
  title. Set manual BPM arrow increments to `0.5` while retaining two-decimal
  display and exact tap measurement internally.
- **Rationale:** Stable placement and consistent icons reduce visual noise;
  stronger title hierarchy improves project orientation.
- **Impact:** These presentation and interaction details are required behavior
  for future framework implementations.

## KOR-DEC-023 — Add a fixed Structure board command toolbar

- **Date:** 2026-10-12
- **Context:** Structure controls scrolled out of view and implemented editing
  commands were discoverable mainly through keyboard shortcuts or context
  menus. The fixed beat width also limited navigation of longer structures.
- **Decision:** Name the workspace the Structure board and keep its toolbar
  outside the scroll viewport. Separate View from Edit commands. Provide
  Lucide-icon actions for horizontal zoom out/in/fit, display modes, template
  generation, add section, add 8-count block, undo, copy, paste, delete, and
  Anchor alignment. Preserve ordinary wheel vertical scrolling; Ctrl+wheel
  adjusts horizontal beat scale only.
- **Rationale:** Persistent, grouped commands improve discovery while retaining
  direct manipulation and established shortcuts.
- **Impact:** Horizontal zoom is presentation state, not project data. Future
  frameworks must preserve modifier ownership and fixed-toolbar behavior.

## KOR-DEC-024 — Separate section and block creation shortcuts

- **Date:** 2026-10-12
- **Context:** Enter previously created an 8-count block, making the more
  structural add-section command less immediate and leaving shortcut discovery
  dependent on prior knowledge.
- **Decision:** Enter creates a new section after the current selection, while
  Ctrl+Enter creates an 8-count block after the selected block or at the end of
  the selected row. Inline text editors retain Enter-to-accept. Tooltips show
  established keyboard and pointer shortcuts in parentheses.
- **Rationale:** The simpler key performs the larger, primary Structure action;
  the modifier distinguishes editing within a section and visible hints make
  both behaviors discoverable.
- **Impact:** Future GUI implementations must preserve these command semantics
  independently from their widget or framework-level shortcut mechanism.

## KOR-DEC-025 — Separate Setup and Choreography workspaces

- **Date:** 2026-10-12
- **Context:** Song setup is complete enough to become a reference for the
  primary choreography workflow. Adding another editor directly to the main
  window would compound distributed project mutation and private undo state.
- **Decision:** Provide top-level Setup and Choreography tabs. Introduce a
  Qt-independent application session for project state, dirty state, and
  shared reversible commands. Choreography uses a compact transport and draws
  smaller move blocks over read-only Structure rows, with a side inspector.
- **Rationale:** A focused seam removes real coupling while the first editing
  slice tests the product workflow; a broad speculative rewrite would not.
- **Impact:** Future views dispatch commands rather than owning project
  history. Setup remains authoritative for tempo, Anchor, and Structure.

## KOR-DEC-026 — Default choreography to one compact lane per section

- **Date:** 2026-10-13
- **Context:** The first board used separate Lead and Follow lanes plus a
  section-title row, consuming three rows per section even though ordinary
  choreography authoring does not yet require multiple move tracks.
- **Decision:** New projects use one generic Choreography track. Single-track
  sections render as one row with the section name integrated into its label.
  The simplified playback view shows section colors, names, and playhead but
  no waveform peaks, beat rulers, or Anchor. Existing multi-track project data
  remains supported and renders as labeled lanes.
- **Rationale:** The common workflow gains substantially more board space
  without discarding the data model needed for later multi-couple or
  leader/follower arrangements.
- **Impact:** Future implementations distinguish the detailed Setup waveform
  from the simplified section overview and optimize the one-track case.

## KOR-DEC-027 — Make choreography navigation compact and self-explanatory

- **Date:** 2026-10-13
- **Context:** The first simplified transport still resembled a tiny waveform,
  duplicated seeking with a slider, and left move manipulation discoverable
  mainly by experimentation.
- **Decision:** Use a half-height, full-fit section overview with outlines,
  elided labels, beat marks, and a directly draggable playhead. Remove the
  redundant slider. Add semantic cursors, a fixed move Edit strip, and context
  actions. Reopen programmed projects in Choreography and place the normally
  styled project-name field at the right of the fixed project toolbar.
- **Rationale:** Stable navigation and visible affordances dedicate more space
  to authoring while making direct manipulation understandable.
- **Impact:** Detailed waveform zoom/pan remains Setup-only; both playback
  views share direct playhead dragging and future GUIs preserve these cues.

## KOR-DEC-028 — Keep the fresh and default choreography view quiet

- **Date:** 2026-10-13
- **Context:** Per-beat marks made the full-song overview busy, seeded demo
  moves incorrectly implied a programmed project at launch, and an always-open
  inspector consumed board width before a move was selected.
- **Decision:** Draw simplified overview divisions at the configured default
  count-group interval. Launch with no moves so Setup remains active. Collapse
  the move inspector by default and toggle it from the left side of the Edit
  strip with Lucide panel-right open/close icons.
- **Rationale:** Defaults should represent an unprogrammed project and reserve
  maximum space for the primary board until details are requested.
- **Impact:** Representative test data remains available separately from the
  starter project; count-group changes refresh overview divisions immediately.

## KOR-DEC-029 — Extend direct manipulation into the boards

- **Date:** 2026-10-13
- **Context:** Playback views allowed direct playhead dragging, but their board
  representations did not. Touching move edges also made resize ownership
  unstable, and the inspector toggle read as another edit command.
- **Decision:** Make the Structure and Choreography playheads draggable across
  both axes, mapping through whichever section row is under the pointer. When
  multiple touching moves share a hit, prefer the selected move. Place the
  inspector toggle in a separate right-aligned toolbar group.
- **Rationale:** Consistent direct manipulation reduces travel to playback,
  preserves user focus during precise resizing, and clarifies toolbar roles.
- **Impact:** Vertical playhead dragging may intentionally jump across gaps;
  ambiguous edge priority is selection-dependent but ordinary hits are not.

## KOR-DEC-030 — Pin and synchronize board rulers

- **Date:** 2026-10-13
- **Context:** Long structures scrolled count labels out of view, and only the
  Structure board could switch between repeating dance counts and continuous
  beat numbers.
- **Decision:** Render each board ruler as a fixed viewport overlay synchronized
  with horizontal scroll and zoom. Give Choreography the same icon, tooltip,
  checked state, and repeating/continuous numbering behavior as Structure.
- **Rationale:** Count context must remain visible during long-form editing and
  equivalent grids should expose equivalent display controls.
- **Impact:** The canvas retains its coordinate system while the sticky ruler
  mirrors its presentation; future GUIs keep ruler and grid state synchronized.

## KOR-DEC-031 — Share board zoom behavior and coordinate origins

- **Date:** 2026-10-14
- **Context:** Structure's pinned ruler inherited the viewport origin while its
  canvas inherited a platform layout margin, causing a visible horizontal
  offset. Choreography also lacked Structure's board-level zoom controls.
- **Decision:** Give both board canvases the same zero-offset ruler origin and
  horizontal zoom interaction: toolbar out/in/fit controls plus Ctrl+wheel,
  with ordinary wheel input reserved for vertical scrolling.
- **Rationale:** Equivalent beat grids should align and navigate consistently,
  independent of platform layout defaults or editing mode.
- **Impact:** Zoom changes repaint both canvas and pinned ruler; future UI
  rewrites must preserve their shared coordinate origin and interaction model.
