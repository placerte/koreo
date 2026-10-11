# Koreo — Product Specification Checkpoint

**Checkpoint:** 01  
**Date:** 2026-10-11  
**Interview coverage:** S-001 through S-030  
**Status:** Consolidated decisions; interview in progress; **NOT an execution handoff**  
**Next interview question:** S-031

## 1. Purpose and authority

Koreo is a lightweight desktop application for planning choreography against a song's musical structure. It must help users both **author** choreography and **communicate** it in a quickly readable **choreography sheet** (analogous in purpose, not notation, to sheet music). The musical structure is the authoritative reference for the entire song. Choreographic moves occupy independently timed tracks against that musical reference.

This document is a durable checkpoint of the spec'ing interview. Its numbered S-entries record decisions agreed by the user. It is **not** a freeze of all V1 requirements, implementation architecture, UX, or acceptance tests. Future interview decisions may amend entries, with an explicit revision trail. Do not execute from this document alone.

### Requirement status vocabulary

- **V1 required:** A committed capability for the first version.
- **V1 conditional:** Implement if straightforward with the selected libraries; otherwise defer without blocking V1.
- **Deferred:** Not required for V1; avoid unnecessarily blocking its future addition.
- **Open:** Requires an explicit later decision.
- **UX candidate:** Illustrative reference, not binding layout.

## 2. Locked decisions

### Product, technology and model

**S-001 — Native desktop application [V1 required].** A graphical, interactive desktop editor with local audio and file access. Desktop may be implemented using native widgets or web technologies in a desktop shell. Prefer existing effective components over building an editor from scratch.

**S-002 — Technology strategy [decision locked; framework open].** Python + PySide6 is the preferred baseline because it is familiar, but Tauri plus web frontend remains a candidate if available timeline/waveform/grid components materially shorten delivery. Evaluate (in order): reusable components; delivery and maintainability; editing quality; familiarity; footprint/packaging. No final framework selection has been made. An earlier response called this *provisionally locked*; this checkpoint preserves that qualification.

**S-003 — Timeline model [V1 required; future extensibility].** V1 presents a hierarchical musical grid over a timeline capable in the future of supporting independent media tracks. Musical sections, phrases, counts and subdivisions are distinct from media clips with offsets and playback rates. A future video may start before/after the song's first beat and require synchronization; no V1 video implementation is required.

### Tempo, calibration and counting

**S-004 — BPM input and calibration [V1 required].** The user may enter a known BPM directly **or** estimate BPM by tapping the spacebar while listening; tapping is never mandatory. Place one **primary anchor** at any identifiable musical *one*, not necessarily the first one in the recording. Generate a constant-tempo grid. Optionally add one distant **calibration point** at another identified *one* to refine BPM from the elapsed time and the known number of beats between them. Formula: `BPM = 60 × beat_distance / elapsed_seconds`. The calibration point is optional. Names: *anchor* and *calibration point* (not *hook*). Precise UX for specifying beat distance remains to be designed.

**S-005 — Constant tempo [V1 required].** One global BPM; at most one primary anchor and one secondary calibration point. Multiple points, variable tempo, piecewise tempo, and smooth/fluid tempo grids are **deferred**. Two anchors can refine a global average BPM, not correct local tempo fluctuations.

**S-029 — Beat-based timing [V1 required].** Musical beats are the fundamental timeline unit. Dance-count grouping is configurable (e.g. 6-count, 8-count or other phrase lengths); displayed counts may restart per phrase. Musical sections may contain different phrase lengths. Moves can span phrases. Formal time signatures, meter changes and full music notation are not required for V1.

### Musical structure

**S-006 — Flexible hierarchical regions [V1 required].** Musical regions can be recursively subdivided, labeled and annotated, without a fixed depth. Support section/phrase/count-level planning. Reusable presets/templates (e.g. `4×8 AABA`, `6×8 Boogie`, user-defined patterns) are **deferred**; the model should permit them later.

**S-007 — Subdivision [V1 required].** Quickly split regions into equal parts, then manually adjust boundaries to make unequal subdivisions. Snap boundaries to the musical grid. Structural regions and move blocks are distinct; moves may cross region boundaries.

**S-014 — Structure creation [V1 required].** Support both direct drawing/editing of musical regions and simple sequence generation such as `AABA` with specified lengths. Users may subsequently draw, resize, split, merge and relabel regions. This simple sequence generator does **not** imply a reusable template library in V1.

**S-015 — Musical structure as source of truth [V1 required].** A song has one authoritative musical structure, editable by the user. It provides a consistent reference for choreography, musical navigation and visual outputs. The musical structure, independently timed choreography and choreography-sheet presentation are separate concepts. Sheet layout/wrapping/centering must not alter musical timing. The choreography sheet is a primary V1 deliverable, not an optional report.

**S-030 — Repeated sections independent [V1 required].** Repeated `A` labels do not create linked definitions; each occurrence is independently editable. Users should be able to duplicate a section **with its subdivisions** as a convenience. Linked musical patterns and reusable choreography sequences are **deferred**.

### Choreography model and editing

**S-008 — Independent move tracks [V1 required].** Moves have start/end musical positions and an associated choreography track; they can cross any structural boundary. Restructuring the music does not automatically change move timing. Moves align to musical beats/counts or supported subdivisions.

**S-009 — Multiple tracks [V1 required].** New projects start with **one** move track. Users can add, rename and remove tracks for dancers, couples, groups or movement categories. Moves on different tracks may overlap. All tracks share the same musical timeline.

**S-010 — Move content [V1 required].** Each move has a short timeline label and optional detailed free-text notes, plus its timing and track. Selecting a move reveals notes. A future move library, structured properties, training-video references and stitched video demonstrations synchronized to music are **deferred**. Preserve stable move identity to facilitate future references.

**S-011 — Timing precision [V1 required + conditional].** Whole-beat snapping is the default. The usual action is to align the *one* of a move to a song beat. Configurable beat subdivisions are **V1 conditional** only if inexpensive with the chosen component; otherwise deferred. Do not default to sub-beat editing or implement expressive swing timing in V1.

**S-012 — Move editing and prepopulation [V1 required; amended].** Create move blocks by drawing directly on a track; reposition, resize, split, merge and delete them. Users may initialize a track with empty editable blocks either (a) from musical regions/subdivisions, or (b) from a specified count interval, such as 8-count moves typical in Lindy Hop. Users may also start with an empty track. Prepopulated blocks become ordinary, independent move blocks; they are not permanently linked to the structure. **Amendment:** count-interval prepopulation was added after the initial decision.

**S-013 — Independence after initialization [V1 required].** Subsequent ordinary edits to musical structure do not automatically alter existing move blocks. This rule is qualified by S-028 for insertion/deletion of musical time.

**S-028 — Insert/delete counts [V1 required].** Distinguish structural edits (labels, subdivisions, boundaries; moves unchanged) from inserting/deleting counts in the musical timeline. For insertion/deletion, ask whether subsequent choreography should ripple/shift or retain its existing positions. The operation must be undoable. Edge-case handling for moves spanning the edit point remains an open detailed specification.

### Choreography sheet and export

**S-016 — Integrated notation [V1 required].** The choreography sheet visually organizes the song by musical structure while displaying moves, timing, and multiple tracks. Cross-boundary moves must remain understandable. Optimize for dancers' rapid comprehension. Exact visual design remains subject to prototyping.

**S-017 — Outputs [V1 required; amended].** Provide an on-screen choreography sheet, printable paginated **PDF** export and **Excel `.xlsx`** export. Excel was added as an explicit amendment to the initial on-screen+PDF choice. Advanced page-layout controls are not required for V1.

**S-018 — Excel export priority [V1 required].** Excel is a **visual choreography sheet**: preserve musical/choreographic organization through cell formatting, merged cells, labels and blocks where practical. It must be readable, printable and manually editable. A normalized structured-data worksheet is not required. Excel is an output, not the project source of truth.

### Persistence and audio

**S-019 — Portable project format [V1 required; implementation open].** Save/load a self-contained single-file project containing project data and imported audio. Make the internal format versioned/extensible, with a path for future migration. ZIP with JSON metadata/media is a candidate, **not a locked implementation**. Native extension and serialization are open. Excel export is not project persistence.

**S-020 — Audio controls [V1 required + conditional].** Required: play, pause, stop, seek and show synchronized position on the grid. Loop a selected musical region **only if straightforward** with the selected audio library; otherwise defer. Variable playback speed, pitch-preserving stretch, count-in and metronome are deferred.

**S-021 — Waveform [V1 required].** Show a basic audio waveform aligned with the beat grid, supporting zoom/navigation and displaying playhead, anchor and optional calibration point. Allow visual grid alignment. Audio editing, transient detection and automatic beat detection are out of scope.

**S-025 — Save/recovery [V1 required].** Standard Save/Save As; warn on closing unsaved changes; periodic recovery snapshots stored separately from the manually saved project; offer restoration after crash without silently overwriting the last saved project. Snapshot frequency and retention remain implementation decisions.

**S-027 — Audio formats [V1 required].** Import and use MP3 and WAV for playback, waveform and calibration. Imported audio is embedded in the project file. Additional codecs may be supported opportunistically, but are not required or exhaustively tested for V1.

### Views, history and platform

**S-022 — Two editing views [V1 required].** (1) A continuous horizontal timeline view for waveform, audio alignment and navigation, with musical structure and move editing; (2) a wrapped musical-grid view for choreography editing and reading, based on the same project data. The choreography sheet is derived from this data. Avoid duplicating business rules in two view implementations.

**S-023 — Shared editing context [V1 required].** Playback cursor and selected move/region are shared across both views; switching views navigates to the relevant location. Each view may retain its own zoom/display settings. Simultaneous split-screen is deferred.

**S-024 — Undo/redo [V1 required].** Shared undo/redo across both views, with `Ctrl+Z` and `Ctrl+Shift+Z`. Include region/move creation/deletion, timing edits, labels and resizing. A drag is one undoable action. Visible history panel not required.

**S-026 — Platforms [V1 required].** Develop/test V1 on Linux. Preserve cross-platform architecture where practical, avoiding unnecessary Linux-specific dependencies. Windows/macOS builds and release validation are not required for V1.

## 3. Display A — Non-binding UX reference

The user supplied [`display-a.xlsx`](../references/display-a.xlsx) as an illustrative **possible display**, not an approved rendering. The concept is a wrapped, vertically progressing choreography sheet, with rows for musical sections and cells for phrases/counts, potentially allowing shorter sections to be centered visually. It may be more readable to dancers than a continuously scrolling DAW-style timeline. It is a candidate for the musical-grid editing view and choreography-sheet export; usability and rendering must be tested. **No exact spreadsheet geometry, styling or cell dimensions are binding.** The uploaded reference should be retained alongside this checkpoint for later UX work.

## 4. V1 delivery guardrails

1. Prefer a usable end-to-end authoring-to-sheet workflow over feature breadth.
2. Features explicitly marked *conditional* may be omitted from V1 when implementation complexity is disproportionate; omission should be documented, not silently reinterpreted.
3. The musical structure is authoritative; choreography tracks are independent and refer to musical beat positions.
4. Do not assume media starts on beat one or at time zero; future independent video clips need their own offsets and time mappings.
5. Do not confuse the read-oriented choreography sheet, the two editing views, and the portable native project format.
6. UI illustrations are exploratory until tested and approved.

## 5. Explicitly deferred capabilities

- Automatic song structure, beat or transient detection.
- Variable/fluid tempo mapping with multiple anchors or interpolation.
- Reusable musical templates and linked repeated patterns.
- Move library, structured move taxonomy, training videos, stitched move-video playback.
- Independent performance-video overlay, clip alignment and tempo scaling.
- Sophisticated page-layout controls; normalized Excel data export.
- Advanced audio editing, metronome, count-in, time stretch/pitch preservation.
- Split-screen simultaneous editing and visible undo history.
- Windows/macOS V1 packaging and validation.

## 6. Open decisions and design risks

- **Framework selection:** assess real PySide6/Qt vs Tauri/web timeline, waveform and wrapped-grid components against delivery criteria (S-002).
- **Sheet UX:** test Display A against real multi-track, cross-boundary and variable-length examples; determine printing/pagination behavior.
- **Anchor semantics:** how users specify the musical distance between anchor and calibration point; how count labels work before the anchor.
- **Structure generator semantics:** whether `AABA` generates four sections, each with configurable phrases, and what defaults apply; avoid conflating 4×8 with four 8-count sections.
- **Move prepopulation:** how a chosen count interval interacts with irregular regions and song endings; whether/how multiple tracks are populated.
- **Overlapping moves on the same track:** not explicitly decided; S-009 only commits to overlap across different tracks.
- **Ripple edge cases:** insert/delete crossing move boundaries, anchoring, and effects on musical time-to-audio mapping.
- **Sheet/PDF/Excel parity:** define essential information and readable handling of spanning moves and long notes.
- **Native file internals:** project schema, versioning/migration policy, audio storage, autosave snapshot lifecycle.
- **Platform/packaging:** Linux distribution targets and application delivery.
- **Acceptance tests and release milestones:** not yet specified; important given the breadth of V1.

## 7. Interview continuation

**Last locked decision:** S-030 — repeated musical sections are independent; duplication with subdivisions is supported.

**Next:** S-031, to be chosen during the continuing interview. Candidate topics: handling same-track overlap, choreography-sheet pagination/visibility, or default structure/count behaviors. Continue one focused A/B/C/D decision at a time, provide a recommendation, then explicitly lock the user's answer.

## 8. Handoff boundary

When spec'ing is complete, produce a **separate**, authoritative `handoff_YYMMDD_i.md` containing at least:

- General description/context
- Non-goals / Do Not Touch
- Specs (`S-…`)
- Implementation (`I-…`)
- Tests (`T-…`)
- Definition of Done (`DoD-…`)

Execution agent must follow that handoff only, stop on ambiguity, and not invent requirements. Future changes require a new handoff. This checkpoint alone does not authorize implementation.

## 9. Revision log

- **2026-10-11 / checkpoint 01:** Consolidated S-001–S-030. Incorporated amendments to S-004 (direct BPM entry), S-012 (count-based move prepopulation), S-017 (Excel output), and interaction between S-013 and S-028. Recorded Display A as a non-binding UX reference and preserved S-002 as an unresolved framework selection.
