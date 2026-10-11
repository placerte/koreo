# Koreo — ChatGPT Specification Interview Archive

> Historical background only. This transcript is not an execution contract and
> does not override `docs/handoffs/handoff_261011_1.md` or other authoritative
> repository artifacts.

## Provenance

- Source: https://chatgpt.com/share/6acbe357-e774-83ea-9c7d-eb0cb057c686
- Shared-conversation ID: `6acbe357-e774-83ea-9c7d-eb0cb057c686`
- Backing-conversation ID: `6acba944-6640-83ea-a79a-4aef5235a8c2`
- Title: Conduct Spec Interview
- Retrieved: 2026-10-11T19:39:09+00:00
- Current node: `d7c43759-bb3f-4500-9aa9-94ac4797d6d1`
- Source chain: 368 nodes
- Archived visible turns: 200 (100 user, 100 assistant)
- Companion JSON SHA-256: `47898d64ea36355f0e705619c5f56c91622421a6945c750dbc42eec298b3e551`

The archive contains every browser-visible user and assistant text turn on the
shared conversation's current branch. It excludes hidden system context, tool
traffic, rendering intermediates, empty reasoning containers, and platform
bootstrap data.

## Referenced artifacts

- `docs/references/display-a.xlsx` — Non-binding UX reference uploaded during the interview (present locally).
- `docs/specifications/koreo_specs_v1.md` — Specification checkpoint covering S-001 through S-030 (present locally).
- `koreo_specs_v2.md` — Specification checkpoint covering S-001 through S-075 (not present locally).
- `docs/handoffs/handoff_261011_1.md` — Authoritative Milestone 1 execution handoff (present locally).

## Transcript

### Turn 001 — User

<!-- node_id: 715a905a-8651-4928-8877-b9bc394094ee message_id: 715a905a-8651-4928-8877-b9bc394094ee -->

Look into your project instructions. We hav to conduct the specing interview

### Turn 002 — Assistant

<!-- node_id: 63cd8eea-b009-4228-99ca-a8169ab2cdbd message_id: 63cd8eea-b009-4228-99ca-a8169ab2cdbd -->

## Koreo — Spec’ing Interview

We're now explicitly transitioning from **Thinking / Exploration** to **Spec’ing / Designing (Phase 3)**.

I'll act as the design authority and conduct the interview according to the project instructions.

Our process will be:

1. **One decision at a time**, with focused A/B/C/D options.
2. I'll explain the trade-offs and give my recommendation.
3. You'll select an option, modify it, or challenge the assumptions.
4. We'll **lock the decision** and move to the next question.
5. At the end, we'll consolidate the decisions into an authoritative specification, ready for handoff generation.

No implementation or code during this phase.

### Interview roadmap

We'll cover the following areas:

| Area | Decisions |
|---|---|
| 1. Product scope | Core workflow, MVP boundaries |
| 2. Interface | Web, desktop, CLI; interaction model |
| 3. Musical timeline | Time, beats, tempo, grid |
| 4. Structure | Sections, phrases, counts, subdivisions |
| 5. Annotations | Moves, notes, repeated patterns |
| 6. Audio | Playback, formats, synchronization |
| 7. Persistence | Project format, saving, loading |
| 8. Validation | Acceptance tests, definition of done |

We'll distinguish between **product requirements** and **implementation decisions**, avoiding unnecessary technical commitments.

---

## Question 1 — Primary interface

For the initial Koreo proof of concept, which interface should we target?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">**A. Native desktop application**

      <text color="secondary" size="sm">Dedicated window, local audio and filesystem access. More platform-specific implementation.</text>
    </radio>
    <radio value="B">**B. Local web application (recommended)**

      <text color="secondary" size="sm">Browser-based graphical editor, local development server, straightforward interactive timeline.</text>
    </radio>
    <radio value="C">**C. Browser-only application**

      <text color="secondary" size="sm">Runs entirely in the browser without a backend server. Local audio and project files handled by browser APIs.</text>
    </radio>
    <radio value="D">**D. CLI / TUI**

      <text color="secondary" size="sm">Lightweight and easy to automate, but less suitable for visual choreography planning.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 1, I choose "+choice+".")} >Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

**My recommendation: B**, initially. A local web app offers a good balance between a visual timeline, interactive editing, audio playback, and development simplicity.

However, **C** is also worth considering seriously: Koreo's initial requirements may not justify running a backend at all.

Your choice is provisional until you confirm it. We'll then lock S-001 and proceed to the next question.

### Turn 003 — User

<!-- node_id: b136adbe-2d18-4cac-9563-84ee7f4d4b14 message_id: b136adbe-2d18-4cac-9563-84ee7f4d4b14 -->

I'd say A or B but if we can branch off or reuse a simple but effective package let's do that

### Turn 004 — Assistant

<!-- node_id: c397000c-f98d-4f78-b4d0-7b75cb3ecaea message_id: c397000c-f98d-4f78-b4d0-7b75cb3ecaea -->

_[No textual content in source node.]_

### Turn 005 — User

<!-- node_id: 79b2bb84-f31a-471e-a9e6-a95662da6836 message_id: 79b2bb84-f31a-471e-a9e6-a95662da6836 -->

For Koreo spec'ing question 1, I choose A.

### Turn 006 — Assistant

<!-- node_id: b79a8131-ba13-42f6-847a-d76bf11add3f message_id: b79a8131-ba13-42f6-847a-d76bf11add3f -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-001 — Locked</badge>

**Primary interface: Native desktop application (Option A).**

Koreo will initially target a desktop application, with the following considerations:

- A graphical, interactive choreography editor.
- Local audio playback and file access.
- Preference for reusing an existing, lightweight, proven UI or timeline component rather than building everything from scratch.
- No commitment yet to a particular programming language, framework, or library.

The desktop decision does not exclude using web technologies inside a desktop shell.

---

## Question 2 — Desktop technology strategy

Given your preference for reusing existing packages, we should decide how much of the application should be native.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Python + Qt (PySide6)**

      <text color="secondary" size="sm">Native desktop widgets, mature graphics framework, Python ecosystem. Timeline interaction would require some custom work.</text>
    </radio>
    <radio value="B">
      **B. Tauri + web frontend (recommended)**

      <text color="secondary" size="sm">Lightweight desktop shell with access to web-based timeline, waveform, and grid libraries. Requires some web development and Rust tooling.</text>
    </radio>
    <radio value="C">
      **C. Electron + web frontend**

      <text color="secondary" size="sm">Mature ecosystem with many existing components, but larger memory and application footprint.</text>
    </radio>
    <radio value="D">
      **D. Defer framework selection**

      <text color="secondary" size="sm">Specify the editing interactions first, then evaluate existing components against those requirements.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 2, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

**My recommendation is B, provisionally.** A web-based timeline inside a desktop application could provide the most reusable components.

However, given your emphasis on finding an existing package rather than reinventing an editor, **D is arguably the more disciplined engineering approach**. We could define the required timeline interactions first, then compare libraries before committing to a framework.

Which direction would you prefer?

### Turn 007 — User

<!-- node_id: 64540d26-f305-4317-8b07-079631772a50 message_id: 64540d26-f305-4317-8b07-079631772a50 -->

I prefer A because this is the technology I know, but we should be delivry focussed. If Tauri has a better ecosystem for this type of application let's use that

### Turn 008 — Assistant

<!-- node_id: ee628e76-3616-4378-a40f-51921c4de3a2 message_id: ee628e76-3616-4378-a40f-51921c4de3a2 -->

That makes sense. We should optimize for **the shortest path to a functional Koreo**, not for a particular technology.

I suggest we **do not lock the framework yet**.

### S-002 — Technology strategy (provisionally locked)

**Decision:** Python + PySide6 is the preferred baseline, but Tauri remains a candidate if its ecosystem offers a meaningful development advantage.

Our selection criteria, in priority order:

1. Availability of reusable timeline, waveform, and grid components.
2. Speed of implementation and ease of maintenance.
3. Quality of interactive editing (dragging, resizing, zooming, snapping).
4. Familiarity with the technology.
5. Application footprint and packaging.

One important distinction: Tauri itself doesn't provide a choreography timeline. Its potential advantage comes from access to JavaScript libraries. Qt, meanwhile, offers mature graphics primitives through `QGraphicsView` and `QGraphicsScene`.

We should evaluate actual component candidates before choosing.

---

## Question 3 — Timeline interaction model

This is more important than the framework choice because it determines what kind of existing editor or component we can reuse.

Which model best represents how you imagine Koreo?

<box gap={3}>
  <row align="start" gap={3}>
    <box width="132px">
      <svg viewBox="0 0 160 96" width="100%">
        {#each [0,1,2,3,4,5,6,7] as i}
          <rect x={i*19+4} y="12" width="17" height="16" rx="2" fill={i<4?"#8BAFC7":"#A5B5A1"}/>
          <rect x={i*19+4} y="32" width="17" height="16" rx="2" fill="#C9B69C"/>
          <rect x={i*19+4} y="52" width="17" height="28" rx="2" stroke="currentColor" strokeOpacity=".3" fill="none"/>
        {/each}
      </svg>
    </box>
    <box flex="1" gap={1}>
      **A. Spreadsheet-like grid**

      Fixed cells representing counts or beats. Users merge, subdivide, and annotate cells.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box width="132px">
      <svg viewBox="0 0 160 96" width="100%">
        <rect x="3" y="10" width="154" height="18" rx="3" fill="#829FAF"/>
        <rect x="3" y="35" width="75" height="20" rx="3" fill="#91A9C1"/>
        <rect x="80" y="35" width="77" height="20" rx="3" fill="#B5A3C8"/>
        <rect x="3" y="61" width="34" height="22" rx="3" fill="#9BAD9B"/>
        <rect x="39" y="61" width="76" height="22" rx="3" fill="#C2A989"/>
        <rect x="117" y="61" width="40" height="22" rx="3" fill="#9BAD9B"/>
      </svg>
    </box>
    <box flex="1" gap={1}>
      **B. DAW-style timeline**

      Horizontal tracks with movable, resizable regions, similar to audio and video editing software.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" gap={3}>
    <box width="132px">
      <svg viewBox="0 0 160 96" width="100%">
        <rect x="3" y="8" width="154" height="16" rx="2" fill="#829FAF"/>
        <rect x="3" y="29" width="154" height="19" rx="2" fill="#91A9C1"/>
        {#each [0,1,2,3] as i}
          <rect x={3+i*39} y="53" width="37" height="15" rx="2" fill="#C2A989"/>
        {/each}
        {#each [0,1,2,3,4,5,6,7] as i}
          <rect x={3+i*19.5} y="72" width="17.5" height="15" rx="2" fill="#9BAD9B"/>
        {/each}
      </svg>
    </box>
    <box flex="1" gap={1}>
      **C. Hierarchical musical grid (recommended)**

      Song sections contain phrases, phrases contain counts, and counts can be subdivided into individual moves.
    </box>
  </row>
</box>

**I recommend C**, since Koreo's primary purpose is describing musical and choreographic structure rather than editing audio clips. We could still use DAW-like interactions such as zooming, dragging, and snapping.

Would you choose **A, B, C, or a hybrid**?

### Turn 009 — User

<!-- node_id: cadfc14c-088c-4d0a-b067-cc529c5c8475 message_id: cadfc14c-088c-4d0a-b067-cc529c5c8475 -->

I think they could all be interchangeable... I think for the first version, C is fine but at some later version we might want to superpose a video. This videofile might not start exactly "on the one" (almost impossible in fact) so the user might have to identfy the one (or even a couple of bars) in order to scale the video tempo (say it was not done on the music in the video) etc... In that case I imagine a DAW style cells where a video could overflow the song grid etc

### Turn 010 — Assistant

<!-- node_id: fc052250-626e-46f5-804c-a998057b2b7f message_id: fc052250-626e-46f5-804c-a998057b2b7f -->

That's an important distinction. I think we should separate the **underlying timeline model** from how it is displayed.

Your video example illustrates why a purely hierarchical data model could become restrictive.

## S-003 — Timeline model

<badge color="success"><icon name="check" inline/> Locked</badge>

**Decision: Hierarchical musical grid for V1, built on a timeline model that can eventually accommodate independent media tracks.**

The key distinction:

- **Musical grid:** Sections, phrases, bars, beats, subdivisions. This is how the user organizes choreography.
- **Media tracks:** Audio and, eventually, video clips with their own positions, offsets, and playback rates.
- **Presentation:** A hierarchical grid in V1, potentially a DAW-style multi-track editor later.

For example, a future video might start 2.3 seconds before the first beat of the song. The user could identify corresponding beats in the video and song to establish synchronization, including tempo adjustment.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium" size="xs" color="secondary">CONCEPTUAL FUTURE TIMELINE</text>
  <svg viewBox="0 0 340 146" width="100%">
    <g fontSize="10" fill="currentColor">
      <text x="3" y="19">Video</text>
      <text x="3" y="59">Audio</text>
      <text x="3" y="99">Grid</text>
    </g>
    <g transform="translate(50 0)">
      {#each [0,1,2,3,4,5] as i}
        <line x1={i*48} y1="7" x2={i*48} y2="124" stroke="currentColor" strokeOpacity=".14" strokeDasharray="3 3"/>
      {/each}
      <rect x="0" y="26" width="195" height="19" rx="3" fill="#A69BCB"/>
      <text x="8" y="39" fontSize="10" fill="#1C1730">Video clip</text>
      <rect x="32" y="66" width="235" height="19" rx="3" fill="#7FA9C1"/>
      <text x="42" y="79" fontSize="10" fill="#122532">Song</text>
      {#each [0,1,2,3] as i}
        <rect x={32+i*58.75} y="105" width="57" height="18" rx="2" fill={i===2?"#C2A989":"#9DB69B"}/>
        <text x={50+i*58.75} y="117" fontSize="10" fill="#172719">{["A","A","B","A"][i]}</text>
      {/each}
      <line x1="32" y1="12" x2="32" y2="127" stroke="#D98A52" strokeWidth="1.7"/>
      <text x="36" y="10" fontSize="9" fill="#D98A52">Beat 1</text>
    </g>
  </svg>
  <caption>Illustrative only: the video and song occupy independent time ranges, while the choreography grid follows the musical structure.</caption>
</box>

We should avoid committing to video synchronization mechanics in V1, but ensure the architecture doesn't assume that every media item starts at beat 1.

---

## Question 4 — How should the musical grid be established?

Before describing sections or choreography, the application needs to know where the beats are.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Manual BPM + starting offset**

      <text color="secondary" size="sm">User enters a BPM and identifies the first beat. The grid is generated at constant tempo.</text>
    </radio>
    <radio value="B">
      **B. Manual BPM + visual/audio alignment (recommended)**

      <text color="secondary" size="sm">Same as A, but users can drag the grid relative to the waveform and adjust BPM while listening.</text>
    </radio>
    <radio value="C">
      **C. Tap tempo and beat markers**

      <text color="secondary" size="sm">User taps along with the music or places several reference beats, allowing more flexible alignment.</text>
    </radio>
    <radio value="D">
      **D. Variable tempo grid**

      <text color="secondary" size="sm">User defines multiple tempo regions or beat anchors, accommodating recordings with tempo drift.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 4, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. It provides a useful visual workflow without requiring complex tempo mapping.

One architectural consideration: we should probably distinguish the **musical position** (beat/count) from the **media time** (seconds). This will be useful for video synchronization later.

Would B be sufficient for your first proof of concept?

### Turn 011 — User

<!-- node_id: 70ed43e8-59f7-4c40-899d-1d6f551987cd message_id: 70ed43e8-59f7-4c40-899d-1d6f551987cd -->

What I am thinking is this work flow. You play the song and have a BPM tool modal or something. We can tap the spacebar. the more time we use the tool the more precise the computed BPM is. Then we identify one anchor. Most of the time the first "one" will be the anchor, but if is fuzzy or not clear it could be "any one". Fine tuning  could be done by adjusting "another one" / the grid much later in the song. if we call the anchor "the anchor" this second key should be called something else... "hook"? this could correct some tempo drift caused either by a bad BPM of the song (not constnt) or even a not so good initial guess. (say i tapped 120 BPM but it is actually 118.76 BPM. Scaling two "far away ones" is a great way to get precision on the grid

### Turn 012 — Assistant

<!-- node_id: 87bc6450-5dbe-4420-aea5-a680c6808890 message_id: 87bc6450-5dbe-4420-aea5-a680c6808890 -->

I like this approach. You're essentially describing a **two-point tempo calibration system**, with tap tempo providing the initial estimate.

Importantly, this means we don't need particularly accurate tapping. We just need a reasonable starting BPM, then use two widely separated musical references to calibrate it.

## S-004 — Beat grid calibration

<badge color="success"><icon name="check" inline/> Concept agreed</badge>

The proposed workflow:

1. **Tap tempo:** Play the song and tap the spacebar. The BPM estimate improves as more taps are collected.
2. **Set primary anchor:** Identify any musical *one* (first beat of a bar or phrase), not necessarily the first one in the recording.
3. **Generate grid:** Create a constant-tempo beat grid extending both before and after the anchor.
4. **Set second reference:** Identify another *one* much later in the song, with its musical distance from the primary anchor known.
5. **Calibrate:** Adjust the grid's BPM so both references align.

### Why the second reference works

Suppose the two references are 64 bars apart, in 4/4.

<box border radius="lg" padding={3} gap={2}>
  <grid columns={2} gap={3}>
    <grid-item>
      <text color="secondary" weight="medium" size="xs">Initial tapped BPM</text>
      <title size="xl" color="default" tabularNums>120.00</title>
    </grid-item>
    <grid-item>
      <text color="secondary" weight="medium" size="xs">Actual average BPM</text>
      <title size="xl" color="default" tabularNums>118.76</title>
    </grid-item>
  </grid>
  <text color="secondary" size="sm">After 64 bars (256 beats), the original estimate is off by approximately 1.34 seconds.</text>
  <svg viewBox="0 0 320 92" width="100%">
    <line x1="18" y1="18" x2="300" y2="18" stroke="currentColor" strokeOpacity=".2"/>
    <line x1="18" y1="48" x2="300" y2="48" stroke="currentColor" strokeOpacity=".2"/>
    <circle cx="18" cy="18" r="4" fill="#7FA9C1"/>
    <circle cx="18" cy="48" r="4" fill="#7FA9C1"/>
    <circle cx="268" cy="18" r="4" fill="#7FA9C1"/>
    <circle cx="291" cy="48" r="4" fill="#C18B60"/>
    <path d="M268 26 L291 40" stroke="#C18B60" strokeDasharray="3 3"/>
    <g fill="currentColor" fontSize="10">
      <text x="18" y="9">Anchor</text>
      <text x="211" y="9">Initial grid</text>
      <text x="203" y="64">Actual beat</text>
      <text x="18" y="82">0 beats</text>
      <text x="256" y="82">256 beats</text>
    </g>
  </svg>
  <caption>Schematic: a small BPM error accumulates into a noticeable timing offset.</caption>
</box>

The calibrated BPM is simply:

\[
\mathrm{BPM}=\frac{60\Delta N}{t_2-t_1}
\]

where \(\Delta N\) is the number of beats between the references.

### Naming

I suggest:

- **Anchor:** The primary reference defining the grid's musical origin.
- **Calibration point:** A secondary reference used to refine the tempo.

I prefer *calibration point* over *hook*, because hook already has a musical meaning.

There's also an important distinction: two points can correct a bad BPM estimate or establish an average tempo, but they cannot correct **nonuniform tempo drift** throughout a recording. That would eventually require multiple calibration points and a variable-tempo grid.

---

## Question 5 — What should happen when we add more calibration points?

This determines whether we build a constant-tempo or variable-tempo system initially.

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. One anchor + one calibration point (recommended for V1)**

      <text color="secondary" size="sm">Two references define one globally constant BPM. Simple and precise for most electronically timed recordings.</text>
    </radio>
    <radio value="B">
      **B. Multiple calibration points with piecewise tempo**

      <text color="secondary" size="sm">Each pair of consecutive points defines its own average BPM. Accommodates tempo changes, but adds complexity.</text>
    </radio>
    <radio value="C">
      **C. Multiple points with smooth tempo interpolation**

      <text color="secondary" size="sm">Tempo changes continuously between calibration points. Better suited to expressive live recordings, but considerably more complex.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 5, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

My recommendation is **A for V1**, while preserving the possibility of B later.

One detail we should address afterward: how the user tells Koreo *which* musical one the calibration point represents, so we don't accidentally align it to the wrong bar.

### Turn 013 — User

<!-- node_id: 516968cd-9d73-4366-b2fc-bd2d8463b076 message_id: 516968cd-9d73-4366-b2fc-bd2d8463b076 -->

Yes just A for v1. We will leave "fluid tempo grids" for another release. Also for S-004. If the user "knows" the tempo no need to force the BPM tap tool on him. It should also have the option to just input a tempo.

### Turn 014 — Assistant

<!-- node_id: 113d6eec-ae52-4f4a-9889-ea22e9b03caa message_id: 113d6eec-ae52-4f4a-9889-ea22e9b03caa -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-004 and S-005 — Locked</badge>

### S-004 — BPM estimation and grid calibration

The user can establish the initial BPM using either method:

- **Manual entry:** Directly enter a known BPM.
- **Tap tempo:** Play the song and tap the spacebar to estimate BPM from successive taps. The estimate can improve as more taps are collected.

Both methods lead to the same calibration workflow:

1. Identify a primary **anchor** at any musical *one*.
2. Generate a constant-tempo grid using the initial BPM.
3. Optionally identify a second, distant **calibration point**.
4. Refine the BPM using the elapsed time and known number of beats between the two references.

The calibration point is optional. The user can work with the initial BPM and anchor alone.

### S-005 — Tempo model

**V1:** One globally constant BPM, with at most one anchor and one secondary calibration point.

**Deferred:** Multiple calibration points, variable tempo, fluid tempo grids, and interpolation.

---

## Question 6 — Musical hierarchy

Now that we can generate a beat grid, we need to decide how choreography is organized on it.

For example, a swing song might have an introduction, then sections following `A A B A`, with each A containing four 8-count phrases.

The important design question is whether that hierarchy should be **fixed or freely configurable**.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Fixed hierarchy**

      <text color="secondary" size="sm">Song → Section → Phrase → Count → Move. Predictable and simple, but less flexible.</text>
    </radio>
    <radio value="B">
      **B. Flexible hierarchical regions (recommended)**

      <text color="secondary" size="sm">Users can subdivide regions recursively, label them, and organize choreography at whatever level is useful. A default hierarchy can still be provided.</text>
    </radio>
    <radio value="C">
      **C. Independent annotation layers**

      <text color="secondary" size="sm">Sections, phrases, and moves occupy separate timeline tracks. Regions may overlap, like in a DAW, without necessarily belonging to one another.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 6, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** for V1. It fits the idea of starting with an `A A B A` structure, subdividing an A into phrases, then subdividing a phrase into individual moves, without imposing a rigid number of levels.

We can treat independent tracks and overlapping annotations as a separate future capability.

### Turn 015 — User

<!-- node_id: 16a86695-6b3f-45e6-830a-44259f3896aa message_id: 16a86695-6b3f-45e6-830a-44259f3896aa -->

yes B and we could propose (in the future) templates like 4x8 AABA, 6x8 "boogie" etc..

### Turn 016 — Assistant

<!-- node_id: 7de5f841-b485-4abc-a233-b63a95973e9f message_id: 7de5f841-b485-4abc-a233-b63a95973e9f -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-006 — Locked</badge>

**Decision: Flexible hierarchical regions.**

- Regions can be subdivided recursively, without a fixed number of levels.
- Each region can have its own label and annotations.
- Subdivisions remain aligned with the underlying musical grid.
- The user can work at the song, section, phrase, count, or individual-move level.

**Future feature — Structure templates:** Reusable presets such as `4×8 AABA`, `6×8 Boogie`, or user-defined patterns. These are explicitly outside V1, but the region model should not prevent their introduction.

---

## Question 7 — How should subdivision work?

Suppose the user creates a region spanning 32 counts. They want to subdivide it to plan choreography.

<box border radius="lg" padding={3} gap={2}>
  <text color="secondary" weight="medium" size="xs">EXAMPLE — 32-COUNT REGION</text>
  <svg viewBox="0 0 320 87" width="100%">
    <rect x="2" y="4" width="316" height="28" rx="4" fill="#819FB9"/>
    <text x="160" y="22" fontSize="12" textAnchor="middle" fill="#142B3B">Section A — 32 counts</text>
    {#each [0,1,2,3] as i}
      <rect x={2+i*79} y="39" width="77" height="27" rx="3" fill={i%2===0?"#A2B9A0":"#C6B18E"}/>
      <text x={40+i*79} y="56" fontSize="11" textAnchor="middle" fill="#24332A">8 counts</text>
    {/each}
    <g fill="currentColor" fontSize="9" opacity=".7">
      <text x="2" y="82">1</text>
      <text x="80" y="82">9</text>
      <text x="158" y="82">17</text>
      <text x="237" y="82">25</text>
      <text x="304" y="82">32</text>
    </g>
  </svg>
</box>

{@body const [choice,setChoice] = DIL.useState("C")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Equal subdivision only**

      <text color="secondary" size="sm">Split a region into 2, 4, 8, etc. equal parts. Very simple but restrictive.</text>
    </radio>
    <radio value="B">
      **B. Arbitrary subdivision**

      <text color="secondary" size="sm">Place boundaries at any beat or count, allowing unequal regions such as 8 + 8 + 4 + 12.</text>
    </radio>
    <radio value="C">
      **C. Equal subdivision + manual adjustment (recommended)**

      <text color="secondary" size="sm">Quickly divide a region into equal parts, then drag boundaries or specify count positions to customize them.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 7, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **C** because equal subdivision is probably the most common operation, while manual adjustment accommodates irregular musical structures.

One consequence we'll address later is whether subdividing a region should preserve the parent region as a visible container, or replace it with its children.

### Turn 017 — User

<!-- node_id: d11543c1-547b-49f1-a693-de31585c1438 message_id: d11543c1-547b-49f1-a693-de31585c1438 -->

yes C. We could have moves (counts) bleeding in or out of the strcuture for instance

### Turn 018 — Assistant

<!-- node_id: cab0b706-2097-40b1-9b07-64ff1fd1556d message_id: cab0b706-2097-40b1-9b07-64ff1fd1556d -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-007 — Locked</badge>

**Decision: Equal subdivision with manual adjustment.**

- Divide a region into equal parts (2, 4, 8, etc.).
- Adjust boundaries manually to create unequal subdivisions.
- Snap boundaries to the musical grid.

Your observation about moves bleeding across structural boundaries introduces an important distinction:

**Musical structure and choreography do not necessarily share the same boundaries.**

For example, a move might begin on count 7 of one phrase and finish on count 2 of the next.

<box border radius="lg" padding={3} gap={2}>
  <text color="secondary" weight="medium" size="xs">ILLUSTRATIVE TIMELINE</text>
  <svg viewBox="0 0 330 116" width="100%">
    <g fontSize="11" fill="currentColor">
      <text x="3" y="19">Structure</text>
      <text x="3" y="71">Moves</text>
    </g>
    <g transform="translate(70 0)">
      <rect x="0" y="7" width="126" height="26" rx="3" fill="#8BAFC7"/>
      <rect x="128" y="7" width="126" height="26" rx="3" fill="#A5B99C"/>
      <text x="63" y="24" fontSize="11" textAnchor="middle" fill="#172C3B">Phrase 1</text>
      <text x="191" y="24" fontSize="11" textAnchor="middle" fill="#203224">Phrase 2</text>
      {#each Array.from({length:17},(_,i)=>i) as i}
        <line x1={i*15.875} y1="38" x2={i*15.875} y2="97" stroke="currentColor" strokeOpacity={i===8?".55":".13"} strokeWidth={i===8?1.5:1}/>
      {/each}
      <rect x="96" y="60" width="65" height="24" rx="4" fill="#C5A07A"/>
      <text x="128" y="76" textAnchor="middle" fontSize="10" fill="#302113">Move X</text>
      <g fontSize="9" fill="currentColor" opacity=".75">
        <text x="0" y="109">1</text>
        <text x="126" y="109">1</text>
        <text x="246" y="109">8</text>
      </g>
    </g>
  </svg>
  <caption>Move X crosses the boundary between two musical phrases without changing the structure.</caption>
</box>

This suggests that **structural regions are hierarchical**, while **moves may need independent timing**.

I wouldn't lock the move model yet. We should resolve that explicitly.

---

## Question 8 — How should moves relate to the structure?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Moves belong to structural regions**

      <text color="secondary" size="sm">A move is attached to a phrase or count, but may extend beyond its parent's boundaries. Simpler organizational model.</text>
    </radio>
    <radio value="B">
      **B. Moves occupy an independent choreography track (recommended)**

      <text color="secondary" size="sm">Moves have their own start and end positions on the musical timeline. They can cross any structural boundary without special handling.</text>
    </radio>
    <radio value="C">
      **C. Both models**

      <text color="secondary" size="sm">Moves have independent timing and can also belong to structural regions. More expressive, but requires rules for ownership and editing.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 8, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

**I recommend B for V1.** It keeps musical analysis separate from choreography planning and accommodates overlapping phrases, anticipations, and moves extending beyond a section.

It also moves us naturally toward the DAW-style presentation you mentioned earlier, without requiring video support in V1.

### Turn 019 — User

<!-- node_id: 9328802f-8a14-43f5-ba8a-2b9cacde1ff8 message_id: 9328802f-8a14-43f5-ba8a-2b9cacde1ff8 -->

For Koreo spec'ing question 8, I choose B.

### Turn 020 — Assistant

<!-- node_id: a7e85fec-8fb2-4d9e-bc81-2bcfc15a4cc5 message_id: a7e85fec-8fb2-4d9e-bc81-2bcfc15a4cc5 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-008 — Locked</badge>

**Decision: Moves occupy an independent choreography track.**

- Moves have their own start and end positions on the musical timeline.
- Moves can cross structural boundaries freely.
- Editing the musical structure does not automatically alter the timing of moves.
- Moves can be aligned to beats, counts, or subdivisions.
- The structural hierarchy and choreography track share the same underlying musical grid.

This establishes two complementary layers: **musical structure** and **choreography**.

---

## Question 9 — How should overlapping moves work?

Imagine a dancer performing a footwork pattern while simultaneously executing an arm movement. Both may need to be documented over the same counts.

Should Koreo support this in V1?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Single choreography lane**

      <text color="secondary" size="sm">Moves appear sequentially on one track. A move cannot overlap another move.</text>
    </radio>
    <radio value="B">
      **B. Multiple independent lanes (recommended)**

      <text color="secondary" size="sm">Users can create lanes for footwork, arms, partner movements, or other purposes. Moves on different lanes can overlap.</text>
    </radio>
    <radio value="C">
      **C. Free overlapping moves**

      <text color="secondary" size="sm">Moves can overlap within a single track. Koreo automatically arranges them visually to avoid collisions.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 9, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I lean toward **B**, because independent lanes would also be useful for documenting multiple dancers or partners later.

However, A would be simpler for the first proof of concept. We should only choose B if simultaneous moves are important to your initial workflow.

### Turn 021 — User

<!-- node_id: fbc62fe7-048d-4b0f-bf6a-ef5e207a24b8 message_id: fbc62fe7-048d-4b0f-bf6a-ef5e207a24b8 -->

Yes B and the other idea is that if we build a choregraphy for multiple couples we could have couples A and B do one thing and couples C and D do something else. Default project should have only one "move track" but having multiple should be possible

### Turn 022 — Assistant

<!-- node_id: b9528fae-c64e-43a5-84ad-8d640a87a753 message_id: b9528fae-c64e-43a5-84ad-8d640a87a753 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-009 — Locked</badge>

**Decision: Multiple independent choreography tracks, with one track by default.**

- A new project starts with a single move track.
- Users can add, rename, and remove tracks.
- Each track contains independently timed moves.
- Moves on different tracks may overlap freely.
- Tracks may represent individual dancers, couples, groups, or movement categories (footwork, arms, etc.).
- Tracks share the same musical grid and playback timeline.

For example:

<box border radius="lg" padding={3} gap={2}>
  <text color="secondary" weight="medium" size="xs">MULTI-COUPLE CHOREOGRAPHY</text>
  <svg viewBox="0 0 340 125" width="100%">
    <g fontSize="10" fill="currentColor">
      <text x="2" y="17">Counts</text>
      <text x="2" y="46">Couples A+B</text>
      <text x="2" y="82">Couples C+D</text>
    </g>
    <g transform="translate(88 0)">
      {#each [0,1,2,3,4,5,6,7] as i}
        <text x={i*30+14} y="17" textAnchor="middle" fontSize="10" fill="currentColor">{i+1}</text>
        <line x1={i*30} y1="24" x2={i*30} y2="110" stroke="currentColor" strokeOpacity=".12"/>
      {/each}
      <rect x="0" y="30" width="118" height="26" rx="3" fill="#8CAFC5"/>
      <rect x="120" y="30" width="118" height="26" rx="3" fill="#A5B99C"/>
      <text x="59" y="47" fontSize="10" fill="#172B3B" textAnchor="middle">Move X</text>
      <text x="179" y="47" fontSize="10" fill="#1C3222" textAnchor="middle">Move Y</text>
      <rect x="0" y="66" width="58" height="26" rx="3" fill="#C6B18E"/>
      <rect x="60" y="66" width="178" height="26" rx="3" fill="#B4A4C9"/>
      <text x="29" y="83" fontSize="10" fill="#322719" textAnchor="middle">Turn</text>
      <text x="149" y="83" fontSize="10" fill="#2A2039" textAnchor="middle">Travel / Formation</text>
    </g>
  </svg>
  <caption>Both groups follow the same counts while executing different choreography.</caption>
</box>

This also reinforces our earlier architectural decision: **tracks should be independent of the musical hierarchy**.

---

## Question 10 — What information does a move contain?

We need to establish the minimum useful representation of a move in V1.

All options assume that a move already has a start position, end position, and associated track.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Text label only**

      <text color="secondary" size="sm">Each move is a timed block containing a short name or description, such as "Swing out" or "Triple step".</text>
    </radio>
    <radio value="B">
      **B. Label + optional detailed notes (recommended)**

      <text color="secondary" size="sm">A short label appears directly on the timeline. Selecting a move reveals a larger text field for instructions, cues, or additional details.</text>
    </radio>
    <radio value="C">
      **C. Structured move properties**

      <text color="secondary" size="sm">In addition to text, moves have predefined properties such as category, dancer assignment, difficulty, direction, and tags.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 10, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

**I recommend B for V1.** It provides enough detail to document choreography without requiring us to design a move taxonomy or library prematurely.

A reusable move library, video demonstrations, and structured move metadata can remain future enhancements.

### Turn 023 — User

<!-- node_id: b340c71f-4412-4f61-bf61-4035d61a233f message_id: b340c71f-4412-4f61-bf61-4035d61a233f -->

B for now, but in future versions it would be nice to have a option for "training videos" about the move. Also in future version mapping these videos could make a stitchable video+music playback....

### Turn 024 — Assistant

<!-- node_id: c443d11e-04df-44ac-94c7-51bcb00d8ca0 message_id: c443d11e-04df-44ac-94c7-51bcb00d8ca0 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-010 — Locked</badge>

**Decision: Move label + optional detailed notes.**

For V1, each move has a start, end, track, short label, and optional free-text notes. The label appears on the timeline; detailed notes are available when selecting the move.

### Future capabilities — Not in V1

Two related ideas are now recorded:

- **Training video references:** Associate a move with one or more demonstration videos, potentially through a reusable move library.
- **Stitched choreography playback:** Assemble video segments associated with successive moves, synchronize them with the song, and produce a visual demonstration of the planned choreography.

These are distinct from the earlier idea of overlaying an independently recorded performance video on the timeline.

We should preserve stable move identities so these associations can be added later, without designing video editing or rendering into V1.

---

## Question 11 — Precision of move timing

We've established that moves can cross musical boundaries. Now we need to decide where their start and end points can be placed.

For example, a move might start on count 7, on the *and* of 7, or at a precise position between beats.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Whole beats only**

      <text color="secondary" size="sm">Moves start and end on integer beats. Simple, but cannot represent syncopated movements precisely.</text>
    </radio>
    <radio value="B">
      **B. Configurable beat subdivisions (recommended)**

      <text color="secondary" size="sm">Snap to whole beats, half-beats, quarter-beats, or triplets. Suitable for swing rhythms and syncopation.</text>
    </radio>
    <radio value="C">
      **C. Free timing with optional snapping**

      <text color="secondary" size="sm">Move boundaries can be placed anywhere in continuous time, with optional snapping to beats and subdivisions.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 11, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. It supports musical timing without requiring arbitrary time positioning.

One consideration: swing eighth notes aren't necessarily evenly spaced. We can represent the conventional *1-and-2* counting grid initially, while leaving expressive swing timing for later.

### Turn 025 — User

<!-- node_id: 89d39651-fe32-4a6b-baf4-d8b67ad717c0 message_id: 89d39651-fe32-4a6b-baf4-d8b67ad717c0 -->

We are mostly going to fit the "one of the move" with some whole beats on the song grid... beat subdivision should be an advanced option not default. If very easy to implement -> v1 if not for later versions

### Turn 026 — Assistant

<!-- node_id: 68209431-1b8e-4b50-9fbe-ee21924f364d message_id: 68209431-1b8e-4b50-9fbe-ee21924f364d -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-011 — Locked</badge>

**Decision: Whole-beat snapping by default.**

- Move boundaries align with whole beats on the musical grid.
- The normal workflow is to position the *one* of a move on the appropriate musical beat.
- Sub-beat precision is an advanced feature, not part of the default interaction.
- **V1 optional:** Configurable subdivisions, only if supported easily by the selected timeline component.
- **Deferred otherwise:** Sub-beat snapping, triplets, and more elaborate rhythmic timing.

This reinforces our delivery-first approach: avoid implementing features that don't materially improve the initial workflow.

---

## Question 12 — Creating and positioning moves

Now we need to define the main editing interaction. This will be particularly important when evaluating reusable timeline libraries.

Imagine a track with an empty 8-count phrase. How should the user create a move?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Select a range, then create a move**

      <text color="secondary" size="sm">Drag across counts 1–6, then choose "Add move". The move occupies the selected range.</text>
    </radio>
    <radio value="B">
      **B. Draw and edit blocks directly (recommended)**

      <text color="secondary" size="sm">Click and drag on an empty track to create a move block. Drag it to reposition, or drag its edges to resize.</text>
    </radio>
    <radio value="C">
      **C. Insert at playhead**

      <text color="secondary" size="sm">Place the playback cursor at a beat, insert a move of a default duration, then adjust it.</text>
    </radio>
    <radio value="D">
      **D. Text-first entry**

      <text color="secondary" size="sm">Enter a move name and its starting count/duration through a form or table. The timeline updates accordingly.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 12, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** as the primary interaction. It feels natural for a visual editor, and it is a common pattern in DAW and video timeline components.

We can still add keyboard shortcuts or numerical editing later without making them prerequisites for V1.

### Turn 027 — User

<!-- node_id: b803253c-5f88-4ebf-ac6c-df4db57e2916 message_id: b803253c-5f88-4ebf-ac6c-df4db57e2916 -->

I'd say B, but also when possible we should pre-populate the move grid with the music grid template example: classic 4x8 AABA should / could have these blocks by defaults then if the user needs to modify blocks merge or remove or add he can. That would be a nice shortcut rather then having to enter individually each move cell

### Turn 028 — Assistant

<!-- node_id: f8473007-839b-44fd-9edb-1e0d2899b3d1 message_id: f8473007-839b-44fd-9edb-1e0d2899b3d1 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-012 — Locked</badge>

**Decision: Direct block editing, with automatic initialization from the musical structure.**

This is an important improvement to the workflow: the user shouldn't have to recreate information already present in the musical grid.

### V1 behavior

- **Direct editing:** Draw, drag, resize, merge, split, and delete move blocks.
- **Grid initialization:** When a musical structure is defined, Koreo can populate a choreography track with corresponding empty move blocks.
- **Independent editing:** Once generated, move blocks can be modified without affecting the musical structure.
- **Optional initialization:** Users can also start with an empty track.

For example, a 4×8 AABA structure could initialize a choreography track with four 8-count blocks, each ready to be annotated or subdivided.

<box border radius="lg" padding={3} gap={2}>
  <text color="secondary" weight="medium" size="xs">INITIALIZED CHOREOGRAPHY</text>
  <svg viewBox="0 0 320 99" width="100%">
    <g fontSize="10" fill="currentColor">
      <text x="2" y="14">Structure</text>
      <text x="2" y="57">Moves</text>
    </g>
    <g transform="translate(64 0)">
      {#each ["A","A","B","A"] as s,i}
        <rect x={i*63.5} y="2" width="61.5" height="23" rx="3" fill={s==="B"?"#C8B08B":"#8BAFC7"}/>
        <text x={i*63.5+30.75} y="17" fontSize="11" fill="#24303B" textAnchor="middle">{s}</text>
        <rect x={i*63.5} y="44" width="61.5" height="27" rx="3" fill="#A4B9A4" stroke="#6C896E" strokeWidth=".6"/>
        <text x={i*63.5+30.75} y="61" fontSize="10" fill="#253627" textAnchor="middle">Empty</text>
      {/each}
      <text x="0" y="90" fontSize="9" fill="currentColor" opacity=".65">Blocks can be split, merged, resized or deleted</text>
    </g>
  </svg>
</box>

**Clarification:** This does not require a library of predefined song templates in V1. The user manually creates the structure, and Koreo can use that structure to initialize the move track. Reusable AABA/Boogie presets remain a future feature.

---

## Question 13 — What happens when the musical structure changes?

Suppose you've already initialized the choreography and written several moves. You then discover that a phrase should be 6 counts instead of 8.

Should the choreography automatically follow changes to the musical structure?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Always synchronized**

      <text color="secondary" size="sm">Changing structural boundaries automatically resizes or repositions associated move blocks.</text>
    </radio>
    <radio value="B">
      **B. Independent after initialization (recommended)**

      <text color="secondary" size="sm">The structure is used to create initial blocks, but subsequent structural edits don't alter existing choreography.</text>
    </radio>
    <radio value="C">
      **C. Ask on each structural change**

      <text color="secondary" size="sm">When the structure changes, Koreo offers to propagate the modification to affected move blocks.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 13, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**, consistent with our earlier decision that musical structure and choreography have independent timing.

It also avoids accidentally damaging choreography that has already been carefully edited.

### Turn 029 — User

<!-- node_id: c492dd4f-5d00-495f-8a86-2cd6b8639d46 message_id: c492dd4f-5d00-495f-8a86-2cd6b8639d46 -->

yes B. ALso for S-012 user could specify basic move grid prepopulation like 8 counts move. (classic for lindy hop)

### Turn 030 — Assistant

<!-- node_id: cd67adf7-bb9f-4d8a-9a64-d5d839e9a71a message_id: cd67adf7-bb9f-4d8a-9a64-d5d839e9a71a -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-013 — Locked</badge>

**Decision: Choreography remains independent after initialization.**

Changes to the musical structure do not automatically resize, reposition, or delete existing move blocks.

### S-012 — Amendment

Move-track prepopulation supports two methods:

1. **From musical structure:** Generate blocks corresponding to the defined sections or subdivisions.
2. **By count interval:** Generate blocks of a specified duration, such as 8 counts per move (a natural default for Lindy Hop).

Both methods create ordinary, editable move blocks. Users can subsequently split, merge, resize, or delete them.

The prepopulation method is selected when initializing a track; it does not create a permanent dependency on the musical structure.

---

## Question 14 — How should the musical structure itself be created?

We have discussed subdividing regions, but not how the user initially lays out the song.

Imagine the BPM and anchor have been established. The user listens to the song and identifies an introduction, followed by `A A B A`.

{@body const [choice,setChoice] = DIL.useState("C")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Draw regions manually**

      <text color="secondary" size="sm">Drag across the musical grid to create a region, label it, and subdivide it as needed.</text>
    </radio>
    <radio value="B">
      **B. Enter a structural sequence**

      <text color="secondary" size="sm">Enter something like AABA and specify the number of counts per section. Koreo generates the regions automatically.</text>
    </radio>
    <radio value="C">
      **C. Both methods (recommended)**

      <text color="secondary" size="sm">Quickly generate a structure from a sequence, then freely draw, resize, split, merge, and relabel regions.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 14, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **C**, provided sequence entry stays simple. It would be useful to generate `AABA` with four 8-count sections in one operation, while retaining complete manual control.

This would be a lightweight structure-generation tool, not the full reusable template system we've deferred to a later release.

### Turn 031 — User

<!-- node_id: fd5111a2-8f45-4116-8d47-e8e6e30268e0 message_id: fd5111a2-8f45-4116-8d47-e8e6e30268e0 -->

Ok C and I added some example of the possible  "display". It is an idea only. Actual rendering and UX will be to test.

### Turn 032 — Assistant

<!-- node_id: ae2d3651-17a4-414e-bc52-28b65e551b26 message_id: ae2d3651-17a4-414e-bc52-28b65e551b26 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-014 — Locked</badge>

**Decision: Both sequence-based and manual musical structure editing.**

- Generate regions from a sequence such as `AABA`, with configurable durations.
- Manually draw, resize, split, merge, and label regions.
- Combine both approaches within the same project.
- Keep reusable structure templates as a future enhancement.

Your Excel example will serve as a **non-binding UX reference**, not a frozen layout specification. We'll distinguish the underlying functional requirements from presentation choices that need prototyping and testing.

### Review of `display-a.xlsx`

Your example introduces an interesting alternative to a conventional horizontal DAW timeline.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium" size="sm">Display A — Conceptual interpretation</text>
  <table>
    <table-row><table-cell width="30%">Intro</table-cell><table-cell>8</table-cell><table-cell>8</table-cell><table-cell/><table-cell/></table-row>
    {#each ["A","A","B","A"] as s,i}
      <table-row><table-cell>{s}</table-cell>{#each [0,1,2,3] as j}<table-cell>8</table-cell>{/each}</table-row>
    {/each}
    <table-row><table-cell>Interlude</table-cell><table-cell/><table-cell>8</table-cell><table-cell>8</table-cell><table-cell/></table-row>
    {#each ["A","A","B","A"] as s,i}
      <table-row><table-cell>{s}</table-cell>{#each [0,1,2,3] as j}<table-cell>8</table-cell>{/each}</table-row>
    {/each}
    <table-row><table-cell>Outro</table-cell>{#each [0,1,2,3] as j}<table-cell>8</table-cell>{/each}</table-row>
  </table>
  <caption>Each row represents a musical section, and each numbered cell represents an 8-count phrase. The interlude's centered cells are a visual arrangement, not a timing offset.</caption>
</box>

I see three useful ideas here:

- **Wrapped musical structure:** The song flows vertically through successive rows instead of extending indefinitely to the right.
- **Variable-length rows:** An intro or interlude can contain fewer phrases than an A section.
- **Visual alignment:** Shorter sections can be centered for readability without changing their musical timing.

This is potentially much more readable for choreography planning than a DAW timeline. We'll retain it as **Display A**, a candidate view to evaluate during UX prototyping.

---

## Question 15 — Relationship between musical structure and visual layout

Your example raises a design question: should the grid's visual arrangement carry musical meaning?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Layout determines structure**

      <text color="secondary" size="sm">Each row is a section, and moving cells between rows changes their musical organization.</text>
    </radio>
    <radio value="B">
      **B. Layout is independent of structure (recommended)**

      <text color="secondary" size="sm">The song has an ordered musical structure. Rows, wrapping, spacing, and centering are presentation choices that don't change timing.</text>
    </radio>
    <radio value="C">
      **C. Hybrid**

      <text color="secondary" size="sm">Visual rearrangement can optionally modify the musical structure, depending on the editing mode.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 15, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It would let us experiment with Display A, a conventional timeline, or other layouts without redesigning the project data model.

The distinction is particularly important for your centered interlude example: visual positioning shouldn't accidentally introduce silence or extra counts.

### Turn 033 — User

<!-- node_id: 16e46d7b-e989-47a5-a5b7-c648adf70dae message_id: 16e46d7b-e989-47a5-a5b7-c648adf70dae -->

the musical structure is a source of truth. Once the user has defined it, it stays true for the whole song. It can then serve for visual, musical reference for the user. One of the very important deliverable / output of this app would be a "choreography sheet". Something intended for a dancer to look at and understand rapidly the layout and the information. So musical structure will be important, but the dancer thinks in both: music and move strcuture. "Display A" looks like a viable "Choreography sheet". This sheet is similar to a music sheet but intended for dancers.

### Turn 034 — Assistant

<!-- node_id: f15339a9-4413-4352-b833-3075df6bd610 message_id: f15339a9-4413-4352-b833-3075df6bd610 -->

This clarifies something fundamental about Koreo: **the choreography sheet is a primary product deliverable, not merely an alternative view of the editor.**

We're building a tool to *author a choreography*, but also to *communicate it to dancers*.

## S-015 — Musical structure and presentation

<badge color="success"><icon name="check" inline/> Locked</badge>

**Decision: The musical structure is the authoritative reference for the entire choreography.**

Once defined, it establishes the musical positions against which all choreography is organized. It remains editable, but there is only one authoritative structure for a given song.

The application distinguishes three concepts:

| Concept | Responsibility |
|---|---|
| **Musical structure** | Defines sections, phrases, counts, and their positions in the song |
| **Choreography structure** | Defines moves, durations, sequences, and dancer/group assignments |
| **Choreography sheet** | Presents both structures in a compact, readable form intended for dancers |

The sheet is analogous to musical notation: its purpose is to communicate the choreography efficiently, not necessarily to reproduce the editing interface.

**Display A** is now a candidate choreography-sheet layout. Its final appearance and interaction model remain subject to prototyping and human validation.

This also changes our priorities slightly: producing a useful choreography sheet should be part of V1, rather than a future reporting feature.

---

## Question 16 — What should the choreography sheet contain?

A sheet could prioritize the musical structure, the move sequence, or both equally.

{@body const [choice,setChoice] = DIL.useState("C")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Music-first**

      <text color="secondary" size="sm">The sheet is primarily a musical map: AABA sections, phrases, and counts, with move labels placed inside the corresponding cells.</text>
    </radio>
    <radio value="B">
      **B. Move-first**

      <text color="secondary" size="sm">The sheet primarily displays the sequence of moves, with musical positions and section labels as secondary references.</text>
    </radio>
    <radio value="C">
      **C. Integrated notation (recommended)**

      <text color="secondary" size="sm">Musical sections provide the visual organization, while move blocks and their timing are clearly visible within that structure. Both remain readable together.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 16, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **C**. It preserves the readability of Display A while supporting moves that cross phrase boundaries and different choreography tracks for different dancers.

We'll address page layout, printing, PDF export, and track selection separately. The first question is what information the sheet must communicate, independently of its final rendering.

### Turn 035 — User

<!-- node_id: 8663d4a5-40c2-422e-bbb3-452d2a452dd8 message_id: 8663d4a5-40c2-422e-bbb3-452d2a452dd8 -->

For Koreo spec'ing question 16, I choose C.

### Turn 036 — Assistant

<!-- node_id: dd142dfa-f326-4a21-9722-250093047f22 message_id: dd142dfa-f326-4a21-9722-250093047f22 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-016 — Locked</badge>

**Decision: Integrated musical and choreographic notation.**

The choreography sheet will:

- Organize the song visually according to its musical structure.
- Display moves and their timing within that structure.
- Support multiple choreography tracks for different dancers, couples, or groups.
- Clearly represent moves crossing musical boundaries.
- Prioritize quick comprehension by dancers over detailed editing controls.

**Display A** remains our initial visual reference, not a mandatory layout.

---

## Question 17 — How should the choreography sheet be delivered?

Since the sheet is a primary deliverable, we should decide its minimum output capabilities for V1.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. On-screen sheet only**

      <text color="secondary" size="sm">A dedicated read-only view optimized for dancers. Printing and export can come later.</text>
    </radio>
    <radio value="B">
      **B. On-screen sheet + PDF export (recommended)**

      <text color="secondary" size="sm">A readable sheet in the application, with the ability to export a paginated PDF for printing or sharing.</text>
    </radio>
    <radio value="C">
      **C. On-screen sheet + PDF + image export**

      <text color="secondary" size="sm">Adds PNG/SVG output for sharing individual sections or entire choreography sheets digitally.</text>
    </radio>
    <radio value="D">
      **D. Fully configurable print layouts**

      <text color="secondary" size="sm">Page sizes, orientations, scaling, track visibility, typography, and layout presets. Most flexible, but significantly more work.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 17, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. It establishes a concrete, testable deliverable: a dancer can open a choreography sheet on-screen or receive a printable PDF.

We can postpone sophisticated page-layout controls until we've tested the sheet with real choreography and dancers.

### Turn 037 — User

<!-- node_id: a44ced16-a0c5-4664-a1af-806dba5c3de1 message_id: a44ced16-a0c5-4664-a1af-806dba5c3de1 -->

B. I would also have an Excel export.

### Turn 038 — Assistant

<!-- node_id: 1480756a-4527-40e3-8b1a-8b0bec164aa2 message_id: 1480756a-4527-40e3-8b1a-8b0bec164aa2 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-017 — Locked</badge>

**Decision: On-screen choreography sheet + PDF and Excel exports.**

V1 will support:

- **On-screen sheet:** Readable, integrated musical and choreographic notation.
- **PDF export:** Paginated, printable choreography sheet intended for dancers.
- **Excel export (`.xlsx`):** Editable spreadsheet representing the musical structure, move blocks, labels, and notes.

The Excel export should preserve the sheet's visual organization where practical, rather than simply dumping the underlying data into a table.

However, **Excel export is not project persistence**. We will define Koreo's native save/load format separately.

---

## Question 18 — What should Excel export prioritize?

Your Display A example suggests that Excel could be more than a secondary output format.

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Visual choreography sheet (recommended)**

      <text color="secondary" size="sm">Preserve the on-screen sheet's organization using formatted cells, merged regions, labels, and move blocks. Optimized for reading, printing, and manual annotation.</text>
    </radio>
    <radio value="B">
      **B. Structured data export**

      <text color="secondary" size="sm">Export sections, tracks, moves, start counts, durations, and notes as tabular data. Optimized for filtering, formulas, and external processing.</text>
    </radio>
    <radio value="C">
      **C. Both in one workbook**

      <text color="secondary" size="sm">One worksheet contains the formatted choreography sheet; another contains normalized data for further processing.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 18, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A for V1** because the main objective is communicating choreography to dancers, not exporting data for software integration.

Option C is attractive if the structured data worksheet can be added with little extra complexity.

### Turn 039 — User

<!-- node_id: da884f8b-7071-4ac6-8d75-92070cae6308 message_id: da884f8b-7071-4ac6-8d75-92070cae6308 -->

For Koreo spec'ing question 18, I choose A.

### Turn 040 — Assistant

<!-- node_id: d295260d-5210-42e6-8339-cea4320c00fe message_id: d295260d-5210-42e6-8339-cea4320c00fe -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-018 — Locked</badge>

**Decision: Excel export prioritizes the visual choreography sheet.**

The exported `.xlsx` workbook will:

- Preserve the sheet's musical and choreographic organization.
- Use formatted cells, merged regions, and labels where appropriate.
- Be readable, printable, and manually editable in Excel.
- Follow the same underlying musical structure as the on-screen sheet and PDF.

A separate structured-data worksheet is **not required for V1**.

Excel remains an output format, not the authoritative project file.

---

## Question 19 — Project persistence

Now we need to decide how Koreo saves its projects so users can resume editing later.

The project must preserve the audio reference, musical structure, BPM calibration, choreography tracks, moves, and notes.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. JSON project file**

      <text color="secondary" size="sm">Human-readable, easy to inspect, version-control, and debug. Audio remains an external file referenced by path.</text>
    </radio>
    <radio value="B">
      **B. Self-contained project package (recommended)**

      <text color="secondary" size="sm">A single Koreo project file containing structured project data and the imported audio. Portable between computers, but potentially larger.</text>
    </radio>
    <radio value="C">
      **C. Project folder**

      <text color="secondary" size="sm">A directory containing a JSON project file, audio, and potentially other media. Easy to inspect and extend, but requires managing multiple files.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 19, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** for a desktop application intended for dancers. A single portable project file would make sharing and archiving choreography easier.

Internally, it could simply be a ZIP container with JSON metadata and media files, avoiding the need for a database in V1.

### Turn 041 — User

<!-- node_id: 294acc12-979d-409c-9781-57e2ec8b54a5 message_id: 294acc12-979d-409c-9781-57e2ec8b54a5 -->

I'd say B for now... but let's keep it modifiable for future versions...

### Turn 042 — Assistant

<!-- node_id: 5230c2aa-981f-439e-ac66-3a02eb866627 message_id: 5230c2aa-981f-439e-ac66-3a02eb866627 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-019 — Locked</badge>

**Decision: Self-contained, portable project file for V1.**

- One file contains the project data and imported audio.
- Projects can be saved, reopened, copied, and shared.
- The internal format should be versioned and extensible.
- Future releases must be able to evolve the format through migrations.
- The file extension and internal serialization technology are not yet frozen.

**Implementation candidate:** ZIP container with JSON metadata and media files. This is a preference, not a binding technology decision.

We'll also distinguish between *project-format compatibility* and *new features*: adding video or move-library references later should not require redesigning the entire project model.

---

## Question 20 — Audio playback requirements

We have defined BPM calibration and musical structure, but not the minimum audio-player capabilities.

For V1, which playback controls are essential?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Basic playback**

      <text color="secondary" size="sm">Play, pause, stop, seek, and display the current playback position on the musical grid.</text>
    </radio>
    <radio value="B">
      **B. Playback + looping (recommended)**

      <text color="secondary" size="sm">Everything in A, plus the ability to loop a selected musical region, such as an 8-count phrase or an entire A section.</text>
    </radio>
    <radio value="C">
      **C. Practice-oriented playback**

      <text color="secondary" size="sm">Everything in B, plus variable playback speed, count-in, and optional metronome clicks.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 20, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. Looping is especially useful when designing or reviewing a specific phrase.

Variable playback speed would also be valuable for dancers, but it introduces questions about pitch preservation and audio processing. We can defer those unless you consider them essential for the initial release.

### Turn 043 — User

<!-- node_id: 57a484c6-e1ac-452b-a822-05f4f0ea83ab message_id: 57a484c6-e1ac-452b-a822-05f4f0ea83ab -->

If B" is easy to implement then ok. If not or if we hit a complexity wall we can keep it at A for v1

### Turn 044 — Assistant

<!-- node_id: c41c0fc5-6595-45e3-b557-277e75fca3a0 message_id: c41c0fc5-6595-45e3-b557-277e75fca3a0 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-020 — Locked</badge>

**Decision: Basic audio playback is mandatory; region looping is conditional for V1.**

- **Required:** Play, pause, stop, seek, and synchronized playback position on the musical grid.
- **Conditional:** Loop a selected musical region if the chosen audio library supports it without significant complexity.
- **Deferred:** Variable playback speed, pitch preservation, count-in, and metronome.

We'll use a consistent rule for conditional features: **include them if straightforward with the selected technology; otherwise defer them without blocking V1.**

---

## Question 21 — Audio visualization

We need to decide whether Koreo should display the audio waveform.

A waveform could help users identify the first beat, place calibration points, and navigate the song.

<box border radius="lg" padding={3} gap={2}>
  <text color="secondary" weight="medium" size="xs">ILLUSTRATIVE WAVEFORM WITH BEAT GRID</text>
  <svg viewBox="0 0 330 104" width="100%">
    <rect x="1" y="1" width="328" height="101" rx="4" fill="#8195A0" fillOpacity=".08"/>
    {#each Array.from({length:17},(_,i)=>i) as i}
      <line x1={10+i*19.3} y1="12" x2={10+i*19.3} y2="91" stroke="currentColor" strokeOpacity={i%4===0?".35":".12"} strokeWidth={i%4===0?1.5:1}/>
    {/each}
    <line x1="10" y1="52" x2="319" y2="52" stroke="currentColor" strokeOpacity=".25"/>
    <path d={"M "+Array.from({length:155},(_,i)=>{const x=10+i*2;const a=(Math.abs(Math.sin(i*0.29)*Math.cos(i*0.07))+0.1)*(8+18*Math.abs(Math.sin(i*0.095)));return `${x},${52-a}`}).join(" L ")+" L "+Array.from({length:155},(_,i)=>{const j=154-i;const x=10+j*2;const a=(Math.abs(Math.sin(j*0.29)*Math.cos(j*0.07))+0.1)*(8+18*Math.abs(Math.sin(j*0.095)));return `${x},${52+a}`}).join(" L ")+" Z"} fill="#76A7B9" fillOpacity=".8"/>
    <line x1="87.2" y1="6" x2="87.2" y2="96" stroke="#D28A4F" strokeWidth="2"/>
    <text x="92" y="14" fontSize="9" fill="#D28A4F">Anchor</text>
  </svg>
</box>

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. No waveform in V1**

      <text color="secondary" size="sm">Use playback and a time ruler to locate beats. Simplest implementation.</text>
    </radio>
    <radio value="B">
      **B. Basic waveform display (recommended)**

      <text color="secondary" size="sm">Show an audio waveform behind or alongside the beat grid, with zoom and navigation. No audio editing.</text>
    </radio>
    <radio value="C">
      **C. Advanced waveform navigation**

      <text color="secondary" size="sm">Waveform overview, detailed zoom, transient markers, and audio-selection tools.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 21, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. A basic waveform would make the BPM calibration workflow considerably more usable, especially when placing the anchor and secondary calibration point.

We don't need audio editing capabilities to benefit from waveform visualization.

### Turn 045 — User

<!-- node_id: 05349051-7e37-461d-9166-3b14dd40ee74 message_id: 05349051-7e37-461d-9166-3b14dd40ee74 -->

For Koreo spec'ing question 21, I choose B.

### Turn 046 — Assistant

<!-- node_id: 6a178c8a-57e2-4ffd-80f9-cfc4c1ac914d message_id: 6a178c8a-57e2-4ffd-80f9-cfc4c1ac914d -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-021 — Locked</badge>

**Decision: Basic waveform visualization in V1.**

- Display the audio waveform alongside the musical beat grid.
- Support horizontal zooming and navigation.
- Show the playback cursor, primary anchor, and secondary calibration point.
- Allow visual alignment of the beat grid with the waveform.
- No audio editing, transient detection, or automatic beat detection.

The waveform is a navigation and calibration aid, not an editable audio track.

---

## Question 22 — How should users navigate the choreography?

We now have two potentially different ways to view the same project:

- A continuous audio timeline, useful for playback, waveform alignment, and BPM calibration.
- A wrapped musical grid, similar to Display A, useful for reading and planning choreography.

Should these be separate views or one combined editor?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. One unified editor**

      <text color="secondary" size="sm">Waveform, musical structure, and move tracks all share one horizontally scrolling timeline. The choreography sheet is a separate read-only output.</text>
    </radio>
    <radio value="B">
      **B. Two complementary editing views (recommended)**

      <text color="secondary" size="sm">A timeline view for audio and calibration, plus a wrapped musical-grid view for choreography. Both edit the same underlying project.</text>
    </radio>
    <radio value="C">
      **C. Sheet-first editor**

      <text color="secondary" size="sm">The wrapped musical grid is the main editing interface. Audio playback and waveform calibration appear in a dedicated panel or modal.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 22, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B conceptually**, because waveform calibration and choreography planning benefit from different visual arrangements.

However, **C may be more delivery-focused for V1**: one primary editor, with a specialized audio calibration panel, would avoid implementing two fully interactive editing interfaces.

Which approach best matches how you expect to use Koreo day to day?

### Turn 047 — User

<!-- node_id: 6ef807a6-f750-42ef-b569-96f30ff77522 message_id: 6ef807a6-f750-42ef-b569-96f30ff77522 -->

For Koreo spec'ing question 22, I choose B.

### Turn 048 — Assistant

<!-- node_id: c337dea0-be8d-4d99-b037-88fa9a8dfa57 message_id: c337dea0-be8d-4d99-b037-88fa9a8dfa57 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-022 — Locked</badge>

**Decision: Two complementary editing views.**

Both views operate on the same authoritative project data.

| | Timeline view | Musical-grid view |
|---|---|---|
| Primary purpose | Audio alignment and navigation | Choreography planning |
| Layout | Continuous horizontal timeline | Wrapped musical structure |
| Waveform | Yes | Not required |
| Musical structure | Visible | Primary organization |
| Move editing | Supported | Supported |
| Playback position | Synchronized | Synchronized |

Changes made in either view must be reflected in the other. The choreography sheet will derive from the same data.

**Implementation consideration:** We should reuse shared editing operations rather than independently implementing all the business logic twice. The actual UX remains subject to prototyping.

---

## Question 23 — How should the two views interact?

Suppose you're listening to a song in the timeline view and reach the second A section. You switch to the musical-grid view to annotate some moves.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Independent navigation**

      <text color="secondary" size="sm">Each view remembers its own scroll position and selection. Switching views doesn't change where you're looking.</text>
    </radio>
    <radio value="B">
      **B. Shared playback and selection (recommended)**

      <text color="secondary" size="sm">Both views share the current playback position and selected musical region or move. Switching views brings the relevant location into view.</text>
    </radio>
    <radio value="C">
      **C. Simultaneous split view**

      <text color="secondary" size="sm">Both views can be displayed side by side, with synchronized playback, selection, and navigation.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 23, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. It gives us one consistent editing context without the additional layout complexity of a split view.

A simultaneous split view could be a useful later enhancement, especially with multiple monitors.

### Turn 049 — User

<!-- node_id: 97063c87-5e16-42f3-b618-7899dd519bd3 message_id: 97063c87-5e16-42f3-b618-7899dd519bd3 -->

For Koreo spec'ing question 23, I choose B.

### Turn 050 — Assistant

<!-- node_id: 4b3424ac-0e85-419d-ae3c-8bc34f534031 message_id: 4b3424ac-0e85-419d-ae3c-8bc34f534031 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-023 — Locked</badge>

**Decision: Shared playback position and selection across both editing views.**

- Both views share the same playback cursor.
- Selecting a move or musical region in one view preserves that selection when switching views.
- Switching views automatically navigates to the relevant position.
- Each view can retain its own zoom level and display settings.
- Simultaneous split-screen editing is deferred.

This gives Koreo a consistent editing context while allowing the timeline and musical-grid views to serve different purposes.

---

## Question 24 — Undo and redo

Before moving into more detailed editing behavior, we should establish how Koreo handles mistakes.

This matters because users will frequently resize, split, merge, and reposition blocks.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Save-based recovery**

      <text color="secondary" size="sm">Users can save and reload their project, but individual editing actions cannot be undone.</text>
    </radio>
    <radio value="B">
      **B. Standard undo/redo (recommended)**

      <text color="secondary" size="sm">Ctrl+Z and Ctrl+Shift+Z reverse and restore editing operations across both views, including moves, regions, labels, and timing changes.</text>
    </radio>
    <radio value="C">
      **C. Undo/redo with visible history**

      <text color="secondary" size="sm">Everything in B, plus a history panel showing previous operations and allowing users to navigate through them.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 24, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. Undo/redo is important for an interactive editor, particularly when dragging or resizing regions.

We should also ensure that a continuous drag counts as **one undoable operation**, rather than generating dozens of separate history entries.

The implementation can likely use an existing command-stack mechanism, such as Qt's `QUndoStack` if we ultimately select PySide6.

### Turn 051 — User

<!-- node_id: 3600804a-32f8-438c-8fb7-2190adc4b99e message_id: 3600804a-32f8-438c-8fb7-2190adc4b99e -->

For Koreo spec'ing question 24, I choose B.

### Turn 052 — Assistant

<!-- node_id: 330d018d-069a-4f7d-8874-1deb100de142 message_id: 330d018d-069a-4f7d-8874-1deb100de142 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-024 — Locked</badge>

**Decision: Standard undo/redo across both editing views.**

- `Ctrl+Z` to undo, `Ctrl+Shift+Z` to redo.
- One shared editing history across both views.
- Supports structural changes, move creation/deletion, resizing, labels, and timing adjustments.
- Continuous operations, such as dragging a boundary, count as one undoable action.
- A visible history panel is not required for V1.

---

## Question 25 — Saving and recovery

We've established the project format (S-019) and undo/redo (S-024). Now we need to decide how Koreo protects work against accidental closure or crashes.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Manual saving only**

      <text color="secondary" size="sm">Standard Save / Save As, with a warning before closing a modified project.</text>
    </radio>
    <radio value="B">
      **B. Manual saving + automatic recovery (recommended)**

      <text color="secondary" size="sm">Standard saving, unsaved-change warnings, and periodic recovery snapshots that can restore work after a crash.</text>
    </radio>
    <radio value="C">
      **C. Continuous autosave**

      <text color="secondary" size="sm">Changes are automatically saved to the project file, with minimal need for manual saving.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 25, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It protects work without silently overwriting the user's last deliberately saved version.

Recovery snapshots should be separate from the authoritative project file. We can decide their precise frequency during implementation planning.

### Turn 053 — User

<!-- node_id: 73d918dc-42b1-41c3-a49a-9918969d75ba message_id: 73d918dc-42b1-41c3-a49a-9918969d75ba -->

For Koreo spec'ing question 25, I choose B.

### Turn 054 — Assistant

<!-- node_id: 320486cc-dac7-487b-95de-cb519d845c13 message_id: 320486cc-dac7-487b-95de-cb519d845c13 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-025 — Locked</badge>

**Decision: Manual saving with automatic crash recovery.**

- Standard **Save** and **Save As** operations.
- Warning when closing a project with unsaved changes.
- Periodic recovery snapshots stored separately from the project file.
- After an unexpected shutdown, Koreo offers to restore recoverable changes.
- Recovery never silently overwrites the last manually saved version.

Snapshot frequency and retention will be determined during implementation planning.

---

## Question 26 — Target operating systems

We should establish which platforms the first release must support. This will influence our choice between PySide6 and Tauri, as well as audio playback and packaging.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Linux only**

      <text color="secondary" size="sm">Focus development and testing on Linux. Other platforms are not required for V1.</text>
    </radio>
    <radio value="B">
      **B. Linux first, cross-platform architecture (recommended)**

      <text color="secondary" size="sm">Develop and validate V1 on Linux, while avoiding Linux-specific dependencies that would complicate Windows and macOS support later.</text>
    </radio>
    <radio value="C">
      **C. Linux + Windows for V1**

      <text color="secondary" size="sm">Both platforms must be packaged and tested before V1 is considered complete.</text>
    </radio>
    <radio value="D">
      **D. Linux + Windows + macOS for V1**

      <text color="secondary" size="sm">Full desktop cross-platform support from the first release, with the corresponding testing and packaging effort.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 26, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** for the initial proof of concept. It lets us focus on delivering a usable application without prematurely introducing a multi-platform release process.

Since choreography sheets can be exported to PDF and Excel, dancers won't need to install Koreo simply to read the results.

### Turn 055 — User

<!-- node_id: 22c97f79-daa1-4d5c-b37b-ef985383f129 message_id: 22c97f79-daa1-4d5c-b37b-ef985383f129 -->

For Koreo spec'ing question 26, I choose B.

### Turn 056 — Assistant

<!-- node_id: a5b19d94-7dbd-46d3-a17c-ed5dc6b5dad2 message_id: a5b19d94-7dbd-46d3-a17c-ed5dc6b5dad2 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-026 — Locked</badge>

**Decision: Linux-first development with cross-platform architecture.**

- Linux is the development and validation platform for V1.
- Windows and macOS compatibility should be preserved where practical.
- No requirement to package or test Windows/macOS releases for V1.
- Avoid unnecessary platform-specific dependencies.

This is consistent with our delivery-first strategy. The final choice between PySide6 and Tauri remains open until we evaluate reusable components.

---

## Question 27 — Supported audio formats

Koreo needs to import audio for playback, waveform visualization, and BPM calibration.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. WAV only**

      <text color="secondary" size="sm">Simplest format to decode and visualize, but inconvenient for users whose music libraries are mostly MP3.</text>
    </radio>
    <radio value="B">
      **B. MP3 + WAV (recommended)**

      <text color="secondary" size="sm">Support the two most common formats needed for the proof of concept. Keep the import pipeline extensible.</text>
    </radio>
    <radio value="C">
      **C. Broad audio format support**

      <text color="secondary" size="sm">MP3, WAV, FLAC, AAC/M4A, OGG, and other formats supported by the selected playback backend.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 27, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. MP3 and WAV cover the initial use case without making codec compatibility a major project concern.

If the selected audio library already handles additional formats reliably, we can expose them without committing to exhaustive testing for every codec.

### Turn 057 — User

<!-- node_id: bee75d09-127d-48f3-b0be-d1ee2a19604b message_id: bee75d09-127d-48f3-b0be-d1ee2a19604b -->

For Koreo spec'ing question 27, I choose B.

### Turn 058 — Assistant

<!-- node_id: 7c8fba3c-dd18-4760-bc2f-73bf9ec29fdf message_id: 7c8fba3c-dd18-4760-bc2f-73bf9ec29fdf -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-027 — Locked</badge>

**Decision: MP3 and WAV are the required audio formats for V1.**

- Both formats must support playback, waveform visualization, and BPM calibration.
- Imported audio is included in the portable project file (S-019).
- The audio backend should remain extensible.
- Additional formats (FLAC, OGG, AAC/M4A) may be supported if straightforward, but are not required for V1.

---

## Question 28 — Editing musical structure after choreography exists

We've established that choreography moves retain their timing when the musical structure changes (S-013).

However, there's an important distinction between **changing a section boundary** and **inserting musical counts**.

Suppose you have a completed choreography and discover that you forgot an 8-count phrase in the introduction. You insert those eight counts into the musical structure.

What should happen to the existing choreography?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Absolute musical positions remain unchanged**

      <text color="secondary" size="sm">Existing moves stay on their original beat numbers. Inserting counts changes the structure, but does not shift moves.</text>
    </radio>
    <radio value="B">
      **B. Ripple editing for inserted/deleted counts (recommended)**

      <text color="secondary" size="sm">Inserting eight counts shifts later moves by eight counts. Ordinary boundary adjustments still leave moves unchanged.</text>
    </radio>
    <radio value="C">
      **C. Ask whether to shift choreography**

      <text color="secondary" size="sm">When inserting or deleting counts, Koreo asks whether subsequent moves should shift or remain at their original musical positions.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 28, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, but this is a meaningful exception to S-013.

We would distinguish two operations:

- **Restructure:** Change labels, subdivisions, or boundaries without shifting choreography.
- **Insert/delete musical time:** Add or remove counts, shifting subsequent choreography accordingly.

This distinction should be explicit in the interface so users don't accidentally move an entire choreography.

### Turn 059 — User

<!-- node_id: 1112670c-70d1-4324-8493-3673f5a29577 message_id: 1112670c-70d1-4324-8493-3673f5a29577 -->

For Koreo spec'ing question 28, I choose C.

### Turn 060 — Assistant

<!-- node_id: 09e53141-4f92-4c0a-b7da-e368be1bdf4d message_id: 09e53141-4f92-4c0a-b7da-e368be1bdf4d -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-028 — Locked</badge>

**Decision: Ask whether to shift choreography when inserting or deleting musical counts.**

Two distinct operations:

- **Restructure:** Modify section labels, boundaries, or subdivisions without changing existing move positions (S-013).
- **Insert/delete counts:** Modify the musical timeline and ask whether subsequent choreography should shift accordingly.

The user can choose to ripple the change through the choreography or preserve existing move positions.

The operation must support undo/redo (S-024).

---

## Question 29 — Musical counting conventions

We have frequently used 8-count phrases, but the underlying musical grid should not assume every song follows that convention.

For example, dancers might count `1–8`, while musicians describe the same interval as two bars of 4/4.

How should Koreo represent counts?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Dance counts only**

      <text color="secondary" size="sm">The grid uses counts such as 1–8, with configurable phrase lengths. No explicit time-signature model.</text>
    </radio>
    <radio value="B">
      **B. Musical beats with dance-count grouping (recommended)**

      <text color="secondary" size="sm">The underlying timeline stores musical beats. Users can group and display them as 8-counts, 6-counts, bars, or other phrases.</text>
    </radio>
    <radio value="C">
      **C. Full musical meter model**

      <text color="secondary" size="sm">Explicit time signatures, bar numbering, beat grouping, and meter changes. More suitable for formal musical notation but more complex.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 29, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It keeps the underlying timing model simple while accommodating Lindy Hop, Boogie, and other dance styles.

An 8-count phrase would simply be eight consecutive beats, rather than a special fundamental unit of time. This also makes moves crossing phrase boundaries straightforward.

### Turn 061 — User

<!-- node_id: 4b0c9e79-38e9-4f78-88af-9b5036765e18 message_id: 4b0c9e79-38e9-4f78-88af-9b5036765e18 -->

For Koreo spec'ing question 29, I choose B.

### Turn 062 — Assistant

<!-- node_id: 316e56fd-8769-4e8c-870a-47774a23b37c message_id: 316e56fd-8769-4e8c-870a-47774a23b37c -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-029 — Locked</badge>

**Decision: Musical beats are the fundamental timing unit, with configurable dance-count groupings.**

- The underlying timeline uses musical beats.
- Users can group beats into 6-count, 8-count, or other phrases.
- Count numbering can restart at phrase boundaries.
- Musical sections can contain different phrase lengths.
- Moves can span multiple phrases without interruption.
- Full musical notation, time signatures, and meter changes are not required for V1.

This keeps the timing model independent of the way dancers count music.

---

## Question 30 — Repeated musical sections

We've established that Koreo supports structures such as `A A B A`.

But what does it mean when two sections are both labeled **A**?

For example, if a user subdivides the first A section into four 8-count phrases, should the other A sections automatically inherit that structure?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Linked repetitions**

      <text color="secondary" size="sm">All sections referencing the same pattern share their internal musical subdivisions. Editing the pattern updates every occurrence.</text>
    </radio>
    <radio value="B">
      **B. Independent sections (recommended for V1)**

      <text color="secondary" size="sm">Each A is a separate region. Matching labels communicate musical similarity but don't establish an automatic editing relationship.</text>
    </radio>
    <radio value="C">
      **C. Optional linked patterns**

      <text color="secondary" size="sm">Users can choose whether repeated sections share a definition or remain independent, with the ability to unlink individual occurrences.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 30, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**, with an important convenience: users should still be able to **duplicate a section and its subdivisions** rather than rebuilding it manually.

That would give us most of the practical benefit without introducing linked-pattern editing.

Later, option C could support reusable musical patterns and potentially reusable choreography sequences as well.

### Turn 063 — User

<!-- node_id: 9e7419fe-c314-423c-b618-969445b7f394 message_id: 9e7419fe-c314-423c-b618-969445b7f394 -->

B for v1. How are we doing on context size. Will we be able to officialize all of this accuratly in a handoff.md file? is it becoming too large?

### Turn 064 — Assistant

<!-- node_id: 4cadc177-0129-4056-b7b8-4b76d6259d4d message_id: 4cadc177-0129-4056-b7b8-4b76d6259d4d -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-030 — Locked</badge>

**Decision:** Repeated sections are independent in V1. Matching labels (A, B, etc.) do not establish automatic links. Duplicating a section with its subdivisions should be supported.

---

## Are we getting too large?

**We're fine for now, but I think it's time to consolidate.**

We've made 30 specification decisions, and I can still access the decisions from this conversation. However, I don't have a reliable numerical measure of the remaining context window.

The main risk isn't the number of decisions. It's that some decisions have been amended, qualified, or refined in subsequent answers.

For example:

- S-012 was amended to support configurable move-grid prepopulation.
- S-013 establishes independent choreography timing, while S-028 introduces optional ripple editing.
- S-004 and S-005 jointly define BPM calibration.
- S-015 through S-018 establish the choreography sheet as a primary deliverable.
- The framework selection remains intentionally unresolved.

All of this can be captured accurately, but **we shouldn't rely indefinitely on conversation history as the source of truth**.

## My recommendation: Create a specification checkpoint now

I'd distinguish two artifacts:

| Artifact | Purpose | Status |
|---|---|---|
| `koreo_specs_v1.md` | Consolidated product decisions S-001 through S-030 | Create now |
| `handoff_YYMMDD_1.md` | Complete execution contract for the development agent | Create after the interview |

The checkpoint would include every locked decision, amendments, deferred features, and unresolved questions.

The eventual handoff would additionally contain implementation instructions, tests, non-goals, and a definition of done.

### One important consideration

We've specified a fairly ambitious V1: two interactive editing views, audio calibration, a flexible musical hierarchy, multiple move tracks, a choreography sheet, PDF/Excel exports, undo/redo, and crash recovery.

That's not necessarily too ambitious for the product, but **it may be too much for a single implementation handoff**.

I would favor one authoritative product specification followed by smaller, milestone-oriented execution handoffs, each with clear acceptance tests.

### Proposed next step

**Transition temporarily from Spec’ing to Specification Consolidation.**

We create `koreo_specs_v1.md` now, verify that it faithfully represents S-001 through S-030, and then resume the interview at S-031.

That would give us a durable checkpoint without prematurely declaring the entire V1 design complete.

Would you like me to generate that checkpoint now?

### Turn 065 — User

<!-- node_id: 16cf2e73-10d5-4080-95ae-66c34680abd2 message_id: 16cf2e73-10d5-4080-95ae-66c34680abd2 -->

yes please so we don't lose productive spec context

### Turn 066 — Assistant

<!-- node_id: 767863a8-b353-4b49-923a-5e74ad6c9fa4 message_id: 767863a8-b353-4b49-923a-5e74ad6c9fa4 -->

## Koreo — Specification checkpoint 01

We're temporarily pausing the interview after **S-030** to preserve the decisions we've made.

I'll consolidate the specifications into `koreo_specs_v1.md`, including the original decisions, subsequent amendments, conditional V1 features, and deferred capabilities.

This will be a **living product specification**, not yet an execution handoff. In particular, I'll preserve the unresolved PySide6-versus-Tauri decision and distinguish mandatory V1 requirements from features that depend on implementation complexity.

I'll also retain `display-a.xlsx` as a non-binding UX reference for the choreography sheet.

<row align="center" gap={2}>
  <icon name="check-circle" color="success" size="lg"/>
  **Specification checkpoint created successfully.**
</row>

<box border radius="lg" padding={3} gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" size="2xl" color="secondary"/>
    <box flex="1" gap={1}>
      **koreo_specs_v1.md**

      <text color="secondary" size="xs">159 lines · ~2,350 words · Markdown</text>
    </box>
  </row>
  [<icon name="download" inline/> Download specification checkpoint](sandbox:/mnt/data/koreo_specs_v1.md)
</box>

The checkpoint contains all **30 decisions**, including their amendments and exceptions, plus:

- Required versus conditional V1 features.
- Deferred capabilities and future architecture considerations.
- Unresolved decisions and design risks.
- The non-binding Display A reference.
- Instructions for resuming the interview and eventually generating execution handoffs.

I also flagged a few details we should clarify later, particularly how the musical structure generator interprets `4×8`, how overlapping moves work within a single track, and how ripple editing handles moves spanning an insertion point.

**We now have a durable checkpoint.** We can safely continue the interview at S-031 without relying exclusively on the conversation history.

My suggestion is to finish the remaining product decisions, then evaluate the scope of V1 before committing to implementation milestones.

### Turn 067 — User

<!-- node_id: 01b07963-46f6-4ac4-bbc4-76734db225f2 message_id: 01b07963-46f6-4ac4-bbc4-76734db225f2 -->

Sounds good

### Turn 068 — Assistant

<!-- node_id: 5e3cb202-6e26-4f61-a371-f14c00779821 message_id: 5e3cb202-6e26-4f61-a371-f14c00779821 -->

## Koreo — Spec’ing Interview (continued)

We're resuming **Phase 3 — Spec’ing**, starting at S-031. The first 30 decisions are consolidated in our specification checkpoint.

## Question 31 — Overlapping moves within a track

We've established that moves on different tracks can overlap (S-009). But what about moves **within the same track**?

For example, a couple might perform a continuous footwork pattern while adding a turn that starts halfway through it.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. No overlaps within a track**

      <text color="secondary" size="sm">Move blocks cannot overlap on the same track. Simultaneous actions require separate tracks.</text>
    </radio>
    <radio value="B">
      **B. Allow overlaps (recommended)**

      <text color="secondary" size="sm">Moves may overlap within the same track. Koreo arranges overlapping blocks visually so their labels remain readable.</text>
    </radio>
    <radio value="C">
      **C. No overlaps in V1, optional overlaps later**

      <text color="secondary" size="sm">Keep the initial editing model simple, but avoid designing the underlying data model around non-overlapping intervals.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 31, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I lean toward **B** because it is more flexible and consistent with the idea of independent move timing.

However, the choreography sheet could become difficult to read when multiple moves overlap in a single lane. Option C is a reasonable delivery-focused compromise.

### Turn 069 — User

<!-- node_id: 677e852d-7a72-4db4-9f06-abe295de4d5a message_id: 677e852d-7a72-4db4-9f06-abe295de4d5a -->

For Koreo spec'ing question 31, I choose A.

### Turn 070 — Assistant

<!-- node_id: cd7920b7-3175-4598-85d9-76ca7296a05a message_id: cd7920b7-3175-4598-85d9-76ca7296a05a -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-031 — Locked</badge>

**Decision: No overlapping moves within a single track.**

- Move blocks on the same track cannot overlap.
- Gaps between moves are permitted.
- Simultaneous movements require separate tracks.
- Moves on different tracks may overlap freely.
- Moves may still cross musical section and phrase boundaries (S-008).

This simplifies both editing and choreography-sheet rendering.

---

## Question 32 — How should Koreo handle conflicting edits?

Suppose a track already contains a move spanning counts 1–8. You drag another move onto counts 5–12.

Since overlaps are prohibited, Koreo needs a predictable response.

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Reject the overlap (recommended)**

      <text color="secondary" size="sm">The dragged move cannot be placed where another move exists. Koreo shows the conflict and leaves the existing choreography unchanged.</text>
    </radio>
    <radio value="B">
      **B. Automatically trim**

      <text color="secondary" size="sm">Koreo shortens the dragged move or an existing move to eliminate the overlap.</text>
    </radio>
    <radio value="C">
      **C. Ripple subsequent moves**

      <text color="secondary" size="sm">Koreo shifts later moves to make room for the dragged block, potentially moving much of the choreography.</text>
    </radio>
    <radio value="D">
      **D. Ask how to resolve the conflict**

      <text color="secondary" size="sm">Offer to cancel, trim, or shift moves whenever a conflict occurs.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 32, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A for V1**. It's predictable, protects existing work, and avoids introducing complicated automatic editing behavior.

We can eventually add explicit commands for inserting space, shifting moves, or replacing a range without making ordinary drag-and-drop unpredictable.

### Turn 071 — User

<!-- node_id: 5b83a9a9-bdde-411f-ad5f-cb0ac48c93f7 message_id: 5b83a9a9-bdde-411f-ad5f-cb0ac48c93f7 -->

For Koreo spec'ing question 32, I choose D.

### Turn 072 — Assistant

<!-- node_id: c83293f4-25da-494e-8254-751c2841ca99 message_id: c83293f4-25da-494e-8254-751c2841ca99 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-032 — Locked</badge>

**Decision: Ask the user how to resolve overlapping moves.**

When an editing operation would create an overlap within a single track, Koreo offers three choices:

- **Cancel:** Reject the operation and preserve the existing choreography.
- **Trim:** Adjust move boundaries to eliminate the overlap.
- **Shift:** Move affected blocks to make room for the new move.

No existing move is silently modified.

The entire operation, including any automatic adjustments, must be undoable as one action (S-024).

The precise behavior of trimming and shifting will be defined during implementation planning.

---

## Question 33 — How should Koreo handle moves crossing a musical insertion point?

This clarifies S-028, where we decided that inserting or deleting musical counts should offer optional ripple editing.

Suppose a move spans beats 13–20, and you insert four beats at beat 17.

If the user chooses to shift the choreography, what happens to that move?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Preserve the move's duration**

      <text color="secondary" size="sm">The move remains at beats 13–20. Only moves starting at or after beat 17 are shifted.</text>
    </radio>
    <radio value="B">
      **B. Extend the crossing move (recommended)**

      <text color="secondary" size="sm">The move becomes beats 13–24, spanning the inserted time. Subsequent moves shift forward by four beats.</text>
    </radio>
    <radio value="C">
      **C. Split the crossing move**

      <text color="secondary" size="sm">The original move is split into two blocks, with the inserted counts creating a gap between them.</text>
    </radio>
    <radio value="D">
      **D. Ask separately for crossing moves**

      <text color="secondary" size="sm">The user chooses how to handle each move that crosses the insertion point.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 33, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** for consistency with typical timeline editing: inserting time extends a region that spans the insertion point.

However, A is also defensible for choreography, because a move's duration may have a specific musical meaning that shouldn't change automatically.

Which behavior feels most natural?

### Turn 073 — User

<!-- node_id: 93f15cce-8fc9-4774-9c72-94b452f1b776 message_id: 93f15cce-8fc9-4774-9c72-94b452f1b776 -->

For Koreo spec'ing question 33, I choose D.

### Turn 074 — Assistant

<!-- node_id: 1473933f-b34c-444c-8ad7-370d2fe8dc20 message_id: 1473933f-b34c-444c-8ad7-370d2fe8dc20 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-033 — Locked</badge>

**Decision: Explicit handling of moves crossing an insertion point.**

When the user inserts musical counts and chooses ripple editing (S-028), Koreo identifies any move spanning the insertion point.

For each affected move, the user can choose to:

- **Preserve:** Keep the move's original position and duration.
- **Extend:** Increase its duration to span the inserted counts.
- **Split:** Divide the move into two blocks separated by the inserted counts.

Moves beginning after the insertion point shift according to the ripple operation.

The user must explicitly approve changes to crossing moves. No automatic modification is permitted.

For efficiency, the interface may offer an *Apply to all* option when multiple moves are affected.

---

## Question 34 — How should musical sections be numbered and identified?

We previously agreed that repeated A sections are independent (S-030). However, the user needs to distinguish them when navigating or editing.

For example, a song might have the structure `Intro – A – A – B – A – Interlude – A – A – B – A`.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Labels only**

      <text color="secondary" size="sm">Sections display their names (A, B, Intro, etc.). Repeated names are allowed without additional identifiers.</text>
    </radio>
    <radio value="B">
      **B. Labels + occurrence numbers (recommended)**

      <text color="secondary" size="sm">Repeated sections can be displayed as A1, A2, B1, A3, etc., while retaining their original musical labels.</text>
    </radio>
    <radio value="C">
      **C. Global section numbering**

      <text color="secondary" size="sm">Every section receives a sequential number (1, 2, 3...), independently of its musical label.</text>
    </radio>
    <radio value="D">
      **D. User-defined identifiers**

      <text color="secondary" size="sm">Users manually assign unique names or numbers to sections, with no automatic numbering.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 34, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, with occurrence numbers treated as optional display information. Internally, each section should have a stable identifier independent of its label.

That would let dancers see a clean `AABA` structure while still allowing the editor to distinguish the first A from the third A.

### Turn 075 — User

<!-- node_id: 8c634f75-63f4-4e35-9292-d2032f8b8bb4 message_id: 8c634f75-63f4-4e35-9292-d2032f8b8bb4 -->

B. But labels should be editable strings and not fixed strings or id (at least front facing)

### Turn 076 — Assistant

<!-- node_id: a43fb654-1f12-4294-b2fb-b5b426a708c7 message_id: a43fb654-1f12-4294-b2fb-b5b426a708c7 -->

## Koreo — Spec’ing Interview

<badge color="success"><icon name="check" inline/> S-034 — Locked</badge>

**Decision: Editable section labels with optional automatic occurrence numbering.**

- Section labels are unrestricted, user-editable strings, such as `A`, `B`, `Intro`, `Solo`, or `Breakdown`.
- Repeated labels are allowed.
- Koreo can automatically distinguish occurrences (`A1`, `A2`, `A3`).
- Occurrence numbering is optional in the user interface and choreography sheet.
- Internally, each section has a stable, unique identifier independent of its label.
- Renaming a section does not affect its timing, subdivisions, or associated choreography.

The important distinction is that **`A` is a user-defined label, not a special section type**.

---

## Question 35 — How should repeated choreography be handled?

We've established that repeated musical sections are independent. However, choreography itself often repeats.

Suppose couples A and B perform the same 32-count sequence three times during a song.

Should Koreo offer a way to reuse that choreography?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Manual duplication only**

      <text color="secondary" size="sm">Users can copy and paste individual move blocks. No special handling of multi-move sequences.</text>
    </radio>
    <radio value="B">
      **B. Copy/paste ranges of moves (recommended)**

      <text color="secondary" size="sm">Select several consecutive moves, copy them, and paste them at another musical position, preserving relative timing and durations.</text>
    </radio>
    <radio value="C">
      **C. Linked choreography patterns**

      <text color="secondary" size="sm">Define a reusable sequence once and place instances throughout the song. Editing the original updates every linked instance.</text>
    </radio>
    <radio value="D">
      **D. Both independent copies and linked patterns**

      <text color="secondary" size="sm">Users choose between ordinary duplication and linked reusable choreography patterns.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 35, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. Copying entire sequences will save considerable time without introducing the complexity of linked patterns.

A reusable choreography library with linked sequences could follow in a later release, alongside the training-video functionality we've already discussed.

### Turn 077 — User

<!-- node_id: 4e9d5c0b-9d76-4057-ad6c-6fdfda6db491 message_id: 4e9d5c0b-9d76-4057-ad6c-6fdfda6db491 -->

For Koreo spec'ing question 35, I choose B.

### Turn 078 — Assistant

<!-- node_id: 18e9a49c-1632-4d59-bd6c-f2f7bf6cd181 message_id: 18e9a49c-1632-4d59-bd6c-f2f7bf6cd181 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-035 — Locked**
</row>

**Decision: Copy and paste ranges of choreography moves.**

For V1:

- Select one or multiple move blocks.
- Copy and paste them at another musical position.
- Preserve relative timing, durations, labels, and notes.
- Pasted moves are independent copies, not linked instances.
- Standard keyboard shortcuts (`Ctrl+C`, `Ctrl+V`) should work.
- Paste operations respect the no-overlap rule (S-031) and conflict-resolution behavior (S-032).

**Deferred:** Linked choreography patterns, reusable sequences, and shared editing of repeated choreography.

---

## Question 36 — Selecting moves across multiple tracks

We know users can copy sequences within a track. But suppose four couples are performing different choreography simultaneously, and you want to repeat an entire 32-count passage.

Should you be able to copy moves from several tracks together?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Single-track selection only**

      <text color="secondary" size="sm">Copy and paste move sequences one track at a time. Simpler selection and clipboard behavior.</text>
    </radio>
    <radio value="B">
      **B. Multi-track selection (recommended)**

      <text color="secondary" size="sm">Select a musical range across multiple tracks and copy all included moves together, preserving their relative timing and track assignments.</text>
    </radio>
    <radio value="C">
      **C. Entire-section duplication**

      <text color="secondary" size="sm">Select a musical section and duplicate all choreography within it across every track, without requiring manual multi-track selection.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 36, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, since multiple choreography tracks are already a V1 requirement. It would allow copying a complete passage involving several couples.

However, this is a convenience feature rather than a fundamental requirement. If multi-track selection significantly complicates the chosen UI framework, we could defer it while retaining single-track copy/paste.

### Turn 079 — User

<!-- node_id: aae3e24c-2b67-425a-8add-8c59934f1610 message_id: aae3e24c-2b67-425a-8add-8c59934f1610 -->

For Koreo spec'ing question 36, I choose B.

### Turn 080 — Assistant

<!-- node_id: 11bd9fa4-13cb-4c9e-95a7-2976c9519ca9 message_id: 11bd9fa4-13cb-4c9e-95a7-2976c9519ca9 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-036 — Locked**
</row>

**Decision: Multi-track selection and copy/paste are supported in V1.**

- Users can select multiple moves across multiple choreography tracks.
- Copying preserves move labels, notes, durations, relative timing, and source track assignments.
- Pasting places the selected choreography at a new musical position, preserving the relationships between tracks.
- Pasted moves are independent copies.
- Overlap conflicts are handled according to S-032.
- The complete paste operation is undoable as one action.

---

## Question 37 — What happens when a move crosses the boundary of a copied range?

Suppose you select counts 9–16 across several tracks, but one move runs from counts 5–12.

Should that partially intersecting move be included?

<box border radius="lg" padding={3} gap={2}>
  <text color="secondary" weight="medium" size="xs">EXAMPLE</text>
  <svg viewBox="0 0 340 105" width="100%" xmlns="http://www.w3.org/2000/svg">
    {#each [0,1,2,3,4] as i}
      <line x1={20+i*75} y1="17" x2={20+i*75} y2="94" stroke="currentColor" opacity={0.14}/>
    {/each}
    <rect x="95" y="30" width="150" height="64" fill="#60a5fa" opacity={0.16}/>
    <rect x="20" y="50" width="112.5" height="27" rx="4" fill="#64748b"/>
    <text x="76" y="67" fontSize="11" textAnchor="middle" fill="white">Move</text>
    <line x1="95" y1="26" x2="95" y2="94" stroke="#3b82f6" strokeWidth="1.5" strokeDasharray="4 3"/>
    <line x1="245" y1="26" x2="245" y2="94" stroke="#3b82f6" strokeWidth="1.5" strokeDasharray="4 3"/>
    {#each ["1","9","17","25","33"] as t,i}
      <text x={20+i*75} y="12" fontSize="11" fill="currentColor" textAnchor="middle">{t}</text>
    {/each}
    <text x="170" y="43" textAnchor="middle" fontSize="10" fill="#3b82f6">Selected range</text>
  </svg>
  <caption>The move begins before the selected range but ends inside it.</caption>
</box>

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Include only fully contained moves (recommended)**

      <text color="secondary" size="sm">A move must start and end within the selected range. Crossing moves are excluded unless explicitly selected.</text>
    </radio>
    <radio value="B">
      **B. Include any intersecting move**

      <text color="secondary" size="sm">Even a one-beat intersection includes the entire move in the copied sequence.</text>
    </radio>
    <radio value="C">
      **C. Trim crossing moves to the selection**

      <text color="secondary" size="sm">Copy only the portion of each move inside the selected range, creating shortened copies.</text>
    </radio>
    <radio value="D">
      **D. Ask when crossing moves exist**

      <text color="secondary" size="sm">Offer to exclude, include entirely, or trim crossing moves when copying a range.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 37, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A** for predictable copying without modifying move durations. Explicitly clicking a move would still allow copying it regardless of the selected musical range.

### Turn 081 — User

<!-- node_id: cf769320-779e-41b6-a1de-9617087bca67 message_id: cf769320-779e-41b6-a1de-9617087bca67 -->

We could have a CAD-type selection: if drag from left->right: all touching if drag right->left: all fully contained (or the other way around if there is a convention in these kind of apps)

### Turn 082 — Assistant

<!-- node_id: 1fb3bc5c-4027-4095-b02a-d2fac326a260 message_id: 1fb3bc5c-4027-4095-b02a-d2fac326a260 -->

## Koreo — Spec’ing Interview

**S-037 — Proposed decision: CAD-style directional selection**

That's a good fit for Koreo. CAD applications such as AutoCAD commonly use this convention:

<box gap={3}>
  <row align="center" gap={3}>
    <box flex="1" gap={1}>
      <svg viewBox="0 0 160 92" width="100%">
        <rect x="35" y="18" width="90" height="56" fill="#60a5fa" fillOpacity=".17" stroke="#2563eb" strokeWidth="1.5"/>
        <rect x="10" y="35" width="48" height="17" rx="3" fill="#64748b"/>
        <rect x="75" y="35" width="40" height="17" rx="3" fill="#2563eb"/>
        <rect x="119" y="35" width="32" height="17" rx="3" fill="#64748b"/>
        <path d="M35 83 H125" stroke="#2563eb" strokeWidth="1.5"/>
        <path d="M118 79 L125 83 L118 87" stroke="#2563eb" strokeWidth="1.5" fill="none"/>
      </svg>
      **Left → Right**
      <text color="secondary" size="sm">Window selection: only fully contained moves.</text>
    </box>
    <box flex="1" gap={1}>
      <svg viewBox="0 0 160 92" width="100%">
        <rect x="35" y="18" width="90" height="56" fill="#22c55e" fillOpacity=".13" stroke="#16a34a" strokeDasharray="5 3" strokeWidth="1.5"/>
        <rect x="10" y="35" width="48" height="17" rx="3" fill="#16a34a"/>
        <rect x="75" y="35" width="40" height="17" rx="3" fill="#16a34a"/>
        <rect x="119" y="35" width="32" height="17" rx="3" fill="#16a34a"/>
        <path d="M125 83 H35" stroke="#16a34a" strokeWidth="1.5"/>
        <path d="M42 79 L35 83 L42 87" stroke="#16a34a" strokeWidth="1.5" fill="none"/>
      </svg>
      **Right → Left**
      <text color="secondary" size="sm">Crossing selection: every move touched by the selection.</text>
    </box>
  </row>
</box>

This matches the established AutoCAD convention, so there's no need to reverse it.

### S-037 — Proposed specification

- Drag left-to-right: select only moves fully enclosed by the selection rectangle.
- Drag right-to-left: select all moves intersecting the rectangle, even partially.
- Use distinct visual feedback for the two modes.
- Selection can span multiple choreography tracks (S-036).
- Selected moves are copied in their entirety, without trimming.
- Individual move selection remains available.

One important distinction: this describes **spatial selection of move blocks**, not necessarily selecting a musical time range.

I recommend adopting this as S-037. It also eliminates the need for a separate dialog when copying moves that cross the selection boundary.

**Shall we lock S-037 with this convention?**

### Turn 083 — User

<!-- node_id: 8841309f-179e-45fb-8387-6e7c4598de3c message_id: 8841309f-179e-45fb-8387-6e7c4598de3c -->

yes

### Turn 084 — Assistant

<!-- node_id: eb4d12a8-8ecb-4902-8570-46f5f79cd475 message_id: eb4d12a8-8ecb-4902-8570-46f5f79cd475 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-037 — Locked**
</row>

**Decision: CAD-style directional selection.**

- **Left → Right:** Select only move blocks fully enclosed by the selection rectangle.
- **Right → Left:** Select every move touched by the selection rectangle.
- The two selection modes have distinct visual feedback.
- Selection works across multiple choreography tracks.
- Selected moves are copied in full, without trimming.
- Individual move selection remains available.

This follows the established AutoCAD convention.

---

## Question 38 — How should Koreo handle zooming?

The waveform timeline and musical-grid editor may benefit from different zoom behaviors.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Buttons and zoom slider**

      <text color="secondary" size="sm">Zoom in/out using toolbar controls. Mouse wheel remains dedicated to scrolling.</text>
    </radio>
    <radio value="B">
      **B. CAD-style zoom controls (recommended)**

      <text color="secondary" size="sm">Mouse wheel zooms around the pointer, middle-button drag pans, and toolbar controls provide zoom-to-fit and zoom in/out.</text>
    </radio>
    <radio value="C">
      **C. Timeline-editor conventions**

      <text color="secondary" size="sm">Mouse wheel scrolls, Ctrl+wheel zooms around the pointer, Shift+wheel scrolls horizontally, and middle-button drag pans.</text>
    </radio>
    <radio value="D">
      **D. Configurable navigation**

      <text color="secondary" size="sm">Support both CAD-style and timeline-editor navigation through a user preference.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 38, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** given your preference for CAD-style interaction. Zooming around the pointer makes navigating a long song particularly efficient.

S-023 already establishes that the two editing views maintain independent zoom levels.

### Turn 085 — User

<!-- node_id: 49d018c1-5a1c-4389-beb5-fcb265ff3317 message_id: 49d018c1-5a1c-4389-beb5-fcb265ff3317 -->

For Koreo spec'ing question 38, I choose B.

### Turn 086 — Assistant

<!-- node_id: 5ee09de0-8644-4d81-b744-9edfbd6355d0 message_id: 5ee09de0-8644-4d81-b744-9edfbd6355d0 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-038 — Locked**
</row>

**Decision: CAD-style zoom and navigation.**

- **Mouse wheel:** Zoom in/out, centered on the pointer.
- **Middle-button drag:** Pan the editing viewport.
- **Toolbar:** Zoom in, zoom out, and zoom-to-fit.
- Both waveform and musical-grid editing views support these controls.
- Each view retains its own zoom level (S-023).
- Zooming and panning do not modify choreography data or create undo-history entries.

---

## Question 39 — How should Koreo display multiple choreography tracks?

Suppose a project contains six tracks for different dancers, couples, or movement categories.

How should those tracks appear in the editor?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. All tracks visible**

      <text color="secondary" size="sm">Every track is displayed as a separate row. Users scroll vertically to navigate larger projects.</text>
    </radio>
    <radio value="B">
      **B. Collapsible tracks (recommended)**

      <text color="secondary" size="sm">Tracks appear as rows, but users can collapse individual tracks to reduce clutter. All tracks remain independently editable.</text>
    </radio>
    <radio value="C">
      **C. One active track at a time**

      <text color="secondary" size="sm">Users select which choreography track to display. Other tracks remain hidden until selected.</text>
    </radio>
    <radio value="D">
      **D. Track groups**

      <text color="secondary" size="sm">Tracks can be organized into collapsible groups, such as Couples, Footwork, or Arms, in addition to individual visibility controls.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 39, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. Collapsible tracks provide a useful balance between readability and simplicity.

Track grouping (D) is potentially valuable, but introduces another level of organization that may not be necessary for the first release.

### Turn 087 — User

<!-- node_id: 45baab4b-af64-4159-8ad8-608938b8a03e message_id: 45baab4b-af64-4159-8ad8-608938b8a03e -->

For Koreo spec'ing question 39, I choose B.

### Turn 088 — Assistant

<!-- node_id: b4f796b6-1389-46a4-b0c5-5c7853fab894 message_id: b4f796b6-1389-46a4-b0c5-5c7853fab894 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-039 — Locked**
</row>

**Decision: Collapsible choreography tracks.**

- Each choreography track occupies its own row in the editor.
- Tracks can be expanded or collapsed individually.
- Collapsed tracks retain their data and can be expanded at any time.
- Users can scroll vertically through the track list.
- Track headers remain identifiable when collapsed.
- Track grouping and nested track hierarchies are deferred beyond V1.

---

## Question 40 — How should tracks appear in the choreography sheet?

The editor may contain several tracks, but the choreography sheet is intended to be easy for dancers to read and print.

Suppose the project contains separate tracks for Couples A, B, and C.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Always show every track**

      <text color="secondary" size="sm">The choreography sheet includes all tracks, regardless of which tracks are currently collapsed in the editor.</text>
    </radio>
    <radio value="B">
      **B. Choose tracks for the sheet (recommended)**

      <text color="secondary" size="sm">Users select which tracks appear in the sheet. For example, print only Couple A's choreography or a combined sheet for all couples.</text>
    </radio>
    <radio value="C">
      **C. One sheet per track**

      <text color="secondary" size="sm">Each choreography track has its own sheet, with the shared musical structure shown alongside it.</text>
    </radio>
    <radio value="D">
      **D. Multiple saved sheet configurations**

      <text color="secondary" size="sm">Create named layouts such as Full Choreography, Couple A, or Instructors, each with its own track selection and presentation settings.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 40, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. It supports both individual dancer sheets and a complete choreography overview without introducing a full layout-management system.

Track selection for the sheet should be independent of whether tracks are collapsed in the editor (S-039).

### Turn 089 — User

<!-- node_id: dcec2e4f-d0f3-40a6-b456-1341a9e7db98 message_id: dcec2e4f-d0f3-40a6-b456-1341a9e7db98 -->

For Koreo spec'ing question 40, I choose B.

### Turn 090 — Assistant

<!-- node_id: 854e7039-5e4c-4761-bf2e-b5bf6b254485 message_id: 854e7039-5e4c-4761-bf2e-b5bf6b254485 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-040 — Locked**
</row>

**Decision: User-selectable choreography tracks in the sheet.**

- Users choose which choreography tracks appear in the sheet.
- The sheet can display one, several, or all tracks.
- Musical structure remains visible regardless of track selection.
- Track selection applies to the on-screen sheet, PDF export, and Excel export.
- Sheet visibility is independent of track collapse state in the editor (S-039).
- Multiple named sheet configurations are deferred beyond V1.

---

## Question 41 — How should the choreography sheet wrap?

Unlike the timeline editor, the choreography sheet should resemble musical notation, where a long song is divided into horizontal lines.

The question is **where Koreo should start a new line**.

<box border radius="lg" padding={3} gap={2}>
  <text weight="medium" size="xs" color="secondary">ILLUSTRATIVE SHEET LAYOUT</text>
  <box gap={2}>
    {#each [["Intro","A1","A2","B1"],["A3","Break","A4","Outro"]] as line}
      <grid columns={4} gap={1}>
        {#each line as section}
          <grid-item>
            <box background="surface-secondary" radius="sm" padding={2} align="center">
              <text size="sm" weight="medium">{section}</text>
              <text size="3xs" color="tertiary">8 counts</text>
            </box>
          </grid-item>
        {/each}
      </grid>
    {/each}
  </box>
  <caption>Each row represents a line of choreography notation, with selected tracks displayed underneath the musical structure.</caption>
</box>

{@body const [choice,setChoice] = DIL.useState("C")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Fixed number of counts per line**

      <text color="secondary" size="sm">For example, every 32 counts starts a new line, even if that splits a musical section.</text>
    </radio>
    <radio value="B">
      **B. Wrap at musical section boundaries**

      <text color="secondary" size="sm">Keep sections together whenever possible. Line lengths may vary to accommodate them.</text>
    </radio>
    <radio value="C">
      **C. Automatic layout with manual breaks (recommended)**

      <text color="secondary" size="sm">Koreo automatically wraps the sheet based on available width and musical boundaries. Users can insert explicit line breaks to improve readability.</text>
    </radio>
    <radio value="D">
      **D. Fully manual line layout**

      <text color="secondary" size="sm">Users decide exactly which musical regions appear on each line, with no automatic wrapping.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 41, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **C** because the sheet must work both on screen and when exported to PDF or Excel. Automatic wrapping provides a useful starting point, while manual line breaks give choreographers control over presentation.

The line breaks would be **presentation metadata**, not changes to musical timing or choreography.

### Turn 091 — User

<!-- node_id: 5f8017d0-646f-45bd-be97-f5f494993340 message_id: 5f8017d0-646f-45bd-be97-f5f494993340 -->

For Koreo spec'ing question 41, I choose C.

### Turn 092 — Assistant

<!-- node_id: 83b9dbdf-ffc8-4edc-af4f-fca87b280667 message_id: 83b9dbdf-ffc8-4edc-af4f-fca87b280667 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-041 — Locked**
</row>

**Decision: Automatic sheet wrapping with manual line breaks.**

- Koreo automatically wraps choreography notation according to available width.
- Musical section boundaries are preferred when choosing where to wrap.
- Users can insert and remove manual line breaks.
- Manual breaks are presentation metadata; they do not alter musical timing or choreography.
- The on-screen sheet, PDF, and Excel exports follow the same layout rules, subject to their respective page and width constraints.
- Manual breaks take precedence over automatic wrapping.

---

## Question 42 — How should musical time be represented horizontally in the sheet?

Consider a musical phrase containing an eight-count section followed by a four-count section.

Should the eight-count section occupy twice as much horizontal space?

<box border radius="lg" padding={3} gap={3}>
  <text weight="medium" color="secondary" size="xs">TWO POSSIBLE LAYOUTS</text>
  <box gap={1}>
    **Proportional to duration**
    <row gap={1}>
      <box flex={2} background="surface-secondary" padding={3} radius="sm" align="center">
        <text weight="medium" size="sm">A · 8 counts</text>
      </box>
      <box flex={1} background="surface-tertiary" padding={3} radius="sm" align="center">
        <text size="sm">B · 4</text>
      </box>
    </row>
  </box>
  <box gap={1}>
    **Equal section widths**
    <row gap={1}>
      <box flex={1} background="surface-secondary" padding={3} radius="sm" align="center">
        <text weight="medium" size="sm">A · 8 counts</text>
      </box>
      <box flex={1} background="surface-tertiary" padding={3} radius="sm" align="center">
        <text size="sm">B · 4 counts</text>
      </box>
    </row>
  </box>
</box>

{@body const [choice,setChoice] = DIL.useState("C")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Strictly proportional**

      <text color="secondary" size="sm">Every beat has the same width. Longer musical regions always occupy proportionally more space.</text>
    </radio>
    <radio value="B">
      **B. Equal section widths**

      <text color="secondary" size="sm">Each section gets the same horizontal width, regardless of duration. Counts are distributed inside it.</text>
    </radio>
    <radio value="C">
      **C. Proportional with readability adjustments (recommended)**

      <text color="secondary" size="sm">Widths follow musical duration, but Koreo can expand crowded regions to fit move labels and notes.</text>
    </radio>
    <radio value="D">
      **D. User-configurable spacing**

      <text color="secondary" size="sm">Users choose proportional or equal-width layout, with optional manual width adjustments.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 42, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **C**. The sheet's purpose is to communicate choreography clearly, so perfectly proportional spacing shouldn't make labels unreadable.

The editing timeline can remain strictly time-proportional, while the sheet uses more flexible notation spacing.

### Turn 093 — User

<!-- node_id: 900669f5-56e7-4e08-b59a-71bf5f8c469c message_id: 900669f5-56e7-4e08-b59a-71bf5f8c469c -->

For Koreo spec'ing question 42, I choose C.

### Turn 094 — Assistant

<!-- node_id: 577ca2f7-bfc4-48bb-9a48-f9b707d72c5c message_id: 577ca2f7-bfc4-48bb-9a48-f9b707d72c5c -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-042 — Locked**
</row>

**Decision: Proportional musical spacing with readability adjustments.**

- Horizontal spacing in the choreography sheet is based on musical duration.
- Longer regions generally occupy more space than shorter regions.
- Koreo may expand regions to accommodate move labels and maintain readability.
- All choreography tracks share the same horizontal musical alignment.
- Expanding a region affects presentation only, never musical timing.
- The waveform timeline remains strictly proportional to time.

This establishes an important distinction: **the timeline is a timing tool; the choreography sheet is a readable notation tool.**

---

## Question 43 — How should detailed move notes appear in the sheet?

S-010 establishes that each move has a short label and optional detailed notes. We now need to decide how much of that information belongs in the choreography sheet.

For example, a move might have:

**Label:** `Swing Out`

**Notes:** `Leader initiates rotation on count 3. Followers maintain connection through count 6.`

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Short labels only**

      <text color="secondary" size="sm">The sheet displays move names. Detailed notes remain available in the editor's properties panel but are excluded from the sheet and exports.</text>
    </radio>
    <radio value="B">
      **B. Labels with optional expanded notes (recommended)**

      <text color="secondary" size="sm">The sheet displays short labels by default. Users can enable detailed notes, which expand the necessary space beneath moves.</text>
    </radio>
    <radio value="C">
      **C. Labels with numbered footnotes**

      <text color="secondary" size="sm">Moves remain compact, with detailed explanations collected in a numbered notes section below the sheet or at the end of the document.</text>
    </radio>
    <radio value="D">
      **D. Always show full notes**

      <text color="secondary" size="sm">Every move displays its complete description directly in the sheet, increasing space requirements but keeping all information visible.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 43, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It allows a compact dancer-facing sheet while also supporting a more detailed instructional version.

The same visibility setting should apply to the on-screen sheet, PDF export, and Excel export.

### Turn 095 — User

<!-- node_id: 9cba907e-d905-4209-8b21-3b72bb180046 message_id: 9cba907e-d905-4209-8b21-3b72bb180046 -->

For Koreo spec'ing question 43, I choose B.

### Turn 096 — Assistant

<!-- node_id: b03e81c8-18fd-4197-8729-dac937489e3c message_id: b03e81c8-18fd-4197-8729-dac937489e3c -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-043 — Locked**
</row>

**Decision: Move labels with optionally expanded notes.**

- The choreography sheet displays short move labels by default.
- Users can enable or disable detailed notes in the sheet.
- When enabled, notes appear alongside their corresponding moves, with the layout expanding as needed.
- The same notes-visibility setting applies to the on-screen sheet, PDF export, and Excel export.
- Hiding notes does not delete them from the project.
- Detailed notes remain accessible in the editor regardless of sheet settings.

---

## Question 44 — How should Koreo handle page breaks when printing?

We've established automatic line wrapping and optional manual line breaks (S-041). But a printed choreography sheet also needs **page breaks**.

For example, a 4-minute choreography might span several pages.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Fully automatic pagination**

      <text color="secondary" size="sm">Koreo divides the sheet into pages according to paper size, margins, and content height. No manual page breaks.</text>
    </radio>
    <radio value="B">
      **B. Automatic pagination with manual page breaks (recommended)**

      <text color="secondary" size="sm">Koreo handles pagination automatically, but users can insert page breaks at musical boundaries to control printed layout.</text>
    </radio>
    <radio value="C">
      **C. User-defined pages**

      <text color="secondary" size="sm">Users manually assign musical passages to pages. Koreo scales each page's contents to fit.</text>
    </radio>
    <radio value="D">
      **D. Continuous sheet only**

      <text color="secondary" size="sm">Koreo produces a continuous sheet and leaves pagination to the PDF or Excel printing system.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 44, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It keeps printing straightforward while allowing a choreographer to start a new page at a natural musical boundary, such as a new verse or chorus.

As with manual line breaks, page breaks would be **presentation metadata**, not changes to the song or choreography.

### Turn 097 — User

<!-- node_id: 9220ad98-8c6c-4069-8ff2-98a9278723de message_id: 9220ad98-8c6c-4069-8ff2-98a9278723de -->

For Koreo spec'ing question 44, I choose B.

### Turn 098 — Assistant

<!-- node_id: 1de8e9d7-0082-46a8-a7e7-7b155999506a message_id: 1de8e9d7-0082-46a8-a7e7-7b155999506a -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-044 — Locked**
</row>

**Decision: Automatic pagination with optional manual page breaks.**

- Koreo automatically divides the choreography sheet into pages according to paper size, margins, and content.
- Users can insert and remove manual page breaks at musical boundaries.
- Manual page breaks take precedence over automatic pagination.
- A musical line should not be split across pages unless unavoidable.
- PDF and Excel exports should respect the same page-break intentions.
- Page breaks are presentation metadata and never affect musical timing or choreography.

---

## Question 45 — How should the sheet handle paper size and orientation?

Since the choreography sheet is a primary deliverable, its printed format matters. A sheet containing several choreography tracks may require significantly more horizontal space than one containing a single track.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Fixed format**

      <text color="secondary" size="sm">Use one standard paper size and orientation, such as Letter landscape, for every sheet.</text>
    </radio>
    <radio value="B">
      **B. Configurable paper size and orientation (recommended)**

      <text color="secondary" size="sm">Support Letter and A4, portrait and landscape. Koreo automatically reflows the sheet for the selected format.</text>
    </radio>
    <radio value="C">
      **C. Automatic orientation**

      <text color="secondary" size="sm">Users select paper size, but Koreo chooses portrait or landscape based on the number of tracks and available content width.</text>
    </radio>
    <radio value="D">
      **D. Full print-layout controls**

      <text color="secondary" size="sm">Configurable paper size, orientation, margins, scaling, and page dimensions, with a live print-layout preview.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 45, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. Letter and A4 cover common printing needs, and both orientations allow the same choreography to be presented differently depending on the number of tracks.

Advanced print-layout controls can be deferred until we've validated the actual sheet rendering and exports.

### Turn 099 — User

<!-- node_id: ca85fba1-2786-4635-b2ec-7c268d365b2a message_id: ca85fba1-2786-4635-b2ec-7c268d365b2a -->

For Koreo spec'ing question 45, I choose B.

### Turn 100 — Assistant

<!-- node_id: f606ef52-f403-4bac-b7e7-f6e95232bce5 message_id: f606ef52-f403-4bac-b7e7-f6e95232bce5 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-045 — Locked**
</row>

**Decision: Configurable paper size and orientation.**

- Support **Letter** and **A4** paper sizes in V1.
- Support **portrait** and **landscape** orientations.
- Koreo automatically reflows the choreography sheet to fit the selected format.
- The same settings apply to PDF and Excel exports.
- Manual line breaks (S-041) and page breaks (S-044) remain respected.
- Advanced margin, scaling, and custom paper-size controls are deferred.

---

## Question 46 — How should choreography tracks be ordered?

Suppose a project has tracks for Couple A, Couple B, Footwork, and Arms.

The order in which these appear may matter, especially when printing a choreography sheet.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Creation order**

      <text color="secondary" size="sm">Tracks appear in the order they were created. Their position cannot be changed.</text>
    </radio>
    <radio value="B">
      **B. Manual drag-and-drop ordering (recommended)**

      <text color="secondary" size="sm">Users reorder tracks by dragging their headers. The order is shared by the editor and choreography sheet.</text>
    </radio>
    <radio value="C">
      **C. Separate editor and sheet ordering**

      <text color="secondary" size="sm">Users can arrange tracks differently in the editor and the sheet, allowing different layouts for editing and printing.</text>
    </radio>
    <radio value="D">
      **D. Automatic sorting**

      <text color="secondary" size="sm">Tracks are sorted alphabetically by their editable names, with no manual reordering.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 46, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. Manual ordering is intuitive and straightforward to implement. A single shared order also avoids unnecessary configuration complexity.

The sheet would display the selected tracks (S-040) in that order, regardless of which tracks are collapsed in the editor.

### Turn 101 — User

<!-- node_id: 24737f5f-5216-4024-b885-a74d0309d912 message_id: 24737f5f-5216-4024-b885-a74d0309d912 -->

For Koreo spec'ing question 46, I choose B.

### Turn 102 — Assistant

<!-- node_id: 29864366-9fd9-4168-8be7-2ddd5b117540 message_id: 29864366-9fd9-4168-8be7-2ddd5b117540 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-046 — Locked**
</row>

**Decision: Manual drag-and-drop track ordering.**

- Users can reorder choreography tracks by dragging their headers.
- The track order is shared between the editing views and the choreography sheet.
- The sheet displays selected tracks (S-040) in their defined order.
- Collapsing or hiding a track does not change its position.
- Track order is saved in the project.
- Reordering tracks is undoable (S-024).

---

## Question 47 — How should Koreo handle move colors?

Colors could help dancers quickly identify movements, categories, or choreography tracks.

For example, you might want to distinguish footwork, turns, transitions, and lifts visually.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. One neutral color for all moves**

      <text color="secondary" size="sm">Keep the interface simple. Move blocks are visually distinguished by their labels and track positions.</text>
    </radio>
    <radio value="B">
      **B. Color per track (recommended)**

      <text color="secondary" size="sm">Each track has an editable color, applied to its moves in the editor and sheet. Individual moves do not have separate colors.</text>
    </radio>
    <radio value="C">
      **C. Color per move**

      <text color="secondary" size="sm">Each move can have its own color, independent of the track, allowing users to categorize individual movements.</text>
    </radio>
    <radio value="D">
      **D. Track colors with optional move overrides**

      <text color="secondary" size="sm">Moves inherit their track's color by default, but users can override individual move colors when needed.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 47, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. Track colors are useful for distinguishing couples or movement categories without adding much complexity.

One consideration: PDF and Excel exports should remain understandable when printed in grayscale. Color should assist readability, not be the only way to distinguish tracks.

### Turn 103 — User

<!-- node_id: ef854edc-8bbf-42b1-9c3a-157e994fe4b6 message_id: ef854edc-8bbf-42b1-9c3a-157e994fe4b6 -->

B. plus alterning shades to help readability

### Turn 104 — Assistant

<!-- node_id: 8649d414-78cd-4cd9-9f57-f52e347f11e4 message_id: 8649d414-78cd-4cd9-9f57-f52e347f11e4 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-047 — Locked**
</row>

**Decision: Track colors with alternating shades for readability.**

- Each choreography track has an editable base color.
- Move blocks inherit their track's color.
- Alternating lighter and darker shades help distinguish adjacent move blocks.
- Shading alternates within each track, independently of other tracks.
- Colors and shading are reflected in the editor, choreography sheet, PDF, and Excel exports.
- Text, borders, and spacing must remain readable in grayscale.
- Individual move color overrides are deferred beyond V1.

For example, consecutive moves on a blue track could alternate between two subtle blue shades without losing their shared track identity.

---

## Question 48 — How should Koreo display empty counts?

A choreography track may contain gaps where no move has been assigned.

Should the choreography sheet explicitly represent those gaps?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Leave gaps blank**

      <text color="secondary" size="sm">Empty musical intervals appear as whitespace between move blocks.</text>
    </radio>
    <radio value="B">
      **B. Show subtle empty-count cells (recommended)**

      <text color="secondary" size="sm">The sheet retains a visible count grid, with lightly outlined cells indicating intervals without choreography.</text>
    </radio>
    <radio value="C">
      **C. Automatically label gaps as rests**

      <text color="secondary" size="sm">Empty intervals display a label such as “Rest” or “Pause,” even when no move has been assigned.</text>
    </radio>
    <radio value="D">
      **D. Configurable gap display**

      <text color="secondary" size="sm">Users choose between blank space, visible count cells, or automatic rest labels.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 48, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. Empty choreography does not necessarily mean a dancer is resting; it may simply be unfinished. A subtle grid makes missing annotations visible without assigning them a musical meaning.

It also preserves the visual alignment of counts across multiple tracks.

### Turn 105 — User

<!-- node_id: 05f0988d-11d3-4705-a35a-2d2e3caa0b40 message_id: 05f0988d-11d3-4705-a35a-2d2e3caa0b40 -->

For Koreo spec'ing question 48, I choose B.

### Turn 106 — Assistant

<!-- node_id: a45674dd-7602-444d-9dcd-74fcb4e125f6 message_id: a45674dd-7602-444d-9dcd-74fcb4e125f6 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-048 — Locked**
</row>

**Decision: Display subtle empty-count cells.**

- Empty intervals remain visible through a lightly outlined musical grid.
- Empty cells contain no automatic labels.
- An empty interval means **no choreography has been assigned**, not necessarily that the dancer is resting.
- Count alignment remains consistent across tracks.
- The same principle applies to the on-screen sheet, PDF, and Excel exports.
- Empty cells remain available for adding new moves.

---

## Question 49 — How should move labels behave when a block is too narrow?

Suppose a move named `Reverse Charleston Variation` occupies only two counts. Its label may not fit inside the available width.

We've already agreed that the sheet may expand regions for readability (S-042), but the interactive timeline needs a separate rule.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Truncate labels**

      <text color="secondary" size="sm">Display something like `Reverse Char…` when space is insufficient. The full label appears on hover or selection.</text>
    </radio>
    <radio value="B">
      **B. Truncate in timeline, wrap in sheet (recommended)**

      <text color="secondary" size="sm">Keep timeline blocks compact with truncated labels. Allow labels to wrap onto multiple lines in the choreography sheet.</text>
    </radio>
    <radio value="C">
      **C. Always show complete labels**

      <text color="secondary" size="sm">Automatically increase block height or width to display full labels in both views.</text>
    </radio>
    <radio value="D">
      **D. User-configurable label display**

      <text color="secondary" size="sm">Provide settings for truncation, wrapping, and label visibility separately in each view.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 49, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. The timeline should prioritize accurate timing and efficient editing, while the sheet should prioritize readability.

This also avoids changing a move's apparent duration merely because its label is long.

### Turn 107 — User

<!-- node_id: 4983ccee-e67b-4264-b6f2-fbf84f53b918 message_id: 4983ccee-e67b-4264-b6f2-fbf84f53b918 -->

For Koreo spec'ing question 49, I choose B.

### Turn 108 — Assistant

<!-- node_id: 95bb596a-6208-4968-84ed-40effbb3b4bb message_id: 95bb596a-6208-4968-84ed-40effbb3b4bb -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-049 — Locked**
</row>

**Decision: Truncate labels in the timeline; wrap them in the choreography sheet.**

- **Timeline editor:** Truncate labels that exceed the available block width, using an ellipsis.
- The complete label remains accessible through a tooltip or by selecting the move.
- **Choreography sheet:** Wrap long labels onto multiple lines.
- Sheet layout expands as necessary to preserve readability (S-042).
- PDF and Excel exports preserve the complete labels.
- Text layout never changes a move's musical duration.

---

## Question 50 — How should move details be edited?

Each move has a short label and optional detailed notes (S-010). We need to define how users enter and modify that information.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Edit directly inside move blocks**

      <text color="secondary" size="sm">Double-click a move to edit its label in place. Detailed notes are edited through a separate dialog.</text>
    </radio>
    <radio value="B">
      **B. Inline labels + properties panel (recommended)**

      <text color="secondary" size="sm">Double-click to edit a label directly. Selecting a move opens or updates a properties panel containing its label, notes, and timing.</text>
    </radio>
    <radio value="C">
      **C. Properties panel only**

      <text color="secondary" size="sm">All move information is edited through a dedicated properties panel. No inline editing.</text>
    </radio>
    <radio value="D">
      **D. Dedicated move editor dialog**

      <text color="secondary" size="sm">Double-clicking a move opens a dialog with all editable properties, keeping the main interface uncluttered.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 50, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. Inline editing makes naming moves fast, while a persistent properties panel provides room for longer notes and precise timing adjustments.

This also fits the CAD-inspired editing conventions we've adopted for selection and navigation.

### Turn 109 — User

<!-- node_id: 04f240f3-1e53-4025-b582-1c33efcfc2f4 message_id: 04f240f3-1e53-4025-b582-1c33efcfc2f4 -->

For Koreo spec'ing question 50, I choose B.

### Turn 110 — Assistant

<!-- node_id: 586b260a-2ad0-47af-9720-62850472bb94 message_id: 586b260a-2ad0-47af-9720-62850472bb94 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-050 — Locked**
</row>

**Decision: Inline move labels with a properties panel.**

- Double-click a move block to edit its label directly.
- Selecting a move displays its properties in a dedicated panel.
- The panel provides editable fields for label, detailed notes, and timing.
- Timing can be adjusted numerically or through direct manipulation of move blocks.
- The properties panel updates when the selection changes.
- All edits participate in the shared undo/redo history (S-024).

---

## Question 51 — How should Koreo handle multiple selected moves in the properties panel?

With CAD-style selection (S-037), users can select several moves across multiple tracks. The properties panel needs to handle that situation.

For example, you select eight moves and want to shift all of them by two counts.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Single-move properties only**

      <text color="secondary" size="sm">The properties panel displays information only when exactly one move is selected. Multiple selections can still be copied, moved, or deleted.</text>
    </radio>
    <radio value="B">
      **B. Basic multi-editing (recommended)**

      <text color="secondary" size="sm">With multiple moves selected, the panel shows the selection count and offers shared operations such as shifting all selected moves by a specified number of counts.</text>
    </radio>
    <radio value="C">
      **C. Full batch property editing**

      <text color="secondary" size="sm">Edit shared fields across selected moves, including labels, notes, timing, and other properties, similar to a CAD properties inspector.</text>
    </radio>
    <radio value="D">
      **D. No multi-editing in V1**

      <text color="secondary" size="sm">The properties panel is disabled for multiple selections. Batch editing is deferred entirely.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 51, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. Shifting several moves together is useful for choreography adjustments, while full batch editing would add complexity without an obvious immediate benefit.

Any batch timing operation must preserve relative timing and respect the overlap-conflict rules established in S-031 and S-032.

### Turn 111 — User

<!-- node_id: eea4bf9d-c21c-4e76-8b58-93b36696f988 message_id: eea4bf9d-c21c-4e76-8b58-93b36696f988 -->

For Koreo spec'ing question 51, I choose B.

### Turn 112 — Assistant

<!-- node_id: 1e139f2d-a3d2-46b8-af12-b48ef73094ed message_id: 1e139f2d-a3d2-46b8-af12-b48ef73094ed -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-051 — Locked**
</row>

**Decision: Basic multi-move editing through the properties panel.**

- When multiple moves are selected, the properties panel displays the number of selected moves.
- Users can shift all selected moves by a specified number of counts.
- Relative timing between selected moves is preserved.
- Moves retain their original track assignments.
- Conflicts with unselected moves follow S-032.
- The entire batch operation is undoable as one action.
- Batch editing of labels and detailed notes is deferred beyond V1.

---

## Question 52 — How should Koreo display musical count numbers?

A choreography sheet needs to communicate *when* moves occur, but there are several useful ways to number counts.

For example, consider a song with four consecutive eight-count phrases.

<box border radius="lg" padding={3} gap={3}>
  <box gap={1}>
    <text weight="medium" size="sm">Local counts</text>
    <grid columns={4} gap={1}>
      {#each [1,2,3,4] as n}
        <grid-item>
          <box background="surface-secondary" radius="sm" padding={2} align="center" gap={1}>
            <text color="secondary" size="2xs">Phrase {n}</text>
            <text size="xs" weight="medium">1 2 3 4 5 6 7 8</text>
          </box>
        </grid-item>
      {/each}
    </grid>
  </box>
  <box gap={1}>
    <text weight="medium" size="sm">Continuous counts</text>
    <grid columns={4} gap={1}>
      {#each ["1–8","9–16","17–24","25–32"] as range}
        <grid-item>
          <box background="surface-secondary" radius="sm" padding={2} align="center">
            <text weight="medium" size="xs">{range}</text>
          </box>
        </grid-item>
      {/each}
    </grid>
  </box>
</box>

{@body const [choice,setChoice] = DIL.useState("C")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Local counts only**

      <text color="secondary" size="sm">Restart numbering at 1 for each configured count group, such as 1–8 or 1–6.</text>
    </radio>
    <radio value="B">
      **B. Continuous counts only**

      <text color="secondary" size="sm">Number beats sequentially from the song's musical origin, without restarting.</text>
    </radio>
    <radio value="C">
      **C. Both numbering systems (recommended)**

      <text color="secondary" size="sm">Show local counts prominently, with optional continuous beat numbers for precise navigation and communication.</text>
    </radio>
    <radio value="D">
      **D. Hierarchical numbering**

      <text color="secondary" size="sm">Use phrase-and-count notation such as 1.1–1.8, 2.1–2.8, etc., identifying both the phrase and the beat within it.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 52, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **C**. Dancers generally think in local six- or eight-count phrases, but continuous numbering is useful when editing, synchronizing tracks, and discussing exact positions.

This builds on S-029, which established musical beats as the fundamental timing unit and configurable dance count groups.

### Turn 113 — User

<!-- node_id: 5872516b-cea5-459e-bc41-9899ec0a59f8 message_id: 5872516b-cea5-459e-bc41-9899ec0a59f8 -->

For Koreo spec'ing question 52, I choose C.

### Turn 114 — Assistant

<!-- node_id: dad82f01-a39a-4297-a190-55001bcdbdea message_id: dad82f01-a39a-4297-a190-55001bcdbdea -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-052 — Locked**
</row>

**Decision: Local dance counts with optional continuous beat numbering.**

- Local counts (e.g., `1–8` or `1–6`) are the primary notation.
- Local numbering restarts at the boundaries of configured count groups (S-029).
- Continuous beat numbers can be displayed as a secondary reference.
- Both numbering systems refer to the same underlying musical positions.
- The continuous numbering option applies consistently to the on-screen sheet, PDF, and Excel exports.
- Count labels are presentation information and do not change musical timing.

---

## Question 53 — How should Koreo handle pickup beats?

Some songs begin with a short musical introduction before the first complete count group. In musical terminology, this can be called an *anacrusis* or pickup.

For example, a song might contain two pickup beats followed by the first full eight-count phrase.

<box border radius="lg" padding={3} gap={2}>
  <row gap={1} align="stretch">
    <box flex={1} background="surface-tertiary" padding={2} radius="sm" align="center" justify="center" gap={1}>
      <text size="2xs" color="secondary">Pickup</text>
      <text weight="medium" size="sm">7 8</text>
    </box>
    <box flex={4} background="surface-secondary" padding={2} radius="sm" align="center" justify="center" gap={1}>
      <text size="2xs" color="secondary">First full phrase</text>
      <text weight="medium" size="sm">1 2 3 4 5 6 7 8</text>
    </box>
  </row>
</box>

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. No special pickup handling**

      <text color="secondary" size="sm">Users represent the opening beats as an ordinary musical region. Count numbering starts at 1 wherever the song begins.</text>
    </radio>
    <radio value="B">
      **B. Configurable count origin (recommended)**

      <text color="secondary" size="sm">Users designate where the first full count group begins. Earlier beats can be displayed as pickup counts without shifting the audio or choreography.</text>
    </radio>
    <radio value="C">
      **C. Explicit pickup region type**

      <text color="secondary" size="sm">Koreo provides a dedicated pickup region with its own count numbering and special handling in the musical structure.</text>
    </radio>
    <radio value="D">
      **D. Manually editable count labels**

      <text color="secondary" size="sm">Users can override displayed count numbers anywhere in the song, including pickup beats and irregular passages.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 53, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It handles pickups without introducing a special musical-region type.

Importantly, the **count origin** would be distinct from the BPM calibration anchor (S-004): one determines how counts are labeled, while the other determines how beats align with audio.

### Turn 115 — User

<!-- node_id: 30c504ad-89d4-48c4-b845-5adce2cd1045 message_id: 30c504ad-89d4-48c4-b845-5adce2cd1045 -->

For Koreo spec'ing question 53, I choose B.

### Turn 116 — Assistant

<!-- node_id: 0a64d2c2-5c4f-477e-b008-9adfb1ab8324 message_id: 0a64d2c2-5c4f-477e-b008-9adfb1ab8324 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-053 — Locked**
</row>

**Decision: Configurable musical count origin.**

- Users can designate where the first complete dance-count group begins.
- Beats preceding that position are treated as pickup beats.
- Pickup counts may be displayed using the ending numbers of the preceding group (e.g., `7, 8` before `1–8`).
- The count origin is independent of the BPM calibration anchor (S-004).
- Changing the count origin updates count labels without moving audio, musical regions, or choreography.
- Continuous beat numbering remains available independently (S-052).

---

## Question 54 — How should Koreo handle irregular count groups?

Although many dances use six- or eight-count phrases, choreography can include irregular passages.

For example:

<box border radius="lg" padding={3} gap={2}>
  <row gap={1}>
    {#each [{n:8,w:8},{n:8,w:8},{n:4,w:4},{n:8,w:8}] as p,i}
      <box flex={p.w} background="surface-secondary" padding={{x:1,y:3}} radius="sm" align="center" gap={1}>
        <text weight="medium" size="sm">{p.n}</text>
        <text color="secondary" size="2xs">counts</text>
      </box>
    {/each}
  </row>
  <caption>A passage with 8 + 8 + 4 + 8 counts.</caption>
</box>

We've already established configurable count groups (S-029). The remaining question is whether that configuration applies globally or can vary throughout the song.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. One global count-group size**

      <text color="secondary" size="sm">Choose six or eight counts for the entire song. Irregular passages are represented through musical subdivisions without changing count numbering.</text>
    </radio>
    <radio value="B">
      **B. Per-region count groups (recommended)**

      <text color="secondary" size="sm">Set a default group size for the song, but allow individual musical regions to use a different number of counts.</text>
    </radio>
    <radio value="C">
      **C. Explicit count-group sequence**

      <text color="secondary" size="sm">Define a sequence of count groups, such as `8, 8, 4, 8, 6, 6`, independently of musical-region boundaries.</text>
    </radio>
    <radio value="D">
      **D. Fully independent count grid**

      <text color="secondary" size="sm">Create and edit count-group boundaries anywhere on the timeline, independently of the hierarchical musical structure.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 54, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. It supports irregular choreography while keeping count-group definitions attached to the musical structure we already have.

Option D offers greater flexibility, but would introduce another independently editable layer of timing information.

### Turn 117 — User

<!-- node_id: bc9895a7-1f2a-4284-a056-1423aa888ff9 message_id: bc9895a7-1f2a-4284-a056-1423aa888ff9 -->

For Koreo spec'ing question 54, I choose B.

### Turn 118 — Assistant

<!-- node_id: 5bcf68bf-2644-4930-8bc7-8b82508f73cc message_id: 5bcf68bf-2644-4930-8bc7-8b82508f73cc -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-054 — Locked**
</row>

**Decision: Configurable count-group sizes per musical region.**

- Each song has a default count-group size, such as 6 or 8 beats.
- Individual musical regions can override that default.
- For example, a passage may use `8 + 8 + 4 + 8`.
- Local count numbering follows each region's configured groups.
- Overrides affect count grouping and notation, not the underlying beat timing.
- Existing choreography remains in place when a region's count grouping changes.
- Regions without overrides inherit the song's default.

This supports irregular musical passages without introducing a separate count-group editing layer.

---

## Question 55 — What happens when a musical region's duration doesn't divide evenly into its count groups?

Suppose a musical region spans **20 beats**, with a configured group size of **8**.

That produces:

<box border radius="lg" padding={3} gap={2}>
  <row gap={1}>
    <box flex={8} background="rgba(59,130,246,0.14)" border radius="sm" padding={{x:1,y:3}} align="center" gap={1}>
      **1–8**
      <text color="secondary" size="2xs">Full group</text>
    </box>
    <box flex={8} background="rgba(59,130,246,0.14)" border radius="sm" padding={{x:1,y:3}} align="center" gap={1}>
      **1–8**
      <text color="secondary" size="2xs">Full group</text>
    </box>
    <box flex={4} background="rgba(245,158,11,0.13)" border radius="sm" padding={{x:1,y:3}} align="center" gap={1}>
      **1–4**
      <text color="secondary" size="2xs">Partial</text>
    </box>
  </row>
  <caption>20 beats divided into groups of 8 leaves a final group of 4.</caption>
</box>

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Allow partial groups (recommended)**

      <text color="secondary" size="sm">Display two complete eight-count groups followed by a four-count group. No special action required.</text>
    </radio>
    <radio value="B">
      **B. Require exact multiples**

      <text color="secondary" size="sm">A region must contain a whole number of count groups. Users must resize the region or change its group size.</text>
    </radio>
    <radio value="C">
      **C. Automatically adjust the final group**

      <text color="secondary" size="sm">Koreo distributes beats among groups to avoid short remainders, such as using 8 + 6 + 6 instead.</text>
    </radio>
    <radio value="D">
      **D. Ask how to handle the remainder**

      <text color="secondary" size="sm">When a remainder exists, users choose whether to allow it, adjust the region, or define custom groups.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 55, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A**. Musical structures frequently contain shortened phrases, and the editor should accommodate them without forcing changes to timing.

A partial group would simply be a valid musical subdivision, not an error.

### Turn 119 — User

<!-- node_id: ca29405e-4106-414b-b7e4-add563863ab4 message_id: ca29405e-4106-414b-b7e4-add563863ab4 -->

For Koreo spec'ing question 55, I choose A.

### Turn 120 — Assistant

<!-- node_id: 6b978e16-5feb-47d6-bf54-c442829cba96 message_id: 6b978e16-5feb-47d6-bf54-c442829cba96 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-055 — Locked**
</row>

**Decision: Allow partial count groups.**

- Musical regions do not need to contain an exact multiple of their configured count-group size.
- A 20-beat region using eight-count groups is displayed as `8 + 8 + 4`.
- The final partial group is valid and requires no warning or confirmation.
- Partial groups preserve their actual duration; Koreo does not redistribute beats.
- Local count numbering restarts at each group boundary.
- Choreography timing remains unchanged.

---

## Question 56 — How should count grouping behave across musical region boundaries?

Suppose a song uses eight-count groups, but one musical region ends after only four beats.

Should the next region restart at count 1, or continue the unfinished eight-count group?

<box border radius="lg" padding={3} gap={3}>
  <box gap={1}>
    <text weight="medium" size="sm">Restart at each region</text>
    <grid columns={2} gap={1}>
      <grid-item>
        <box background="surface-secondary" radius="sm" padding={3} align="center" gap={1}>
          <text size="2xs" color="secondary">Region A · 4 beats</text>
          **1 2 3 4**
        </box>
      </grid-item>
      <grid-item>
        <box background="surface-secondary" radius="sm" padding={3} align="center" gap={1}>
          <text size="2xs" color="secondary">Region B · 4 beats</text>
          **1 2 3 4**
        </box>
      </grid-item>
    </grid>
  </box>
  <box gap={1}>
    <text weight="medium" size="sm">Continue across regions</text>
    <grid columns={2} gap={1}>
      <grid-item>
        <box background="surface-secondary" radius="sm" padding={3} align="center" gap={1}>
          <text size="2xs" color="secondary">Region A · 4 beats</text>
          **1 2 3 4**
        </box>
      </grid-item>
      <grid-item>
        <box background="surface-secondary" radius="sm" padding={3} align="center" gap={1}>
          <text size="2xs" color="secondary">Region B · 4 beats</text>
          **5 6 7 8**
        </box>
      </grid-item>
    </grid>
  </box>
</box>

{@body const [choice,setChoice] = DIL.useState("C")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Always restart**

      <text color="secondary" size="sm">Every musical region starts at count 1, even when the preceding region ends mid-group.</text>
    </radio>
    <radio value="B">
      **B. Always continue**

      <text color="secondary" size="sm">Count groups continue across region boundaries until complete, unless the count-group size changes.</text>
    </radio>
    <radio value="C">
      **C. Configurable restart per region (recommended)**

      <text color="secondary" size="sm">Each region can either restart at count 1 or continue the preceding count sequence. Restart is the default.</text>
    </radio>
    <radio value="D">
      **D. Restart only at top-level sections**

      <text color="secondary" size="sm">Major sections restart numbering, while subdivisions within those sections continue the count sequence.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 56, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **C** because the musical hierarchy is flexible: some region boundaries represent major phrases, while others are merely subdivisions.

Allowing an explicit restart setting avoids making every structural boundary automatically reset the dancer's count.

### Turn 121 — User

<!-- node_id: 7dedc764-e4f2-44dd-b349-27c191d30624 message_id: 7dedc764-e4f2-44dd-b349-27c191d30624 -->

For Koreo spec'ing question 56, I choose C.

### Turn 122 — Assistant

<!-- node_id: 6381d4f3-0e2b-415d-b22a-0f8d522c6581 message_id: 6381d4f3-0e2b-415d-b22a-0f8d522c6581 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-056 — Locked**
</row>

**Decision: Configurable count restart at musical region boundaries.**

- Each musical region can either restart local counting at `1` or continue counting from the preceding region.
- **Restart is the default.**
- The setting is independent of the region's editable label.
- Subdivisions may continue counting across boundaries when configured.
- Changing this setting affects count labels, not beat timing or choreography.
- The behavior is consistent across the editor, choreography sheet, PDF, and Excel exports.

This completes the basic rules for musical count numbering, including pickups, irregular groups, and region boundaries.

---

## Question 57 — How should Koreo handle snapping while dragging moves?

We've already established whole-beat snapping as the default (S-011). However, users may occasionally need to position a move between beats.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Always snap to beats**

      <text color="secondary" size="sm">Move boundaries must align with the beat grid. No off-grid placement in V1.</text>
    </radio>
    <radio value="B">
      **B. Temporary snap override (recommended)**

      <text color="secondary" size="sm">Moves snap to whole beats by default. Holding a modifier key while dragging temporarily disables snapping for finer positioning.</text>
    </radio>
    <radio value="C">
      **C. Global snap toggle**

      <text color="secondary" size="sm">Provide a toolbar button to enable or disable snapping. The selected mode remains active until changed.</text>
    </radio>
    <radio value="D">
      **D. Both temporary override and global toggle**

      <text color="secondary" size="sm">Users can turn snapping on or off globally and temporarily invert the current mode using a modifier key.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 57, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. It keeps beat-aligned choreography the normal behavior without preventing precise adjustments.

One consideration: allowing off-grid placement means the underlying timing model must support fractional beat positions, even if the interface normally displays whole counts.

### Turn 123 — User

<!-- node_id: 654ce7de-9ba2-42ef-880d-820be55a3034 message_id: 654ce7de-9ba2-42ef-880d-820be55a3034 -->

For Koreo spec'ing question 57, I choose B.

### Turn 124 — Assistant

<!-- node_id: 2ce7e92e-2caf-48f1-aa5e-c07a73595915 message_id: 2ce7e92e-2caf-48f1-aa5e-c07a73595915 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-057 — Locked**
</row>

**Decision: Whole-beat snapping with a temporary override.**

- Move boundaries snap to whole beats by default.
- Holding a modifier key while dragging temporarily disables snapping.
- Releasing the modifier restores normal snapping.
- Off-grid positions are permitted and stored precisely, including fractional beats.
- This applies to moving and resizing choreography blocks.
- Subbeat grid snapping remains a possible later enhancement (S-011).

---

## Question 58 — How should Koreo handle move timing when BPM changes?

Suppose you've annotated an entire song at 120 BPM, then discover that the correct tempo is 118 BPM.

The beat grid will shift relative to the audio. What should happen to existing moves?

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Preserve musical positions (recommended)**

      <text color="secondary" size="sm">A move starting at beat 17 remains at beat 17. Its playback time changes to follow the corrected beat grid.</text>
    </radio>
    <radio value="B">
      **B. Preserve audio timestamps**

      <text color="secondary" size="sm">A move starting at 8.0 seconds remains at 8.0 seconds, even if its musical beat position changes.</text>
    </radio>
    <radio value="C">
      **C. Ask whenever BPM changes**

      <text color="secondary" size="sm">Choose whether to preserve musical positions or audio timestamps each time the tempo is adjusted.</text>
    </radio>
    <radio value="D">
      **D. Different behavior for structure and choreography**

      <text color="secondary" size="sm">Musical regions preserve beat positions, while choreography moves preserve their absolute audio timestamps.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 58, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A** because Koreo is fundamentally a beat-based choreography planner.

Correcting the BPM should realign the existing choreography to the audio without changing its musical count positions. This also keeps musical regions and choreography consistent.

### Turn 125 — User

<!-- node_id: 0dc6e518-1a66-4579-bbbd-4ab80235cdb9 message_id: 0dc6e518-1a66-4579-bbbd-4ab80235cdb9 -->

For Koreo spec'ing question 58, I choose A.

### Turn 126 — Assistant

<!-- node_id: 5d4a6a09-b543-4b5d-9c71-b1b038ce0ecd message_id: 5d4a6a09-b543-4b5d-9c71-b1b038ce0ecd -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-058 — Locked**
</row>

**Decision: Preserve musical positions when BPM changes.**

- Musical regions and choreography moves retain their beat positions and durations.
- Changing BPM recalculates their corresponding audio timestamps.
- The beat grid and playback synchronization update accordingly.
- Fractional beat positions remain supported (S-057).
- Changing BPM does not alter count-group definitions or section boundaries.
- BPM changes participate in undo/redo (S-024).

For example, a move starting at beat 17 remains at beat 17 when BPM changes from 120 to 118. Its position in seconds changes.

---

## Question 59 — What happens when the beat anchor moves?

S-004 allows users to place an anchor at a musical downbeat to align the beat grid with the audio.

Unlike changing BPM, moving the anchor shifts the entire beat grid without changing its spacing.

Suppose a move starts at beat 17, and you shift the anchor forward by 0.5 seconds.

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Preserve musical positions (recommended)**

      <text color="secondary" size="sm">The move remains at beat 17 and shifts 0.5 seconds forward with the beat grid. Musical structure and choreography stay aligned.</text>
    </radio>
    <radio value="B">
      **B. Preserve audio timestamps**

      <text color="secondary" size="sm">The move stays at its original audio time, and its beat position changes relative to the shifted grid.</text>
    </radio>
    <radio value="C">
      **C. Ask each time**

      <text color="secondary" size="sm">Choose whether to preserve musical positions or audio timestamps whenever the anchor is moved.</text>
    </radio>
    <radio value="D">
      **D. Separate structure and choreography behavior**

      <text color="secondary" size="sm">Musical structure follows the anchor, but choreography remains fixed to audio timestamps.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 59, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A**, consistent with S-058. Both BPM and anchor corrections would adjust the mapping between musical beats and audio time, without rewriting the choreography.

This gives Koreo a simple underlying rule: **musical positions are authoritative; audio timestamps are derived from calibration.**

### Turn 127 — User

<!-- node_id: de86ad23-49fc-4316-bdde-5e3b462938a0 message_id: de86ad23-49fc-4316-bdde-5e3b462938a0 -->

For Koreo spec'ing question 59, I choose A.

### Turn 128 — Assistant

<!-- node_id: ed7f1264-1b15-44d7-a535-6b6ab1c07598 message_id: ed7f1264-1b15-44d7-a535-6b6ab1c07598 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-059 — Locked**
</row>

**Decision: Preserve musical positions when the beat anchor moves.**

- Musical regions and choreography moves retain their beat positions and durations.
- Moving the beat anchor shifts their corresponding audio timestamps.
- The entire beat grid moves together without changing its spacing.
- No choreography blocks are repositioned relative to the musical grid.
- Anchor adjustments participate in undo/redo (S-024).

Together, S-058 and S-059 establish a consistent principle:

**Musical beat positions are authoritative. Audio timestamps are derived from BPM and anchor calibration.**

---

## Question 60 — What happens when a musical region is resized?

We've established that choreography moves are independent of musical regions (S-013).

Suppose section A occupies beats 1–32, and you resize it to end at beat 40. Section B originally starts at beat 33.

Should Koreo automatically adjust neighboring musical regions?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Independent boundaries**

      <text color="secondary" size="sm">Resizing section A changes only A. Gaps or overlaps between musical regions are permitted.</text>
    </radio>
    <radio value="B">
      **B. Shared boundaries (recommended)**

      <text color="secondary" size="sm">Dragging the boundary between A and B changes the end of A and the start of B together. Later sections remain in place.</text>
    </radio>
    <radio value="C">
      **C. Ripple resizing**

      <text color="secondary" size="sm">Extending A shifts B and every subsequent section forward, preserving their original durations.</text>
    </radio>
    <radio value="D">
      **D. Choose resize behavior**

      <text color="secondary" size="sm">Users choose between adjusting the shared boundary, shifting subsequent regions, or resizing independently.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 60, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. It keeps adjacent musical regions contiguous without unexpectedly shifting the rest of the song.

Importantly, this operation would modify the **musical structure only**. Choreography moves would remain at their original beat positions unless the user explicitly performs a ripple insertion or deletion (S-028).

### Turn 129 — User

<!-- node_id: 2fe1f9db-c27f-429d-b936-baad73f5a688 message_id: 2fe1f9db-c27f-429d-b936-baad73f5a688 -->

For Koreo spec'ing question 60, I choose D.

### Turn 130 — Assistant

<!-- node_id: d02cd057-251f-49c7-8402-e5d8e0ddaf32 message_id: d02cd057-251f-49c7-8402-e5d8e0ddaf32 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-060 — Locked**
</row>

**Decision: User-selectable musical region resize behavior.**

When resizing a musical region, Koreo supports three operations:

- **Shared boundary:** Move the boundary between adjacent regions, changing both durations without moving later regions.
- **Ripple resize:** Extend or shorten a region and shift subsequent regions accordingly, preserving their durations.
- **Independent resize:** Change only the selected region, allowing gaps or overlaps between musical regions.

The user explicitly selects the intended operation. Koreo must not silently shift unrelated regions.

All three operations are undoable. Choreography remains at its original beat positions unless a separate ripple operation affecting choreography is explicitly requested (S-028).

---

## Question 61 — How should overlapping musical regions appear?

S-060 now permits independently resized musical regions to overlap. We need to define what that means visually.

For example, section A might occupy beats 1–32 while section B occupies beats 25–48.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Overlap in the same row**

      <text color="secondary" size="sm">Draw overlapping regions in one lane, using transparency or outlines to reveal their boundaries.</text>
    </radio>
    <radio value="B">
      **B. Separate overlapping regions into lanes (recommended)**

      <text color="secondary" size="sm">Keep regions on the same hierarchy level, but display overlapping intervals on separate visual lanes so both remain readable.</text>
    </radio>
    <radio value="C">
      **C. Flag overlaps as structural conflicts**

      <text color="secondary" size="sm">Allow overlaps temporarily during editing, but highlight them as unresolved conflicts that users should correct.</text>
    </radio>
    <radio value="D">
      **D. Prevent overlaps at completion**

      <text color="secondary" size="sm">Independent resizing may temporarily overlap regions, but Koreo requires users to resolve the overlap before completing the operation.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 61, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, since S-060 explicitly allows independent resizing and overlaps. Separate visual lanes preserve access to both regions without treating an intentional overlap as an error.

One architectural implication: **hierarchical containment and chronological adjacency are different concepts**. We should avoid assuming that sibling musical regions always form a non-overlapping partition of their parent.

### Turn 131 — User

<!-- node_id: d357921c-df63-4bb3-900c-87c71b4d318e message_id: d357921c-df63-4bb3-900c-87c71b4d318e -->

Sorry i revert: musical section should not overlap. At least for V1.

### Turn 132 — Assistant

<!-- node_id: f7c16985-50b8-4419-9567-f59af7aebd44 message_id: f7c16985-50b8-4419-9567-f59af7aebd44 -->

## Koreo — Spec’ing Interview

**S-060 — Revised**

Agreed. Musical sections should form a coherent structure, not overlap accidentally.

**Updated decision for V1:**

- Musical regions at the same hierarchical level **cannot overlap**.
- **Shared boundary resize:** Adjusts the boundary between neighboring regions.
- **Ripple resize:** Changes a region's duration and shifts subsequent regions.
- **Independent resize:** Permitted only when it does not create an overlap. Gaps are allowed.
- Any operation that would create an overlap must be rejected or constrained.
- Choreography tracks remain independent and can cross musical section boundaries.

This supersedes the previous S-060 decision. **S-061 (overlap visualization) is no longer needed.**

One distinction worth preserving: a parent region naturally contains its child regions. That is hierarchical containment, not an overlap conflict.

---

## Question 61 — Should gaps between musical sections be allowed?

For example, section A ends at beat 32, while section B starts at beat 41, leaving eight beats without a named section.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. No gaps**

      <text color="secondary" size="sm">Musical sections must cover the entire song continuously. Unassigned beats are not permitted.</text>
    </radio>
    <radio value="B">
      **B. Allow unassigned gaps (recommended)**

      <text color="secondary" size="sm">Sections cannot overlap, but portions of the song may remain unassigned. Gaps are shown as empty musical-grid regions.</text>
    </radio>
    <radio value="C">
      **C. Automatically create unnamed sections**

      <text color="secondary" size="sm">Whenever a gap appears, Koreo creates an unlabeled section covering it.</text>
    </radio>
    <radio value="D">
      **D. Allow gaps while editing, require completion before export**

      <text color="secondary" size="sm">Users may leave gaps temporarily, but the musical structure must be complete to produce a choreography sheet.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 61, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It supports incremental planning: users can annotate the chorus before identifying every other part of the song.

An unassigned musical interval would be distinct from an empty choreography interval (S-048).

### Turn 133 — User

<!-- node_id: 0bae3b1a-296f-4171-a97e-abbb3ea873f2 message_id: 0bae3b1a-296f-4171-a97e-abbb3ea873f2 -->

For Koreo spec'ing question 61, I choose B.

### Turn 134 — Assistant

<!-- node_id: 05a84051-0411-4ff3-a789-8cb2d5954438 message_id: 05a84051-0411-4ff3-a789-8cb2d5954438 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-061 — Locked**
</row>

**Decision: Allow unassigned gaps between musical sections.**

- Musical regions at the same hierarchical level cannot overlap (revised S-060).
- Gaps between musical regions are permitted.
- Unassigned intervals appear as empty areas of the musical grid.
- Users can create or extend regions to fill those gaps later.
- Gaps do not prevent saving, playback, or exporting the choreography sheet.
- An unassigned musical interval is distinct from an empty choreography interval (S-048).

This supports building a song's structure incrementally without forcing users to annotate every passage.

---

## Question 62 — How should Koreo handle musical sections extending beyond the audio?

Suppose an imported song is 3 minutes long, but the user accidentally extends the final musical section beyond the end of the recording.

Should the musical grid be constrained by the audio duration?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Strict audio boundaries**

      <text color="secondary" size="sm">Musical sections and choreography moves cannot extend beyond the imported audio's duration.</text>
    </radio>
    <radio value="B">
      **B. Allow extensions with a warning (recommended)**

      <text color="secondary" size="sm">Users may create musical regions and moves beyond the audio's end. Koreo visually identifies the portion without audio.</text>
    </radio>
    <radio value="C">
      **C. Automatically extend the project timeline**

      <text color="secondary" size="sm">The project timeline grows to accommodate musical regions and moves beyond the audio, without displaying a warning.</text>
    </radio>
    <radio value="D">
      **D. Ask when exceeding audio duration**

      <text color="secondary" size="sm">Koreo asks for confirmation whenever an editing operation would extend beyond the end of the recording.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 62, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It supports planning an ending or transition before the final audio is available, while making it clear that no recording exists for that portion.

It also avoids treating the imported audio duration as a permanent limit on the choreography project.

### Turn 135 — User

<!-- node_id: fc8881a9-c6d6-4015-963f-cebf9e723bc1 message_id: fc8881a9-c6d6-4015-963f-cebf9e723bc1 -->

For Koreo spec'ing question 62, I choose B.

### Turn 136 — Assistant

<!-- node_id: adaddab3-6f70-448b-b8ec-e9facace5e87 message_id: adaddab3-6f70-448b-b8ec-e9facace5e87 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-062 — Locked**
</row>

**Decision: Allow musical regions and moves beyond the audio duration, with a visual warning.**

- Musical regions and choreography moves may extend beyond the imported recording.
- The project timeline expands to accommodate them.
- Portions beyond the audio duration are visually distinguished.
- Koreo indicates that no audio is available for those portions.
- Such content can be saved and included in the choreography sheet, PDF, and Excel exports.
- Audio playback stops at the end of the recording.
- No confirmation dialog is required for every extension.

This keeps the choreography project independent of the recording's exact duration.

---

## Question 63 — How should Koreo handle replacing the song's audio file?

Suppose you've already built a choreography using a rehearsal recording, then receive the final version of the song.

You want to replace the audio without losing the choreography.

The new recording may have a different beginning, duration, or tempo.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Replace audio and preserve calibration**

      <text color="secondary" size="sm">Replace the audio file but keep the existing BPM and beat anchor. Users manually recalibrate afterward if necessary.</text>
    </radio>
    <radio value="B">
      **B. Replace audio and offer recalibration (recommended)**

      <text color="secondary" size="sm">Preserve all musical regions and choreography at their beat positions, but offer to adjust BPM and anchor for the new recording.</text>
    </radio>
    <radio value="C">
      **C. Import as a new project**

      <text color="secondary" size="sm">Replacing audio creates a separate project containing a copy of the existing structure and choreography.</text>
    </radio>
    <radio value="D">
      **D. Multiple audio versions**

      <text color="secondary" size="sm">Store several recordings in the same project, each with its own BPM and anchor, and switch between them.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 63, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. It handles a common workflow without introducing multi-recording management.

This is consistent with S-058 and S-059: **musical positions remain authoritative**, while the mapping to audio time can be recalibrated.

### Turn 137 — User

<!-- node_id: a1cdd14a-3338-4b1b-878b-90a40533a415 message_id: a1cdd14a-3338-4b1b-878b-90a40533a415 -->

B+C

### Turn 138 — Assistant

<!-- node_id: 1e2c03f4-1823-4985-a322-60c73e8de0a4 message_id: 1e2c03f4-1823-4985-a322-60c73e8de0a4 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-063 — Locked (B + C)**
</row>

**Decision: Support audio replacement with recalibration, and offer project duplication.**

When replacing the audio, Koreo offers two workflows:

- **Replace in current project:** Preserve musical regions, choreography, and their beat positions. Offer BPM and anchor recalibration for the new recording.
- **Create a new project from existing:** Duplicate the project, then replace the audio in the copy. The original project remains unchanged.

Both workflows preserve musical positions (S-058, S-059). The new audio is embedded in the resulting project (S-019).

Multiple audio versions within one project remain outside V1 scope.

---

## Question 64 — What happens to choreography when a musical section is deleted?

Suppose section B covers beats 33–64 and contains several choreography moves.

You delete section B from the musical structure.

Should those choreography moves remain?

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Preserve choreography (recommended)**

      <text color="secondary" size="sm">Delete only the musical section and its subdivisions. All choreography moves remain at their original beat positions.</text>
    </radio>
    <radio value="B">
      **B. Ask whether to delete associated choreography**

      <text color="secondary" size="sm">Offer to preserve the moves or delete moves within the section's interval.</text>
    </radio>
    <radio value="C">
      **C. Delete choreography automatically**

      <text color="secondary" size="sm">Remove all moves contained within the deleted section.</text>
    </radio>
    <radio value="D">
      **D. Prevent deletion of occupied sections**

      <text color="secondary" size="sm">Require the user to remove or relocate choreography before deleting the section.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 64, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A**, consistent with S-013: musical structure and choreography are independent.

Deleting a section would remove its structural annotation, not the underlying beats or the choreography.

This is distinct from **deleting musical counts** (S-028), which can explicitly trigger a ripple operation.

### Turn 139 — User

<!-- node_id: b4ecfb39-5d65-4266-a7d9-c2e28f288802 message_id: b4ecfb39-5d65-4266-a7d9-c2e28f288802 -->

For Koreo spec'ing question 64, I choose B.

### Turn 140 — Assistant

<!-- node_id: ee26b732-5855-499f-b684-73e3d98d3843 message_id: ee26b732-5855-499f-b684-73e3d98d3843 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-064 — Locked**
</row>

**Decision: Ask whether to preserve or delete choreography when deleting a musical section.**

When deleting a musical section, Koreo offers two choices:

- **Preserve choreography (default):** Remove the musical section and its subdivisions, leaving all choreography moves at their original beat positions.
- **Delete associated choreography:** Also remove choreography moves associated with the section's time interval.

The operation is undoable as a single action.

An important detail remains: how should Koreo treat moves that only *partially* overlap the deleted section?

---

## Question 65 — How should partially overlapping moves be handled?

Suppose section B occupies beats 33–64, but a choreography move spans beats 60–68.

The user deletes section B and selects **Delete associated choreography**.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Delete only fully contained moves**

      <text color="secondary" size="sm">Moves entirely inside section B are deleted. Moves crossing its boundaries remain unchanged.</text>
    </radio>
    <radio value="B">
      **B. Ask about crossing moves (recommended)**

      <text color="secondary" size="sm">Delete fully contained moves, then offer to preserve, delete entirely, or trim each partially overlapping move. Include an apply-to-all option.</text>
    </radio>
    <radio value="C">
      **C. Delete every intersecting move**

      <text color="secondary" size="sm">Any move touching section B is deleted entirely, even if it extends beyond the section.</text>
    </radio>
    <radio value="D">
      **D. Trim moves automatically**

      <text color="secondary" size="sm">Delete fully contained moves and remove only the overlapping portions of crossing moves, preserving portions outside section B.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 65, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It avoids silently destroying choreography outside the deleted section, while still letting the user clean up all associated moves.

This follows the same principle as S-033: **when an operation affects a move crossing a structural boundary, the user controls what happens to that move.**

### Turn 141 — User

<!-- node_id: 90627c2f-4a8b-42d8-99a2-5e90fa951536 message_id: 90627c2f-4a8b-42d8-99a2-5e90fa951536 -->

B. I think this is fine we ask all these question about modiofying the music structures after considerable move choreography has been done, but I think this will be relativelly rare. It does not mean we should not spec behavior, but song structures are relativelly simple, most of the time, for song used with dancing. We are not choreographing on very complexe time signatures or exotic , prog music

### Turn 142 — Assistant

<!-- node_id: c73448aa-e196-4ce1-a721-5e63806c986d message_id: c73448aa-e196-4ce1-a721-5e63806c986d -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-065 — Locked (B)**
</row>

When deleting a musical section and its associated choreography:

- Fully contained moves are deleted.
- For moves crossing the section boundary, Koreo asks whether to **preserve, delete entirely, or trim** each move.
- An **Apply to all** option avoids repetitive prompts.
- The entire operation is undoable.

### Your observation changes our priorities

I agree with your distinction. We've spent considerable time defining exceptional editing behaviors, but they shouldn't dictate the complexity of the main interface.

For Koreo V1, we should optimize for **ordinary dance music and straightforward choreography planning**, rather than sophisticated music-theory editing.

That suggests three design priorities:

1. **Fast initial setup:** Import a song, calibrate BPM, describe sections and count groups, start choreographing.
2. **Simple everyday editing:** Most work involves placing, labeling, copying, and adjusting moves.
3. **Safe exceptional editing:** Structural changes remain supported, but their more complex controls can stay out of the normal workflow.

This is a product-design priority, not a restriction against unusual songs.

---

## Question 66 — What should users see when starting a new project?

This is probably more consequential to V1 usability than another structural edge case.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Blank editor**

      <text color="secondary" size="sm">Open the timeline immediately. Users import audio, configure tempo, and create sections using the normal editing controls.</text>
    </radio>
    <radio value="B">
      **B. Guided initial setup (recommended)**

      <text color="secondary" size="sm">A lightweight sequence: import audio → set BPM and anchor → optionally describe song structure → enter editor. Every step can be revisited.</text>
    </radio>
    <radio value="C">
      **C. Single setup panel**

      <text color="secondary" size="sm">Show audio, BPM, anchor, and musical structure configuration together on one screen, then create the project.</text>
    </radio>
    <radio value="D">
      **D. Immediate audio-first editing**

      <text color="secondary" size="sm">Import audio and enter the editor immediately. Show contextual prompts for BPM, anchor, and structure only when needed.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 66, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, provided the setup is genuinely lightweight and skippable. The goal is to get from an MP3 to a usable choreography grid quickly, not to create a complicated project-configuration wizard.

### Turn 143 — User

<!-- node_id: 74ffd17c-ebd5-4841-b9f5-21223c7ff699 message_id: 74ffd17c-ebd5-4841-b9f5-21223c7ff699 -->

For Koreo spec'ing question 66, I choose B.

### Turn 144 — Assistant

<!-- node_id: 0abfc084-8bf8-45fd-817b-5b73c705f038 message_id: 0abfc084-8bf8-45fd-817b-5b73c705f038 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-066 — Locked**
</row>

**Decision: Guided initial project setup.**

Creating a new Koreo project follows a lightweight sequence:

1. **Import audio** — Select an MP3 or WAV file.
2. **Calibrate the beat grid** — Enter or tap BPM and position the beat anchor.
3. **Describe musical structure (optional)** — Define sections and count groups, manually or using simple repetition patterns.
4. **Enter the editor** — Start placing choreography moves.

All settings remain editable afterward. The setup must be skippable where practical and must not become a prerequisite for experimenting with the editor.

This establishes an important UX principle: **make the common workflow easy; keep advanced structural operations accessible but unobtrusive.**

---

## Question 67 — How should users create their initial song structure?

Imagine a typical dance song with an intro, several verses, choruses, and a bridge.

We already support manual region creation and generating sections from patterns (S-014). The question is how to make this convenient during initial setup.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Graphical creation only**

      <text color="secondary" size="sm">Users draw sections on the musical grid, resize them, and enter labels.</text>
    </radio>
    <radio value="B">
      **B. Simple sequence entry + graphical editing (recommended)**

      <text color="secondary" size="sm">Users can enter a sequence such as `Intro A A B A Outro`, choose a default length in counts for each section, and generate the structure. Then adjust it visually.</text>
    </radio>
    <radio value="C">
      **C. Structured section table**

      <text color="secondary" size="sm">Users add rows with section name, start beat, and duration. Koreo generates the grid from the table.</text>
    </radio>
    <radio value="D">
      **D. All three methods**

      <text color="secondary" size="sm">Support sequence entry, graphical drawing, and a structured table as equivalent ways to create and edit sections.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 67, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. For dance music, typing a simple section sequence is often faster than drawing every region individually.

For example, `A A B A` could generate four sections of 32 beats each, which you could subsequently rename, resize, or subdivide.

This is intentionally **manual structure definition**, not automatic song analysis.

### Turn 145 — User

<!-- node_id: 8944c23e-9556-43bf-b4bd-d95614ce306c message_id: 8944c23e-9556-43bf-b4bd-d95614ce306c -->

Yes B. And since editing song structure is mostly done way before choregraphy structure I see like a "modal" editing UX. We are not going to go back and forth between music and choreography... So song structure editing mode VS choreography ediuting mode

### Turn 146 — Assistant

<!-- node_id: ca189551-3312-45cc-8731-f6e511951eba message_id: ca189551-3312-45cc-8731-f6e511951eba -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-067 — Locked (B)**
</row>

**Decision:** Initial musical structure can be generated from a simple sequence such as `Intro A A B A Outro`, with configurable section lengths, followed by graphical editing.

### New design direction: Separate editing modes

I think this is an important simplification.

Rather than treating musical structure and choreography as two equally active editing layers, Koreo should distinguish between:

<box border radius="xl" gap={0}>
  <row align="start" padding={3} gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="music" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Structure mode**

      Define song sections, subdivisions, count groups, BPM, and beat alignment.

      Primary workflow: prepare the musical framework.
    </box>
  </row>
  <divider color="subtle"/>
  <row align="start" padding={3} gap={3}>
    <box background="surface-secondary" radius="lg" padding={2}>
      <icon name="footprints" size="lg"/>
    </box>
    <box flex="1" gap={1}>
      **Choreography mode**

      Place, resize, copy, and annotate moves against the existing musical structure.

      Primary workflow: develop the choreography.
    </box>
  </row>
</box>

Both modes operate on the same project and musical timeline. The distinction is **which elements are editable**, not which information exists.

This also means the many structural-editing safeguards we've specified can live in Structure mode without cluttering everyday choreography work.

---

## Question 68 — How should switching between modes work?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Two simple mode tabs**

      <text color="secondary" size="sm">Structure and Choreography are always available as tabs. Switching is immediate, with no additional confirmation.</text>
    </radio>
    <radio value="B">
      **B. Two modes with a structure-change warning (recommended)**

      <text color="secondary" size="sm">Switch freely between modes, but when modifying musical structure after choreography exists, show a contextual warning if the operation may affect moves.</text>
    </radio>
    <radio value="C">
      **C. Explicit structure locking**

      <text color="secondary" size="sm">After initial setup, the musical structure is locked. Users must deliberately unlock it to make structural changes.</text>
    </radio>
    <radio value="D">
      **D. Guided phase transition**

      <text color="secondary" size="sm">Users explicitly mark structure preparation complete before entering choreography mode. Returning to structure editing requires reopening that phase.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 68, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It preserves the workflow you described—structure first, choreography second—without imposing a rigid process.

Crucially, **switching modes itself would never be dangerous**. Only an actual structural edit that could affect existing choreography would require confirmation.

### Turn 147 — User

<!-- node_id: c9d10b12-e2cf-4f25-8388-9a4689d2ca21 message_id: c9d10b12-e2cf-4f25-8388-9a4689d2ca21 -->

For Koreo spec'ing question 68, I choose B.

### Turn 148 — Assistant

<!-- node_id: 4ebd3db4-f39b-4afc-b8cb-c2f0bbdf2be7 message_id: 4ebd3db4-f39b-4afc-b8cb-c2f0bbdf2be7 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-068 — Locked (B)**
</row>

**Decision: Two editing modes with contextual safeguards.**

- **Structure mode:** Edit musical sections, subdivisions, count groups, BPM, and beat calibration.
- **Choreography mode:** Edit movement tracks, blocks, labels, and notes.
- Users can switch modes freely without confirmation.
- Both modes share the same project, timeline, and playback.
- If a structural edit could affect existing choreography, Koreo displays an appropriate warning or resolution dialog, following S-028, S-033, S-060, and S-064.
- Simply entering Structure mode never triggers a warning.

The intended workflow is **structure first, choreography second**, while still allowing revisions.

---

## Question 69 — What should Structure mode look like after choreography has begun?

Suppose you've completed several sections of choreography but return to Structure mode to adjust a musical boundary.

Should the existing choreography remain visible?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Hide choreography**

      <text color="secondary" size="sm">Structure mode displays only musical sections and the beat grid. This gives maximum editing space and keeps the interface simple.</text>
    </radio>
    <radio value="B">
      **B. Show choreography as read-only (recommended)**

      <text color="secondary" size="sm">Choreography remains visible but cannot be selected or edited. This provides context while adjusting musical structure.</text>
    </radio>
    <radio value="C">
      **C. Optional choreography overlay**

      <text color="secondary" size="sm">Structure mode normally hides choreography, but users can toggle a read-only overlay when they need to see existing moves.</text>
    </radio>
    <radio value="D">
      **D. Show only a choreography occupancy indicator**

      <text color="secondary" size="sm">Instead of individual moves, show a compact indication of which musical intervals contain choreography.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 69, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, because it provides immediate context when revisiting the musical structure without allowing accidental move edits.

However, **C** may better match your preference for keeping the two workflows visually distinct and uncluttered.

### Turn 149 — User

<!-- node_id: 58b49b70-55d6-45a1-8baa-7eb7fe3169c1 message_id: 58b49b70-55d6-45a1-8baa-7eb7fe3169c1 -->

For Koreo spec'ing question 69, I choose B.

### Turn 150 — Assistant

<!-- node_id: 70595124-cbb2-4420-90a0-828eb86b52fc message_id: 70595124-cbb2-4420-90a0-828eb86b52fc -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-069 — Locked (B)**
</row>

**Decision: Choreography remains visible but read-only in Structure mode.**

- Existing choreography blocks and tracks remain visible for context.
- Musical sections and subdivisions are the active editing targets.
- Choreography cannot be selected, dragged, resized, or modified directly in Structure mode.
- Structural operations may still affect choreography through the explicit safeguards already defined.
- Switching back to Choreography mode restores normal move editing.

This reinforces the distinction between the two modes without hiding information that could be useful during structural revisions.

---

## Question 70 — What should Choreography mode show of the musical structure?

We have established that Structure mode shows choreography as read-only. Now we need the reverse behavior.

The musical structure is essential for planning moves, but its editing controls shouldn't clutter Choreography mode.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Full musical structure, read-only**

      <text color="secondary" size="sm">Display the complete hierarchy of sections and subdivisions above the choreography tracks, with all structural editing disabled.</text>
    </radio>
    <radio value="B">
      **B. Compact musical structure header (recommended)**

      <text color="secondary" size="sm">Show section labels, count groups, and beat markers in a compact header above the choreography tracks. The full hierarchy is available in Structure mode.</text>
    </radio>
    <radio value="C">
      **C. Configurable hierarchy depth**

      <text color="secondary" size="sm">Users choose how many levels of musical structure to display in Choreography mode, from a compact header to the full hierarchy.</text>
    </radio>
    <radio value="D">
      **D. Minimal beat grid only**

      <text color="secondary" size="sm">Display beat and count markers but hide musical section labels and subdivisions, maximizing space for choreography.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 70, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**. It keeps the musical reference visible while dedicating most of the screen to choreography.

The important principle is that **editing modes change the available tools, not the underlying musical timing or structure**.

### Turn 151 — User

<!-- node_id: 1deb507a-5b2b-4b74-821e-bc32903ef806 message_id: 1deb507a-5b2b-4b74-821e-bc32903ef806 -->

For Koreo spec'ing question 70, I choose B.

### Turn 152 — Assistant

<!-- node_id: 0cffd396-d7d8-49de-95be-4d7d237a8aef message_id: 0cffd396-d7d8-49de-95be-4d7d237a8aef -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-070 — Locked (B)**
</row>

**Decision: Compact musical structure header in Choreography mode.**

- Display section labels, count groups, and beat markers above choreography tracks.
- Keep the musical structure visible but read-only.
- Reserve most of the editing area for choreography.
- Full musical hierarchy editing remains in Structure mode.
- Both modes share the same underlying timing and musical structure.

This gives us a clear division:

**Structure mode:** Detailed musical hierarchy, with choreography visible but read-only.

**Choreography mode:** Compact musical reference, with choreography fully editable.

---

## Question 71 — How should users switch between the timeline and notation sheet?

We've already established two complementary views (S-022): a horizontal waveform timeline and a wrapped musical grid.

Now that we also have Structure and Choreography editing modes, we should avoid confusing **editing modes** with **views**.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Independent view tabs**

      <text color="secondary" size="sm">Timeline and Sheet are separate tabs within each editing mode. Switching views preserves the current mode.</text>
    </radio>
    <radio value="B">
      **B. Persistent view toggle (recommended)**

      <text color="secondary" size="sm">A clearly visible Timeline / Sheet toggle works independently of the Structure / Choreography mode switch. Both controls remain accessible.</text>
    </radio>
    <radio value="C">
      **C. Mode-specific views**

      <text color="secondary" size="sm">Structure mode defaults to the timeline, while Choreography mode defaults to the sheet. Users can switch views when necessary.</text>
    </radio>
    <radio value="D">
      **D. Dedicated Sheet workspace**

      <text color="secondary" size="sm">Structure and Choreography are editing modes, while Sheet is a separate presentation/export workspace rather than an editing view.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 71, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** because it keeps two concepts independent:

- **Mode:** What am I editing?
- **View:** How am I looking at it?

One important consideration: **D** would be simpler if the sheet is primarily intended for reviewing, printing, and exporting rather than directly editing choreography.

### Turn 153 — User

<!-- node_id: dbfc373c-54c9-47ba-9390-b49fdf32ece9 message_id: dbfc373c-54c9-47ba-9390-b49fdf32ece9 -->

For Koreo spec'ing question 71, I choose B.

### Turn 154 — Assistant

<!-- node_id: e4ac7431-b0cb-4888-8213-fc39a6c18ded message_id: e4ac7431-b0cb-4888-8213-fc39a6c18ded -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-071 — Locked (B)**
</row>

**Decision: Editing mode and display view are independent controls.**

- **Editing mode:** Structure / Choreography — determines what can be edited.
- **Display view:** Timeline / Sheet — determines how the project is presented.
- Both controls remain visible and accessible.
- Switching views preserves the current editing mode.
- Switching modes preserves the selected view.
- Both views use the same project data, selection, and playback position (S-023).

This gives Koreo four possible combinations without requiring four separate workspaces.

---

## Question 72 — Should the notation sheet be directly editable?

We previously established that Koreo has a wrapped musical grid with move labels, counts, and section boundaries.

However, we've not explicitly decided whether users can manipulate choreography blocks directly in that view.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Read-only sheet**

      <text color="secondary" size="sm">The sheet is exclusively for reviewing and exporting. All choreography editing happens in the timeline.</text>
    </radio>
    <radio value="B">
      **B. Full editing in both views (recommended)**

      <text color="secondary" size="sm">Users can select, create, resize, move, copy, and edit choreography blocks directly in either Timeline or Sheet view.</text>
    </radio>
    <radio value="C">
      **C. Limited sheet editing**

      <text color="secondary" size="sm">Users can select blocks, edit labels and notes, and copy/paste moves in Sheet view. Creating, resizing, or repositioning moves requires Timeline view.</text>
    </radio>
    <radio value="D">
      **D. Sheet-first editing**

      <text color="secondary" size="sm">The sheet is the primary choreography editor. Timeline view is mainly for audio synchronization and precise timing adjustments.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 72, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** based on the original concept of Koreo as a grid-based choreography editor.

However, this has a meaningful implementation cost: dragging and resizing moves across wrapped lines is more complicated than editing them on a continuous timeline.

**C would be a reasonable V1 simplification** if we want to prioritize getting a usable application sooner.

### Turn 155 — User

<!-- node_id: 3e5aa2f5-269e-4d11-a1ff-9d727bd8c264 message_id: 3e5aa2f5-269e-4d11-a1ff-9d727bd8c264 -->

For Koreo spec'ing question 72, I choose B.

### Turn 156 — Assistant

<!-- node_id: cb9ccc19-d68a-4689-90b3-a071955aed0e message_id: cb9ccc19-d68a-4689-90b3-a071955aed0e -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-072 — Locked (B)**
</row>

**Decision: Full choreography editing in both Timeline and Sheet views.**

- Users can create, select, move, resize, split, delete, and copy/paste choreography blocks in either view.
- Labels, notes, and timing properties are editable in both views.
- The same snapping, collision handling, and undo/redo rules apply.
- Edits immediately appear in the other view.
- Editing permissions still depend on the active Structure / Choreography mode.
- The Sheet view's wrapping and pagination must not change the underlying beat positions.

This establishes an important architectural requirement: **Timeline and Sheet are two editors of the same choreography model**, not an editor and a static report.

---

## Question 73 — How should dragging work across wrapped sheet lines?

Consider a choreography move near the end of one line. You want to drag it eight counts later, onto the next line.

Unlike the continuous timeline, the sheet wraps musical time across multiple rows.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Drag within a line only**

      <text color="secondary" size="sm">Moves can be dragged and resized within a single sheet line. Moving across lines requires cut/paste or numeric timing adjustments.</text>
    </radio>
    <radio value="B">
      **B. Continuous drag across lines (recommended)**

      <text color="secondary" size="sm">Dragging from the end of one line into the next automatically maps the pointer to the corresponding musical beat. A preview shows the destination before release.</text>
    </radio>
    <radio value="C">
      **C. Drag with automatic scrolling**

      <text color="secondary" size="sm">Cross-line dragging works, and approaching the top or bottom edge automatically scrolls the sheet to reach distant lines.</text>
    </radio>
    <radio value="D">
      **D. Explicit move command for cross-line edits**

      <text color="secondary" size="sm">Normal dragging stays within one line. A dedicated Move command allows selecting a destination anywhere in the sheet.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 73, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B as the minimum behavior**, with edge-triggered auto-scrolling from C as a possible refinement.

This keeps Sheet editing consistent with the continuous timeline while allowing the visual layout to wrap naturally.

### Turn 157 — User

<!-- node_id: 1f9f3feb-d9b8-48f5-8d69-d076f6567646 message_id: 1f9f3feb-d9b8-48f5-8d69-d076f6567646 -->

For Koreo spec'ing question 73, I choose B.

### Turn 158 — Assistant

<!-- node_id: a19bcfe1-a8b5-4061-9858-a2dc5649ce43 message_id: a19bcfe1-a8b5-4061-9858-a2dc5649ce43 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-073 — Locked (B)**
</row>

**Decision: Continuous dragging across wrapped sheet lines.**

- Users can drag choreography moves from one sheet line to another.
- Pointer position maps to the corresponding musical beat, even across line boundaries.
- A live preview indicates the destination before releasing the move.
- Existing beat-snapping and collision-resolution rules remain applicable.
- Each completed drag is a single undoable operation.
- Automatic edge-scrolling is a possible enhancement, not a V1 requirement.

This completes an important part of the Sheet view's editing behavior.

---

## Question 74 — How should Koreo handle moves that span two sheet lines?

Suppose a move starts on beat 29 and lasts eight beats, while the current sheet line ends at beat 32.

The move therefore crosses a visual line break, even though it is one continuous choreography move.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Keep the move on one line**

      <text color="secondary" size="sm">Automatically adjust sheet wrapping so a move never crosses a line boundary, even if this creates uneven line lengths.</text>
    </radio>
    <radio value="B">
      **B. Show two connected visual segments (recommended)**

      <text color="secondary" size="sm">Display the move's first portion at the end of one line and its continuation at the beginning of the next, with a clear continuation indicator. Both segments represent one move.</text>
    </radio>
    <radio value="C">
      **C. Automatically split the move**

      <text color="secondary" size="sm">Convert the move into two independent choreography blocks at the line boundary.</text>
    </radio>
    <radio value="D">
      **D. Show a single block extending beyond the line**

      <text color="secondary" size="sm">Allow the move to extend visually past the sheet's normal line boundary, preserving one uninterrupted rectangle.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 74, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It preserves the underlying move as one object while allowing the sheet to wrap naturally.

Selecting either visual segment would select the entire move, and dragging or resizing it would update the same underlying object.

### Turn 159 — User

<!-- node_id: ca4964e1-a502-41ea-b6c5-4735d0561116 message_id: ca4964e1-a502-41ea-b6c5-4735d0561116 -->

For Koreo spec'ing question 74, I choose B.

### Turn 160 — Assistant

<!-- node_id: bf9f5fb8-ac11-4519-af9d-95f54de8f98b message_id: bf9f5fb8-ac11-4519-af9d-95f54de8f98b -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-074 — Locked (B)**
</row>

**Decision: Moves crossing sheet line boundaries appear as connected visual segments.**

- A move remains **one logical object**, regardless of how many sheet lines it spans.
- Each line displays the portion of the move belonging to that line.
- Continuation indicators make it clear that the move extends onto another line.
- Selecting either segment selects the entire move.
- Editing either segment modifies the same underlying move.
- PDF and Excel exports preserve the visual continuation without splitting the underlying choreography data.

This reinforces an important distinction: **sheet layout is presentation; musical timing is data.**

---

## Question 75 — How should Koreo handle editing moves when the sheet reflows?

Suppose you're editing a choreography block and its label becomes longer. The sheet expands or rewraps to accommodate the text (S-042, S-049).

That could cause blocks to move to different visual positions while you're working.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Immediate reflow**

      <text color="secondary" size="sm">The sheet continuously recalculates its layout as labels change or blocks are edited, even during an active interaction.</text>
    </radio>
    <radio value="B">
      **B. Reflow after each completed edit (recommended)**

      <text color="secondary" size="sm">Keep the sheet layout stable during typing, dragging, or resizing. Recalculate layout when the edit is committed, preserving the selected move and visible location.</text>
    </radio>
    <radio value="C">
      **C. Manual reflow**

      <text color="secondary" size="sm">The sheet maintains its current layout until the user clicks Refresh Layout or requests an export.</text>
    </radio>
    <radio value="D">
      **D. Fixed layout during editing**

      <text color="secondary" size="sm">Use fixed-width cells in the editable sheet. Dynamic spacing and wrapping are applied only to the printable/exported sheet.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 75, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It prevents the interface from shifting beneath the pointer during a drag, while keeping the sheet automatically formatted.

The user should never lose track of the move they were editing simply because the layout changed.

### Turn 161 — User

<!-- node_id: aa1c5697-3b6c-4e06-bd14-87e5d101f7f4 message_id: aa1c5697-3b6c-4e06-bd14-87e5d101f7f4 -->

B. How are we doping on context size and need to crystalise decisions?

### Turn 162 — Assistant

<!-- node_id: 388beb27-106d-4a22-91fd-f7dbc5b97dd4 message_id: 388beb27-106d-4a22-91fd-f7dbc5b97dd4 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-075 — Locked (B)**
</row>

**Decision: Reflow the sheet after each completed edit.**

- Keep the layout stable during typing, dragging, and resizing.
- Recalculate the layout when the edit is committed.
- Preserve the selected move and its visible location as closely as possible.
- Apply the same behavior in both editing modes wherever sheet reflow is relevant.

---

## Specification checkpoint — Recommended now

**We're at a good point to crystallize decisions.** We've accumulated 75 numbered decisions, including several revisions and cross-dependencies.

I would stop the interview temporarily and consolidate the specification before asking S-076.

The concern isn't simply running out of context. It's that a long conversational specification becomes increasingly difficult to maintain consistently.

In particular, we've made significant architectural decisions since the earlier checkpoint:

- Separate Structure and Choreography editing modes.
- Independent Timeline and Sheet views, both fully editable.
- Musical beat positions as authoritative timing.
- Non-overlapping musical sections, with gaps allowed.
- Cross-line editing and layout behavior for the sheet.

These deserve a coherent written contract rather than relying on the conversation history.

### Current status

| Area | Status |
|---|---|
| Decisions S-001–S-075 | Captured in conversation |
| Earlier checkpoint S-001–S-030 | Existing Markdown file |
| Decisions S-031–S-075 | Need consolidation into the artifact |
| Conflicts and superseded decisions | Need reconciliation |
| Implementation handoff | Not yet generated |
| Current phase | Phase 3 — Spec’ing |

The earlier [specification checkpoint](sandbox:/mnt/data/koreo_specs_v1.md) is still available.

I can't provide a reliable percentage of remaining context capacity, but **we have enough accumulated decisions that consolidating now is prudent**, independently of any context limit.

### Proposed next step

Create `koreo_specs_v2.md` as an authoritative **design checkpoint**, not yet an implementation handoff. It should include all 75 decisions, supersede revised ones explicitly, identify unresolved questions, and separate V1 requirements from deferred features.

Then we can resume the interview at S-076 using that document as our reference.

**My recommendation: consolidate now, review the document, then continue spec’ing.** This would be a checkpoint within Phase 3, not a premature transition to implementation.

### Turn 163 — User

<!-- node_id: 6af9b8ef-f14c-4cdf-976d-b9d3dcb67311 message_id: 6af9b8ef-f14c-4cdf-976d-b9d3dcb67311 -->

sounds good please proceed

### Turn 164 — Assistant

<!-- node_id: f098d8bb-ecc9-4dc1-a248-8415b8a8470a message_id: f098d8bb-ecc9-4dc1-a248-8415b8a8470a -->

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **Koreo specification checkpoint V2 created**
</row>

[<icon name="download" inline/> Download koreo_specs_v2.md](sandbox:/mnt/data/koreo_specs_v2.md)

The document consolidates **all 75 decisions (S-001 through S-075)** into a single Markdown specification, approximately 32 KB.

### What's included

- All previously locked requirements, carried forward from V1.
- Decisions S-031–S-075, including the two editing modes and two independent views.
- Corrections and superseded decisions, particularly S-060 (no overlapping musical sections).
- Consolidated timing rules, editing behavior, sheet formatting, and exports.
- An explicit register of unresolved design questions.
- V1 scope, deferred features, and the handoff boundary.

### Items worth reviewing

I identified several details that still need clarification:

| Area | Outstanding issue |
|---|---|
| Musical calibration | Secondary calibration point behavior |
| Structure editing | Exact ripple and boundary behavior |
| Move conflicts | Precise trim/shift semantics |
| Sheet editor | Interaction details across wrapped lines |
| Technology | PySide6 versus Tauri |
| Delivery | Acceptance tests and release milestones |

These are documented as **open questions**, not invented requirements.

### Project status

<box gap={2}>
  <row align="center" justify="between">
    <text color="secondary" weight="medium" size="xs">CURRENT PHASE</text>
    **3 — Spec’ing**
  </row>
  <row align="center" justify="between">
    <text color="secondary" weight="medium" size="xs">DECISIONS CONSOLIDATED</text>
    **75**
  </row>
  <row align="center" justify="between">
    <text color="secondary" weight="medium" size="xs">NEXT INTERVIEW QUESTION</text>
    **S-076**
  </row>
  <row align="center" justify="between">
    <text color="secondary" weight="medium" size="xs">IMPLEMENTATION HANDOFF</text>
    **Not yet generated**
  </row>
</box>

The V2 document is now our **current design checkpoint**, superseding V1 for future decisions.

My recommendation is to review it before continuing. We can then shift the interview toward **V1 completion criteria, practical UX, and implementation choices**, rather than spending too much time on rare structural-editing edge cases.

### Turn 165 — User

<!-- node_id: c0356aea-8b1a-4f9c-943e-a6b7c52c586b message_id: c0356aea-8b1a-4f9c-943e-a6b7c52c586b -->

alright let's proceed as you recommend

### Turn 166 — Assistant

<!-- node_id: a75d3c2a-4016-492a-b1bd-7766be8eaa5f message_id: a75d3c2a-4016-492a-b1bd-7766be8eaa5f -->

## Koreo — Spec’ing Interview

**Phase 3 continues — V1 completion and usability**

We have consolidated S-001–S-075. From here, I suggest shifting our attention toward the **minimum complete product** rather than further edge cases.

Our goal is to define what makes Koreo V1 genuinely useful for planning a choreography, then establish acceptance criteria and prepare the implementation handoff.

---

## Question 76 — What is the minimum successful end-to-end workflow?

Imagine opening Koreo with a song you've never choreographed before.

Which outcome must V1 reliably support before we consider it complete?

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Basic choreography editor**

      <text color="secondary" size="sm">Import audio, calibrate beats, define sections, create and annotate moves, save and reopen the project. Exports can come later.</text>
    </radio>
    <radio value="B">
      **B. Complete choreography-to-sheet workflow (recommended)**

      <text color="secondary" size="sm">Everything in A, plus a readable, formatted choreography sheet, PDF export, and Excel export. A dancer could use the resulting sheet without Koreo.</text>
    </radio>
    <radio value="C">
      **C. Polished editing workflow**

      <text color="secondary" size="sm">Everything in B, plus mature editing conveniences, shortcuts, extensive undo/redo coverage, and smooth navigation before V1 is considered complete.</text>
    </radio>
    <radio value="D">
      **D. Incremental releases**

      <text color="secondary" size="sm">Define A as the first usable milestone, B as the next milestone, and C as a later refinement. V1 is delivered through these stages rather than as one release.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 76, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

**My recommendation is B as the V1 acceptance target**, with incremental internal milestones.

That distinction matters: we can build and validate the editor before implementing exports, without calling the product complete until it delivers the usable choreography sheet.

This question defines the **release threshold**, not a change to the features we've already specified.

### Turn 167 — User

<!-- node_id: 4ae37d9d-415f-4668-af67-c728a59f6a80 message_id: 4ae37d9d-415f-4668-af67-c728a59f6a80 -->

For Koreo spec'ing question 76, I choose B.

### Turn 168 — Assistant

<!-- node_id: a67bc0c5-870e-4bd3-bad4-f8bdeeded386 message_id: a67bc0c5-870e-4bd3-bad4-f8bdeeded386 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-076 — Locked (B)**
</row>

**Decision: V1 must deliver a complete choreography-to-sheet workflow.**

A successful V1 must allow a user to:

1. Import an MP3 or WAV recording and calibrate the beat grid.
2. Define the musical structure and count groups.
3. Create, arrange, and annotate choreography moves.
4. Save, close, and reopen the project without losing data.
5. Produce a readable, formatted choreography sheet.
6. Export that sheet to **PDF and Excel**, usable independently of Koreo.

We can implement this incrementally, but V1 is not considered complete until the entire workflow passes acceptance testing.

This establishes the **V1 release threshold**, not a new feature expansion.

---

## Question 77 — How should we organize implementation milestones?

Since the complete workflow is substantial, we should define how the external execution agent builds and validates it.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Feature-by-feature**

      <text color="secondary" size="sm">Build the audio engine, musical structure model, choreography editor, sheet renderer, and exporters separately, integrating them near the end.</text>
    </radio>
    <radio value="B">
      **B. Vertical slices (recommended)**

      <text color="secondary" size="sm">Build a small working end-to-end application first, then progressively improve editing, presentation, and exports. Every milestone leaves a runnable, testable application.</text>
    </radio>
    <radio value="C">
      **C. Model-first, then interface**

      <text color="secondary" size="sm">Complete and test the underlying project model, timing calculations, editing operations, and serialization before developing the graphical interface.</text>
    </radio>
    <radio value="D">
      **D. Interface prototype first**

      <text color="secondary" size="sm">Build an interactive UI prototype with representative data, validate the editing experience, then connect it to the real project model and audio playback.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 77, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, with automated model tests developed alongside each slice.

For Koreo, interaction quality is a significant risk. A mathematically correct model isn't enough if drawing moves, navigating the grid, or editing wrapped sheet lines feels awkward.

Vertical slices let us validate those interactions early, rather than discovering usability problems after most of the application has been built.

### Turn 169 — User

<!-- node_id: 991cf1b3-d1e5-4173-99d2-9e1435789be5 message_id: 991cf1b3-d1e5-4173-99d2-9e1435789be5 -->

For Koreo spec'ing question 77, I choose C.

### Turn 170 — Assistant

<!-- node_id: 219fc051-cf18-4369-9974-b2046b5304fd message_id: 219fc051-cf18-4369-9974-b2046b5304fd -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-077 — Locked (C)**
</row>

**Decision: Model-first implementation strategy.**

The execution roadmap will prioritize:

1. **Domain model:** Musical regions, beats, count groups, choreography tracks, moves, and their relationships.
2. **Core operations:** Timing calculations, structural edits, move operations, collision resolution, and undo/redo.
3. **Persistence:** Project serialization, audio embedding, and save/load integrity.
4. **Automated tests:** Validate model behavior and edge cases before integrating the graphical interface.
5. **Graphical application:** Build the Timeline and Sheet editors on top of the tested model.
6. **End-to-end validation:** Confirm the complete workflow required by S-076, including PDF and Excel exports.

This does not prohibit small UI prototypes to investigate interaction risks. It establishes that **the domain model and its tests are the first implementation milestone**.

---

## Question 78 — Which technology stack should we commit to?

We've previously identified Python/PySide6 as the preferred direction, while leaving Tauri available as an alternative (S-002).

Now that we've selected a model-first implementation strategy, we should decide whether to freeze the application stack.

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Python + PySide6 (recommended)**

      <text color="secondary" size="sm">Python domain model and Qt desktop interface. Use Qt graphics facilities for waveform, timeline, and sheet editing.</text>
    </radio>
    <radio value="B">
      **B. Python backend + Tauri frontend**

      <text color="secondary" size="sm">Keep the domain model in Python, but build the desktop interface using web technologies inside Tauri. Requires communication between Python and the frontend.</text>
    </radio>
    <radio value="C">
      **C. TypeScript + Tauri**

      <text color="secondary" size="sm">Implement the model and interface primarily in TypeScript, with Tauri providing the native desktop shell.</text>
    </radio>
    <radio value="D">
      **D. Defer the framework decision**

      <text color="secondary" size="sm">Specify a framework-independent Python domain model first. Evaluate PySide6 versus a web-based frontend after the model milestone.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 78, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A** for V1. It aligns with the model-first strategy, avoids a Python-to-web communication layer, and provides a mature desktop graphics framework.

The main technical risk to validate early is whether Qt's graphics facilities can deliver sufficiently smooth interaction with the waveform, beat grid, and wrapped sheet editor.

### Turn 171 — User

<!-- node_id: b618d211-e255-4689-9ae8-520e8c1220d3 message_id: b618d211-e255-4689-9ae8-520e8c1220d3 -->

For Koreo spec'ing question 78, I choose A.

### Turn 172 — Assistant

<!-- node_id: 8269f756-5001-4e1c-a366-5f00f169a42d message_id: 8269f756-5001-4e1c-a366-5f00f169a42d -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-078 — Locked (A)**
</row>

**Decision: Python + PySide6 for Koreo V1.**

- **Language:** Python for the domain model and application logic.
- **GUI:** PySide6 (Qt for Python).
- **Architecture:** Keep the domain model independent of the graphical interface.
- **Graphics:** Use Qt's graphics facilities for the waveform timeline, musical grid, and editable sheet.
- **Testing:** pytest for domain behavior, with GUI interaction tests where appropriate.
- **Platform:** Linux-first, preserving cross-platform compatibility where practical.

This supersedes the open framework choice in S-002.

The first implementation milestone remains the **domain model and automated tests**, as established in S-077.

---

## Question 79 — How should the domain model represent musical time?

This is one of the remaining foundational technical decisions.

We have established that beats are authoritative (S-058), but we haven't decided how to represent beat positions internally.

For example, a move might start at beat `17`, `17.5`, or `17.333…` when snapping is temporarily disabled.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Floating-point beat positions**

      <text color="secondary" size="sm">Use standard Python floating-point numbers. Simple and convenient, but repeated calculations can introduce tiny precision errors.</text>
    </radio>
    <radio value="B">
      **B. Exact rational beat positions (recommended)**

      <text color="secondary" size="sm">Represent positions and durations as fractions of beats, such as 17, 17½, or 17⅓. Avoid floating-point drift in editing operations.</text>
    </radio>
    <radio value="C">
      **C. Fixed-resolution integer ticks**

      <text color="secondary" size="sm">Represent musical time using integer ticks, such as 960 ticks per beat. Common in MIDI-style timing systems, with a fixed precision limit.</text>
    </radio>
    <radio value="D">
      **D. Floating-point internally, quantized on save**

      <text color="secondary" size="sm">Use floating-point during editing, then round beat positions to a defined precision when storing the project.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 79, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** because Python has built-in support for exact fractions, and the model-first approach makes precise interval calculations especially valuable.

We would still use floating-point values where appropriate for audio playback and screen coordinates. The exact representation would apply to **stored musical positions and durations**, not every calculation in the application.

### Turn 173 — User

<!-- node_id: f3b76e59-c808-47cd-8c38-4e58157cb3a5 message_id: f3b76e59-c808-47cd-8c38-4e58157cb3a5 -->

For Koreo spec'ing question 79, I choose B.

### Turn 174 — Assistant

<!-- node_id: c6ff99bf-1494-47e8-b990-a12c7b444baf message_id: c6ff99bf-1494-47e8-b990-a12c7b444baf -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-079 — Locked (B)**
</row>

**Decision: Exact rational representation of musical time.**

- Musical positions and durations are stored as rational numbers (fractions of beats).
- Whole beats and fractional beats are represented exactly.
- Musical interval calculations must not accumulate floating-point rounding errors.
- Audio timestamps and graphical coordinates may use floating-point values.
- Project serialization must preserve rational values exactly.
- The domain model remains independent of PySide6.

For example, a move starting at beat \(17+\frac13\) and lasting \(2+\frac12\) beats retains those exact values through editing, saving, and reopening.

This provides a solid foundation for the model-first implementation strategy.

---

## Question 80 — How should Koreo represent musical regions internally?

We have hierarchical regions (S-006), independent labels (S-034), and non-overlapping siblings (S-060).

There are two main ways to represent their positions.

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Absolute beat intervals (recommended)**

      <text color="secondary" size="sm">Every region stores its start beat and duration relative to the song. Parent-child relationships are stored separately. Resizing a parent does not automatically change its children's timing.</text>
    </radio>
    <radio value="B">
      **B. Parent-relative intervals**

      <text color="secondary" size="sm">Each child stores its position relative to its parent. Moving a parent automatically moves all descendants. Resizing requires explicit rules for children.</text>
    </radio>
    <radio value="C">
      **C. Proportional child positions**

      <text color="secondary" size="sm">Children store relative percentages within their parent. Resizing a parent automatically stretches or compresses its subdivisions.</text>
    </radio>
    <radio value="D">
      **D. Hybrid absolute and relative timing**

      <text color="secondary" size="sm">Regions can independently use absolute or parent-relative positions, allowing flexible behavior but requiring additional complexity.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 80, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A** for the underlying storage model, with explicit operations to move a parent and its descendants together.

This simplifies timeline calculations, serialization, and collision detection. It also avoids silently stretching musical subdivisions when a parent region is resized.

One important invariant would still apply: **children must remain within their parent's interval**. Operations that violate that constraint would need an explicit resolution rule.

### Turn 175 — User

<!-- node_id: 8103e11b-9bc9-4df5-aee2-5e1ee965ec32 message_id: 8103e11b-9bc9-4df5-aee2-5e1ee965ec32 -->

For Koreo spec'ing question 80, I choose A.

### Turn 176 — Assistant

<!-- node_id: 8429a198-090c-49fc-933d-7dfc162df548 message_id: 8429a198-090c-49fc-933d-7dfc162df548 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-080 — Locked (A)**
</row>

**Decision: Musical regions use absolute beat intervals.**

- Every musical region stores its start position and duration in song-relative beats.
- Parent-child relationships are stored separately from timing.
- Moving a parent can move its descendants through an explicit operation.
- Resizing a parent does not automatically stretch or compress its children.
- Children must remain within their parent's interval.
- Sibling regions cannot overlap, but gaps are permitted (S-060, S-061).
- All timing values use exact rational numbers (S-079).

This keeps the domain model simple while leaving editing behavior under explicit control.

---

## Question 81 — What happens to children when their parent region is resized?

Consider this structure:

<box border radius="lg" padding={3} gap={2}>
  <text color="secondary" weight="medium" size="xs">BEFORE RESIZING</text>
  <box background="surface-secondary" radius="md" padding={2} gap={2}>
    <row justify="between">
      **Section A**
      <text color="secondary" size="xs" tabularNums>Beats 1–32</text>
    </row>
    <grid columns={4} gap="3px">
      {#each [1,2,3,4] as n}
        <grid-item>
          <box background="rgba(80,130,210,0.17)" border radius="sm" padding={{x:1,y:2}} align="center">
            <text size="xs">8 beats</text>
          </box>
        </grid-item>
      {/each}
    </grid>
  </box>
  <row align="center" justify="center" gap={2}>
    <icon name="arrow-down" color="secondary"/>
    <text color="secondary" size="xs">Shorten parent to 24 beats</text>
  </row>
  <text color="secondary" size="sm">The fourth child would extend beyond its parent.</text>
</box>

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Reject the resize**

      <text color="secondary" size="sm">A parent cannot be shortened beyond its existing children. Users must adjust or remove the children first.</text>
    </radio>
    <radio value="B">
      **B. Ask how to resolve affected children (recommended)**

      <text color="secondary" size="sm">Offer to trim, remove, or cancel when children would extend outside the new parent boundary. Unaffected children remain unchanged.</text>
    </radio>
    <radio value="C">
      **C. Automatically trim children**

      <text color="secondary" size="sm">Shorten or remove children as necessary to fit the new parent, without asking.</text>
    </radio>
    <radio value="D">
      **D. Resize all children proportionally**

      <text color="secondary" size="sm">Scale child positions and durations to fit the new parent, preserving their relative proportions.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 81, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**. It preserves the absolute-beat model while handling occasional structural revisions safely.

Since you've emphasized that extensive structure changes should be relatively rare, this resolution dialog would appear only when a resize actually conflicts with existing subdivisions.

### Turn 177 — User

<!-- node_id: 08e6f37b-c643-471a-8290-0a3fa5b74a84 message_id: 08e6f37b-c643-471a-8290-0a3fa5b74a84 -->

For Koreo spec'ing question 81, I choose B.

### Turn 178 — Assistant

<!-- node_id: 1207158b-78c0-4977-8855-39587fba0cf6 message_id: 1207158b-78c0-4977-8855-39587fba0cf6 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-081 — Locked (B)**
</row>

**Decision: Explicit resolution when resizing a parent conflicts with its children.**

- Children retain their absolute beat positions and durations by default.
- If a parent resize would leave children outside its boundaries, Koreo offers **Trim, Remove, or Cancel**.
- Unaffected children remain unchanged.
- Any affected descendants must also satisfy the hierarchy's containment rules.
- The complete operation is undoable as one action.
- No child is silently resized or deleted.

This preserves the domain invariants established in S-080 without complicating normal editing.

---

## Question 82 — How should the domain model represent choreography tracks and moves?

We have already established that tracks are independent of musical sections and that moves cannot overlap within the same track.

The remaining question is how to represent this relationship internally.

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Independent moves with track references (recommended)**

      <text color="secondary" size="sm">Each move has a stable ID, track ID, absolute start beat, duration, label, and notes. Tracks hold their own metadata and display order. Musical sections do not own moves.</text>
    </radio>
    <radio value="B">
      **B. Tracks own ordered move collections**

      <text color="secondary" size="sm">Each track stores its moves as an ordered collection. Moves have beat positions relative to the song, but are structurally contained within their track.</text>
    </radio>
    <radio value="C">
      **C. Moves belong to musical regions**

      <text color="secondary" size="sm">Moves are stored inside musical sections and assigned to tracks for display. Structural changes must update those relationships.</text>
    </radio>
    <radio value="D">
      **D. Shared event timeline**

      <text color="secondary" size="sm">Musical regions and choreography moves are represented as different event types in one shared collection, with separate metadata and constraints.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 82, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A**. It gives every move an independent identity and makes copying between tracks, querying moves by time interval, and preserving choreography during structural edits straightforward.

It also keeps a clean separation between the musical structure and choreography, which has been a consistent design principle throughout the specification.

### Turn 179 — User

<!-- node_id: 472da392-537c-4d0c-9674-38ca5f72e563 message_id: 472da392-537c-4d0c-9674-38ca5f72e563 -->

For Koreo spec'ing question 82, I choose A.

### Turn 180 — Assistant

<!-- node_id: 9ec57fe8-2665-45a4-a594-6d85147d93b7 message_id: 9ec57fe8-2665-45a4-a594-6d85147d93b7 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-082 — Locked (A)**
</row>

**Decision: Independent choreography moves with track references.**

- Each move has a stable, unique ID.
- Each move stores its track ID, absolute start beat, duration, short label, and optional detailed notes.
- Tracks store their own identity, name, color, and display order.
- Musical sections do not own choreography moves.
- Moves are independent of the musical hierarchy.
- Moves on the same track cannot overlap (S-031).
- All positions and durations use exact rational beats (S-079).

This gives us a clean domain model with three principal concepts: **musical regions, choreography tracks, and moves**.

---

## Question 83 — How should the domain model handle undo/redo?

We've already established shared undo/redo (S-024). Now we need to choose how editing operations are represented internally.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Project snapshots**

      <text color="secondary" size="sm">Store a copy of the project state before each edit. Undo restores the previous snapshot. Simple to implement, but potentially memory-intensive.</text>
    </radio>
    <radio value="B">
      **B. Reversible commands (recommended)**

      <text color="secondary" size="sm">Represent each edit as a command that can be applied and reversed. Group complex edits into one transaction, including conflict resolutions.</text>
    </radio>
    <radio value="C">
      **C. Event history**

      <text color="secondary" size="sm">Record every change as an immutable event. Reconstruct project state by replaying events, with undo represented by compensating events.</text>
    </radio>
    <radio value="D">
      **D. Hybrid commands and snapshots**

      <text color="secondary" size="sm">Use reversible commands for ordinary edits and snapshots for complex structural operations.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 83, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** for Koreo V1.

It fits our model-first strategy and gives us a clear way to test editing operations independently of PySide6.

For example, resizing a musical section, trimming an affected child, and shifting subsequent sections could be treated as **one atomic command**: either the entire operation succeeds, or nothing changes.

This would also give Timeline and Sheet editing the same undo/redo behavior.

### Turn 181 — User

<!-- node_id: 1d0000b9-e26e-4b77-900f-cea7ebadeb8a message_id: 1d0000b9-e26e-4b77-900f-cea7ebadeb8a -->

For Koreo spec'ing question 83, I choose B.

### Turn 182 — Assistant

<!-- node_id: 85b574ab-c089-4d93-9eba-ed788d4b547f message_id: 85b574ab-c089-4d93-9eba-ed788d4b547f -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-083 — Locked (B)**
</row>

**Decision: Reversible commands for undo/redo.**

- Every model-changing operation is represented by a reversible command.
- Complex operations can group several changes into one atomic transaction.
- Failed or cancelled commands leave the project unchanged.
- Dragging and resizing generate one undo entry per completed interaction, not one per pointer movement.
- Timeline and Sheet share the same command history.
- Commands operate on the domain model independently of PySide6.
- Undo/redo behavior must be covered by automated tests.

This establishes the foundation for consistent editing behavior across Koreo.

---

## Question 84 — How should Koreo validate changes to the project model?

We now have several important invariants: no overlapping moves within a track, no overlapping sibling musical regions, children contained within parents, and valid beat intervals.

The question is where these rules should be enforced.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Validate in the interface**

      <text color="secondary" size="sm">The GUI prevents invalid edits before passing them to the domain model. The model assumes incoming operations are valid.</text>
    </radio>
    <radio value="B">
      **B. Centralized domain validation (recommended)**

      <text color="secondary" size="sm">The domain layer enforces invariants for every operation. The GUI provides previews and warnings, but cannot bypass the rules.</text>
    </radio>
    <radio value="C">
      **C. Validate after each command**

      <text color="secondary" size="sm">Commands can modify the model provisionally. A validator checks the resulting state and rolls back the entire command if invalid.</text>
    </radio>
    <radio value="D">
      **D. Validate on save**

      <text color="secondary" size="sm">Allow temporary inconsistencies during editing, then require a valid project state before saving or exporting.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 84, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, with atomic validation of completed commands.

This makes the domain model the authoritative source of correctness. The interface can help users avoid invalid operations, but the same rules remain enforced when changes come from either editor, project loading, or future automation.

It also fits the model-first testing strategy established in S-077.

### Turn 183 — User

<!-- node_id: 30b0394f-3b93-49ab-b16c-57ed91533a32 message_id: 30b0394f-3b93-49ab-b16c-57ed91533a32 -->

For Koreo spec'ing question 84, I choose B.

### Turn 184 — Assistant

<!-- node_id: 6b5c1d56-3859-4cf1-b691-58d9db842170 message_id: 6b5c1d56-3859-4cf1-b691-58d9db842170 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-084 — Locked (B)**
</row>

**Decision: Centralized domain validation.**

- The domain layer is the authoritative enforcer of project invariants.
- Every editing command must produce a valid project state.
- Invalid commands fail atomically, leaving the project unchanged.
- The GUI provides previews, warnings, and conflict-resolution choices but cannot bypass validation.
- Project loading must also validate the resulting model.
- Automated tests verify both valid operations and rejection of invalid ones.

This completes an important architectural foundation:

**Domain model → Validated commands → Shared state → Timeline / Sheet interfaces**

Neither graphical view owns the underlying project data or its correctness rules.

---

## Question 85 — How should Koreo handle project file compatibility?

We've established a portable, self-contained project file containing audio and structured data (S-019).

As Koreo evolves, the project format will inevitably change. We should decide how older files are handled.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Strict version matching**

      <text color="secondary" size="sm">Koreo opens only projects using its current file format. Older projects require external conversion.</text>
    </radio>
    <radio value="B">
      **B. Versioned format with automatic migration (recommended)**

      <text color="secondary" size="sm">Every project records its format version. Koreo automatically migrates supported older versions when opening, while preserving the original file until the user saves.</text>
    </radio>
    <radio value="C">
      **C. Versioned format with explicit conversion**

      <text color="secondary" size="sm">When opening an older project, Koreo offers to convert it into a new project file, keeping the original unchanged.</text>
    </radio>
    <radio value="D">
      **D. Forward-compatible extensible format**

      <text color="secondary" size="sm">Design the format to preserve unknown fields where possible, allowing some projects from newer Koreo versions to open in older versions.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 85, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, implemented pragmatically.

For V1, that means defining a format version from the beginning and providing a clear migration mechanism. We don't need to invent migrations for versions that don't exist yet.

Newer, unsupported project formats should be rejected safely rather than risking data corruption.

### Turn 185 — User

<!-- node_id: bb5ac0ae-7798-41a7-9490-d7fc315139b9 message_id: bb5ac0ae-7798-41a7-9490-d7fc315139b9 -->

For Koreo spec'ing question 85, I choose B.

### Turn 186 — Assistant

<!-- node_id: b3305bfa-930e-47d9-80de-b95f3224bf54 message_id: b3305bfa-930e-47d9-80de-b95f3224bf54 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-085 — Locked (B)**
</row>

**Decision: Versioned project format with automatic migration.**

- Every project records its file-format version.
- Koreo automatically migrates supported older formats when opening them.
- Migration occurs in memory; the original file remains unchanged until the user explicitly saves.
- Unsupported newer formats are rejected safely with an explanatory message.
- Migration must preserve musical timing, choreography, annotations, and embedded audio.
- Automated tests verify migrations and round-trip serialization.

For V1, we establish the versioning mechanism and initial format. We do not need to implement hypothetical future migrations.

---

## Question 86 — How should Koreo handle project save failures?

Since a project contains both structured data and embedded audio, saving may involve writing a relatively large file.

We need to ensure that an interrupted save doesn't destroy the user's existing project.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Direct file overwrite**

      <text color="secondary" size="sm">Write directly to the existing project file. Simple, but a crash or disk error could leave it incomplete.</text>
    </radio>
    <radio value="B">
      **B. Atomic save with temporary file (recommended)**

      <text color="secondary" size="sm">Write the complete project to a temporary file, validate it, then replace the original only after the new file is ready.</text>
    </radio>
    <radio value="C">
      **C. Atomic save plus automatic backup**

      <text color="secondary" size="sm">Use the temporary-file approach and also retain the previous successfully saved project as a backup.</text>
    </radio>
    <radio value="D">
      **D. Incremental saves**

      <text color="secondary" size="sm">Update only changed portions of the project rather than rewriting the complete archive. More complex but potentially faster for large audio files.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 86, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B for V1**.

The existing project should remain intact if saving fails because of insufficient disk space, an interrupted process, or a serialization error.

This complements S-025's crash-recovery snapshots, which serve a different purpose: recovering **unsaved work**, rather than protecting an existing file during a save operation.

### Turn 187 — User

<!-- node_id: 885749d5-c37a-46ed-9b6f-2f00cd12dd11 message_id: 885749d5-c37a-46ed-9b6f-2f00cd12dd11 -->

For Koreo spec'ing question 86, I choose B.

### Turn 188 — Assistant

<!-- node_id: 9d0da598-63d6-4ddc-999c-4fbc9a2f54b7 message_id: 9d0da598-63d6-4ddc-999c-4fbc9a2f54b7 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-086 — Locked (B)**
</row>

**Decision: Atomic project saves using a temporary file.**

- Koreo writes the complete project to a temporary file in the destination directory.
- The new file is validated before replacing the existing project.
- The original remains intact if writing or validation fails.
- Replacement occurs atomically where supported by the filesystem.
- Temporary files left by interrupted saves are handled safely.
- Save failures are reported clearly without incorrectly marking the project as saved.
- Crash-recovery snapshots (S-025) remain a separate mechanism.

This completes the core persistence strategy for V1.

---

## Question 87 — How should we define the first implementation milestone?

With the model, command system, validation, and persistence approach established, we can define what the execution agent must deliver first.

The first milestone should be independently testable, even before the graphical interface exists.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Minimal domain model**

      <text color="secondary" size="sm">Implement musical regions, tracks, moves, exact beat timing, and validation, with unit tests. Editing commands and persistence follow in later milestones.</text>
    </radio>
    <radio value="B">
      **B. Complete headless project engine (recommended)**

      <text color="secondary" size="sm">Implement the domain model, core editing commands, undo/redo, validation, and project save/load. Demonstrate the complete workflow through automated tests without a GUI.</text>
    </radio>
    <radio value="C">
      **C. Domain model plus basic graphical viewer**

      <text color="secondary" size="sm">Implement the domain model and a minimal PySide6 window that displays musical regions and choreography tracks. Editing and persistence follow later.</text>
    </radio>
    <radio value="D">
      **D. Audio-calibration prototype first**

      <text color="secondary" size="sm">Prioritize audio loading, playback, BPM, beat anchors, and waveform alignment. Implement the remaining domain model afterward.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 87, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, consistent with the model-first strategy in S-077.

The first milestone would produce a **tested, headless Koreo engine** that can create a project, define musical structure, manipulate moves, undo operations, save, and reopen the result.

The GUI would then become a client of this established engine rather than the place where application rules are implemented.

We can keep audio decoding, waveform rendering, and PDF/Excel export for subsequent milestones without compromising this foundation.

### Turn 189 — User

<!-- node_id: fb88603e-0e9f-4237-a135-5e2961ca91f2 message_id: fb88603e-0e9f-4237-a135-5e2961ca91f2 -->

For Koreo spec'ing question 87, I choose C.

### Turn 190 — Assistant

<!-- node_id: f66a7489-9e63-4d11-ad9e-611fd6b95fde message_id: f66a7489-9e63-4d11-ad9e-611fd6b95fde -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-087 — Locked (C)**
</row>

**Decision: First implementation milestone delivers the domain model and a basic graphical viewer.**

The first milestone includes:

- A Python domain model for musical regions, tracks, moves, and exact beat timing.
- Domain validation and automated unit tests.
- A minimal PySide6 application displaying musical regions and choreography tracks using representative project data.
- A clear separation between domain logic and presentation.

**Not required in the first milestone:** full editing, audio playback, project persistence, or exports.

This remains compatible with S-077's model-first strategy: the GUI is initially a **read-only visualization of the tested model**, not a place to implement business rules.

It also gives us something tangible to evaluate early, before committing to complex editing interactions.

---

## Question 88 — What should the first graphical prototype demonstrate?

Since you've chosen a graphical viewer for the first milestone, we should decide which visual representation to validate first.

{@body const [choice,setChoice] = DIL.useState("A")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Continuous timeline (recommended)**

      <text color="secondary" size="sm">Show musical sections, beat markers, and choreography tracks along one horizontal timeline. Validate coordinate mapping, alignment, zoom, and pan.</text>
    </radio>
    <radio value="B">
      **B. Wrapped notation sheet**

      <text color="secondary" size="sm">Show musical sections, count groups, and choreography blocks arranged into wrapped lines. Validate readability, spacing, and line breaks.</text>
    </radio>
    <radio value="C">
      **C. Both views, minimal functionality**

      <text color="secondary" size="sm">Implement basic read-only Timeline and Sheet views, with a toggle between them. Validate that both render the same project data.</text>
    </radio>
    <radio value="D">
      **D. Editing-mode distinction first**

      <text color="secondary" size="sm">Prototype Structure and Choreography modes, including their different visual emphasis, using a simple shared timeline.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 88, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **A** for the first milestone. The continuous timeline is the simpler graphical foundation and lets us validate beat-to-pixel mapping before tackling sheet wrapping and pagination.

The Sheet view remains a V1 requirement; this only determines the order in which we validate the interface.

### Turn 191 — User

<!-- node_id: 908078bc-82d8-4c4e-830e-f267b82fcda7 message_id: 908078bc-82d8-4c4e-830e-f267b82fcda7 -->

For Koreo spec'ing question 88, I choose C.

### Turn 192 — Assistant

<!-- node_id: 12cb0d20-71a2-4af6-bf7b-e87e3864f0ee message_id: 12cb0d20-71a2-4af6-bf7b-e87e3864f0ee -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-088 — Locked (C)**
</row>

**Decision: First graphical prototype includes both Timeline and Sheet views.**

The first implementation milestone will demonstrate:

- A minimal, read-only **Timeline view** showing musical sections, beat markers, tracks, and moves.
- A minimal, read-only **Sheet view** showing the same data in a wrapped musical grid.
- A toggle to switch between the two views.
- Both views rendered from the same underlying domain model.
- Representative test data covering sections, subdivisions, and multiple choreography tracks.

Advanced editing, waveform rendering, audio playback, and export are not required for this milestone.

This gives us an early opportunity to compare both visual representations before implementing their more complicated interactions.

---

## Question 89 — How should we validate the first graphical prototype?

The domain model will have automated tests, but visual usability requires a different kind of validation.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Automated tests only**

      <text color="secondary" size="sm">Validate rendering and view switching programmatically. Continue implementation when tests pass.</text>
    </radio>
    <radio value="B">
      **B. Human review checkpoint (recommended)**

      <text color="secondary" size="sm">The execution agent delivers a runnable prototype and screenshots. You inspect both views and approve or request changes before the next milestone.</text>
    </radio>
    <radio value="C">
      **C. Structured usability test**

      <text color="secondary" size="sm">Validate the prototype against predefined visual and navigation tasks, with explicit pass/fail criteria and recorded observations.</text>
    </radio>
    <radio value="D">
      **D. Automated tests plus structured human review**

      <text color="secondary" size="sm">Require automated model/view tests and a human review using a short checklist of visual criteria before advancing.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 89, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B** as the minimum checkpoint, although **D** provides stronger validation without much additional overhead.

Since the first prototype is read-only, the review should focus on whether the Timeline and Sheet communicate musical structure clearly, not on interactions that haven't been implemented yet.

### Turn 193 — User

<!-- node_id: b86ba233-5f23-4eb9-ae91-143569c6f534 message_id: b86ba233-5f23-4eb9-ae91-143569c6f534 -->

For Koreo spec'ing question 89, I choose B.

### Turn 194 — Assistant

<!-- node_id: 69536747-45a3-4d27-840d-f08577f3732b message_id: 69536747-45a3-4d27-840d-f08577f3732b -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-089 — Locked (B)**
</row>

**Decision: Human review checkpoint after the first graphical prototype.**

The execution agent must deliver:

- A runnable PySide6 prototype with both Timeline and Sheet views.
- Representative project data demonstrating musical regions, subdivisions, tracks, and moves.
- Screenshots of both views.
- Instructions for launching the prototype.
- Automated domain tests and their results.

**You review and approve the visual design before implementation advances to the next milestone.**

The review focuses on layout, readability, musical alignment, and the relationship between the two views. Full editing interactions are not yet expected.

This matches our workflow: the execution agent implements the agreed contract, while design decisions remain with us.

---

## Question 90 — How should we organize implementation handoffs?

We've established that development proceeds through milestones with human review. Now we should decide how instructions are delivered to the execution agent.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. One comprehensive handoff**

      <text color="secondary" size="sm">Produce one implementation contract covering the entire V1 application. The agent works through all milestones using that document.</text>
    </radio>
    <radio value="B">
      **B. Separate handoff per milestone (recommended)**

      <text color="secondary" size="sm">Produce a focused, self-contained handoff for each milestone. Review results, then create the next handoff incorporating approved changes.</text>
    </radio>
    <radio value="C">
      **C. Master specification plus milestone instructions**

      <text color="secondary" size="sm">Maintain one authoritative master specification and issue smaller milestone-specific execution documents referencing it.</text>
    </radio>
    <radio value="D">
      **D. One handoff per feature**

      <text color="secondary" size="sm">Create individual handoffs for the domain model, Timeline, Sheet, audio, persistence, and exporters, independently of milestones.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 90, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, consistent with your existing design-authority workflow.

Each handoff would be the **sole execution contract for its milestone**, containing the necessary context, specifications, implementation boundaries, tests, and definition of done.

The consolidated Koreo specification would remain our design reference, while the execution agent would not need to reconstruct requirements from the conversation.

At this point, we're also approaching a natural stopping point for the interview: after settling handoff organization and a few remaining milestone boundaries, we can prepare the first execution contract.

### Turn 195 — User

<!-- node_id: 62600220-1c3b-494d-b4b9-fac4cd1d144b message_id: 62600220-1c3b-494d-b4b9-fac4cd1d144b -->

For Koreo spec'ing question 90, I choose B.

### Turn 196 — Assistant

<!-- node_id: 8ba8c52f-4ec0-43ea-9b1d-109b40d6da27 message_id: 8ba8c52f-4ec0-43ea-9b1d-109b40d6da27 -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-090 — Locked (B)**
</row>

**Decision: One self-contained execution handoff per milestone.**

- Each milestone receives its own authoritative handoff document.
- Each handoff contains all context required for execution, without relying on chat history.
- The execution agent implements only the scope defined in that handoff.
- You review the completed milestone before the next handoff is prepared.
- Corrections and new requirements are incorporated into a subsequent handoff, not informally added during execution.

The consolidated specification remains our **design reference**, while each milestone handoff is the **sole execution contract** for that milestone.

---

## Question 91 — What should happen when an execution agent encounters ambiguity?

Our handoffs should minimize ambiguity, but an implementation agent may still encounter an unforeseen design decision.

We should establish how it must respond.

{@body const [choice,setChoice] = DIL.useState("B")}
<box gap={3}>
  <radio-group direction="col" value={choice} onChange={setChoice}>
    <radio value="A">
      **A. Make reasonable assumptions**

      <text color="secondary" size="sm">The agent chooses the simplest reasonable interpretation, documents it, and continues.</text>
    </radio>
    <radio value="B">
      **B. Stop and report ambiguity (recommended)**

      <text color="secondary" size="sm">If a decision affects requirements, behavior, architecture, or scope, the agent stops the affected work and reports the ambiguity for resolution.</text>
    </radio>
    <radio value="C">
      **C. Continue unaffected work**

      <text color="secondary" size="sm">The agent records the ambiguity, skips the affected component, and continues implementing independent parts of the milestone.</text>
    </radio>
    <radio value="D">
      **D. Propose alternatives**

      <text color="secondary" size="sm">The agent pauses, presents possible interpretations with a recommendation, and waits for an explicit decision.</text>
    </radio>
  </radio-group>
  <row justify="end">
    <button onClick={()=>GenUI.issueNewTurn("For Koreo spec'ing question 91, I choose "+choice+".")}>Confirm choice <icon name="arrow-right" inline/></button>
  </row>
</box>

I recommend **B**, consistent with our existing design-authority rules.

The agent can make ordinary implementation choices within the contract, but must not invent product behavior or silently expand scope.

After S-091, I suggest we stop asking process questions and concentrate on preparing the first milestone handoff.

### Turn 197 — User

<!-- node_id: c0172fe8-eded-4150-95fa-28606b759b0f message_id: c0172fe8-eded-4150-95fa-28606b759b0f -->

For Koreo spec'ing question 91, I choose B.

### Turn 198 — Assistant

<!-- node_id: 15d07cc1-e957-4b66-9e0c-f48a376da6ca message_id: 15d07cc1-e957-4b66-9e0c-f48a376da6ca -->

## Koreo — Spec’ing Interview

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **S-091 — Locked (B)**
</row>

**Decision: Execution agents must stop and report ambiguities.**

- Agents may make routine technical choices within the handoff's constraints.
- They must not invent requirements, reinterpret product behavior, or expand scope.
- If an ambiguity affects behavior, architecture, or requirements, the agent stops the affected work.
- The agent reports the ambiguity and explains what decision is needed.
- Resolution belongs to the design-authority workflow.
- Changes to the execution contract require a new handoff.

This reinforces the existing Koreo development rules.

---

## Phase 3 — Spec’ing: Milestone 1 is ready for handoff preparation

We've now established the key decisions needed to define the first implementation milestone.

<box border radius="xl" padding={3} gap={3}>
  <title size="lg">Milestone 1 — Domain Model + Graphical Viewer</title>
  <row align="center" gap={2}>
    <icon name="layers" color="secondary"/>
    **Domain foundation**
  </row>
  Exact rational beat timing, musical-region hierarchy, choreography tracks and moves, and centralized validation.

  <divider color="subtle"/>
  <row align="center" gap={2}>
    <icon name="monitor" color="secondary"/>
    **Graphical prototype**
  </row>
  A minimal PySide6 application with read-only Timeline and wrapped Sheet views, both displaying the same representative project.

  <divider color="subtle"/>
  <row align="center" gap={2}>
    <icon name="clipboard-check" color="secondary"/>
    **Validation**
  </row>
  Automated domain tests, a runnable application, screenshots, and a human approval checkpoint.
</box>

**Explicitly deferred beyond Milestone 1:** full editing commands, undo/redo integration, audio playback, waveform rendering, project persistence, and PDF/Excel export. These remain V1 requirements where previously specified.

### Recommended next action

I suggest we now transition from **Phase 3 — Spec’ing** to **Phase 4 — Handoff Generation**, producing:

`handoff_261011_1.md`

It will be a self-contained execution contract with the required sections: context, non-goals, specifications, implementation requirements, tests, and definition of done.

We have 91 recorded decisions, but the handoff will include **only those necessary to implement Milestone 1**, plus enough architectural context to avoid incompatible choices.

**Shall I generate the Milestone 1 handoff now?**

### Turn 199 — User

<!-- node_id: b3cbed5d-6da8-45fb-a0eb-66838d8dbf5e message_id: b3cbed5d-6da8-45fb-a0eb-66838d8dbf5e -->

yes please

### Turn 200 — Assistant

<!-- node_id: 94cbde3e-fb2a-4c85-9ef2-b5b598aa08b2 message_id: 94cbde3e-fb2a-4c85-9ef2-b5b598aa08b2 -->

## Koreo — Phase 4: Handoff Generation

We're moving from specification to the **Milestone 1 execution contract**.

The agreed scope is a tested Python domain model plus a runnable PySide6 prototype with two read-only views: Timeline and Sheet. Full editing, audio playback, persistence, and exports remain outside this milestone.

The handoff will be self-contained so the execution agent won't need our conversation or the larger specification checkpoint to implement it.

<row align="center" gap={2}>
  <icon name="check-circle" color="success"/>
  **Milestone 1 handoff generated**
</row>

<box border radius="xl" padding={3} gap={2}>
  <row align="center" gap={3}>
    <icon name="file-text" size="2xl" color="secondary"/>
    <box flex="1" gap={1}>
      **handoff_261011_1.md**
      <text color="secondary" size="xs">171 lines · Markdown · Self-contained execution contract</text>
    </box>
  </row>
  [<icon name="download" inline/> Download Milestone 1 handoff](sandbox:/mnt/data/handoff_261011_1.md)
</box>

### What's in the handoff

The contract includes all required sections:

- **Context and non-goals:** Explicit Milestone 1 boundaries.
- **Specifications:** Domain entities, exact rational timing, validation, and both graphical views.
- **Implementation:** Ordered tasks for the external execution agent.
- **Tests:** Ten test groups covering domain correctness, view consistency, and GUI behavior.
- **Definition of Done:** Concrete acceptance checklist.
- **Ambiguity protocol:** Stop and report decisions that exceed the contract.

### Milestone 1 deliverables

<box gap={2}>
  <row align="center" gap={2}>
    <icon name="check-circle" color="success"/>
    Tested Python domain model
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle" color="success"/>
    Read-only PySide6 Timeline view
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle" color="success"/>
    Read-only PySide6 wrapped Sheet view
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle" color="success"/>
    Shared representative project data
  </row>
  <row align="center" gap={2}>
    <icon name="check-circle" color="success"/>
    Automated tests, screenshots, and launch instructions
  </row>
</box>

I also specified half-open beat intervals (`[start, end)`) as an internal convention, so adjacent musical regions and moves are not incorrectly classified as overlapping.

### Next step

**Phase 4 — Handoff Generation is complete.**

Review the document, then give it to your execution agent as its sole contract. The agent should stop after producing the first runnable prototype.

Once you've tested the Timeline and Sheet views, we can enter **Phase 6 — Iteration**, evaluate the results, and prepare the next handoff.

No implementation has been executed here.
