"""Exact constant-tempo calibration and tap-tempo estimation."""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from fractions import Fraction

# [GH-15] [S-M2-02] [S-M2-03] Exact calibration and tap-tempo rules.


class CalibrationError(ValueError):
    """Raised when calibration input cannot define a valid tempo map."""


def parse_bpm(text: str) -> Fraction:
    """Parse a positive decimal BPM without introducing binary-float error."""

    try:
        value = Decimal(text.strip())
    except InvalidOperation as error:
        raise CalibrationError("BPM must be a decimal number") from error
    if not value.is_finite() or value <= 0:
        raise CalibrationError("BPM must be a positive finite number")
    return Fraction(value)


@dataclass(frozen=True, slots=True)
class BeatCalibration:
    """An exact mapping between authoritative beats and media seconds."""

    bpm: Fraction
    anchor_seconds: Fraction
    anchor_beat: Fraction = Fraction(0)
    calibration_beat: Fraction | None = None
    calibration_seconds: Fraction | None = None

    def __post_init__(self) -> None:
        values = (self.bpm, self.anchor_seconds, self.anchor_beat)
        if not all(isinstance(value, Fraction) for value in values):
            raise CalibrationError("Calibration values must use Fraction")
        if self.bpm <= 0:
            raise CalibrationError("BPM must be positive")
        has_beat = self.calibration_beat is not None
        has_seconds = self.calibration_seconds is not None
        if has_beat != has_seconds:
            raise CalibrationError("Calibration point requires both beat and seconds")
        if has_beat:
            assert self.calibration_beat is not None
            assert self.calibration_seconds is not None
            if not isinstance(self.calibration_beat, Fraction) or not isinstance(
                self.calibration_seconds, Fraction
            ):
                raise CalibrationError("Calibration point values must use Fraction")
            _validate_point_deltas(
                self.calibration_beat - self.anchor_beat,
                self.calibration_seconds - self.anchor_seconds,
            )

    def seconds_at(self, beat: Fraction) -> Fraction:
        """Return the exact media time corresponding to ``beat``."""

        if not isinstance(beat, Fraction):
            raise CalibrationError("Beat must use Fraction")
        return self.anchor_seconds + (beat - self.anchor_beat) * 60 / self.bpm

    def beat_at(self, seconds: Fraction) -> Fraction:
        """Return the exact beat corresponding to a media time."""

        if not isinstance(seconds, Fraction):
            raise CalibrationError("Seconds must use Fraction")
        return self.anchor_beat + (seconds - self.anchor_seconds) * self.bpm / 60

    def with_bpm(self, bpm: Fraction) -> "BeatCalibration":
        """Return the same anchor with a new BPM and no stale second point."""

        return BeatCalibration(bpm, self.anchor_seconds, self.anchor_beat)

    def with_anchor(self, anchor_seconds: Fraction) -> "BeatCalibration":
        """Return the same musical anchor at a new media time."""

        return BeatCalibration(self.bpm, anchor_seconds, self.anchor_beat)

    def with_calibration_point(
        self, beat: Fraction, seconds: Fraction
    ) -> "BeatCalibration":
        """Refine global BPM from a matching grid beat and media position."""

        if not isinstance(beat, Fraction) or not isinstance(seconds, Fraction):
            raise CalibrationError("Calibration point values must use Fraction")
        beat_delta = beat - self.anchor_beat
        seconds_delta = seconds - self.anchor_seconds
        _validate_point_deltas(beat_delta, seconds_delta)
        bpm = 60 * beat_delta / seconds_delta
        return BeatCalibration(
            bpm=bpm,
            anchor_seconds=self.anchor_seconds,
            anchor_beat=self.anchor_beat,
            calibration_beat=beat,
            calibration_seconds=seconds,
        )


def _validate_point_deltas(beat_delta: Fraction, seconds_delta: Fraction) -> None:
    if beat_delta == 0 or seconds_delta == 0:
        raise CalibrationError("Calibration point must differ from the anchor")
    if (beat_delta > 0) != (seconds_delta > 0):
        raise CalibrationError(
            "Calibration beat and media time must have the same direction"
        )


@dataclass(slots=True)
class TapTempo:
    """Deterministic first-to-last tap estimator with inactivity reset."""

    timeout_seconds: Fraction = Fraction(3)
    _taps: list[Fraction] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("Tap timeout must be positive")

    @property
    def tap_count(self) -> int:
        """Return the number of taps in the active session."""

        return len(self._taps)

    @property
    def estimate(self) -> Fraction | None:
        """Return the current BPM estimate, or ``None`` before two taps."""

        if len(self._taps) < 2:
            return None
        elapsed = self._taps[-1] - self._taps[0]
        return 60 * (len(self._taps) - 1) / elapsed

    def tap(self, timestamp: Fraction, *, auto_repeat: bool = False) -> Fraction | None:
        """Record one monotonic tap and return the updated estimate."""

        if not isinstance(timestamp, Fraction):
            raise CalibrationError("Tap timestamp must use Fraction")
        if auto_repeat:
            return self.estimate
        if self._taps and timestamp <= self._taps[-1]:
            raise CalibrationError("Tap timestamps must increase")
        if self._taps and timestamp - self._taps[-1] >= self.timeout_seconds:
            self.reset()
        self._taps.append(timestamp)
        return self.estimate

    def reset(self) -> None:
        """Clear the active tapping session."""

        self._taps.clear()
