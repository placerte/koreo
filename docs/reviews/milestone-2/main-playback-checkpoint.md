# Main playback and waveform assessment

## Start

From the repository root:

```console
uv run koreo
```

Your local test song is intentionally not part of the repository. Select it
with **Choose song…**.

## Assessment workflow

1. Confirm the selected song reports “waveform ready.”
   While it decodes, confirm a **Processing song…** activity indicator is
   visible.
2. Press **Play** and confirm audio, the seek slider, red waveform playhead,
   and fixed-width time label advance together.
3. Press **Pause** and confirm position is retained; resume with **Play**.
4. Drag the seek slider and confirm audio and the waveform playhead move to
   the selected position. Also left-click the waveform and confirm it seeks to
   that time.
5. Point at a recognizable waveform feature and turn the mouse wheel. Confirm
   zoom stays centered beneath the pointer. Middle-drag horizontally to pan.
   Also verify the **−**, **+**, and **Fit** controls. At zoom, enable
   **Follow** and confirm the red playhead stays near a fixed horizontal offset
   while the waveform moves. Left-drag the waveform to pan; crossing the drag
   threshold must suppress click-to-seek and suspend Follow. Its button resumes
   it.
6. Press **Stop** and confirm the position returns to the start.
7. Seek or play to a musical `one`, then press **Set playhead as grid anchor**.
   Confirm a green Anchor marker appears and the faint BPM grid immediately
   shifts its offset to that waveform position.
8. Optional: move later in the song, enter the continuous beat at that point
   (for example `128`), and press **Match beat to playhead**. Confirm the BPM
   updates rather than the anchor moving.
9. Switch between Timeline and Sheet and confirm playback continues without
   losing the selected song or calibration.
10. Focus several different main-window controls and press Space. Confirm it
    always toggles Play/Pause rather than activating the focused control. Tap
    BPM remains the intentional modal exception where Space records taps.

## Current checkpoint boundary

- The main playback surface and waveform-context calibration are implemented.
- The waveform currently spans the full song above the editor tabs.
- Direct calibrated beat-grid overlay and playheads inside both Timeline and
  Sheet canvases remain in progress.
- Count presentation and editor-canvas navigation are not part of this
  checkpoint; waveform wheel zoom and middle-button pan are included.

Record approval or corrections against this workflow; it is a partial
Milestone 2 review, not final Milestone 2 acceptance.
