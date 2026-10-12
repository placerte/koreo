# Count presentation assessment

## Start

```console
uv run koreo
```

No song is required for this review.

## Assessment workflow

1. Compare Timeline and Sheet and confirm both show the same local dance count
   at each beat.
2. Change **Count origin** to `-2`. Confirm both views update together and the
   timing/geometry of regions and moves remains unchanged.
3. Change **Default group** between `6` and `8`. Confirm regions with their own
   group override retain that override.
4. Enable **Continuous beat numbers**. Confirm secondary continuous labels
   appear in both views while local dance counts remain primary.
5. Disable continuous numbers and confirm only presentation changes.
6. Inspect region boundaries: regions restart at `1` by default, nested region
   entry can restart independently, and incomplete groups are not padded.

## Current boundary

- Count mapping and global presentation controls are implemented.
- Regional group-size and restart/continue editing belongs to the future
  song-structure editor; current fixture metadata exercises those behaviors.
- Calibration UX remains deferred until that structure editor exists.
