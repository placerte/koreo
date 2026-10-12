# Manual save/load review

1. Build a structure, then confirm `*` appears in the window title.
2. Use File → Save or Ctrl+S, choose a `.kro` path, and confirm `*` disappears.
3. Make another edit and press Ctrl+S. Confirm the existing path is reused.
4. Open the `.kro` file using the toolbar, File → Open, or Ctrl+O. Confirm the
   complete structure, calibration, BPM, counts, and embedded song return.
   The saved waveform should appear from its cache without a decoding delay.
5. With unsaved edits, try opening another project and closing Koreo. Confirm
   Save, Discard, and Cancel are offered and Cancel preserves the current app.
6. Move the `.kro` file elsewhere and reopen it. Embedded audio should still
   load because the project does not depend on its original filesystem path.
7. While stopped, click a waveform location and immediately set the grid
   Anchor. It must use the clicked position without requiring playback first.

The native file may contain copyrighted audio. Users are responsible for
having permission to store or share embedded content.
