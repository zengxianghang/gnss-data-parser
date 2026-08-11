"""GPS time helpers.

The parser layer should preserve the original GNSS week and seconds-of-week
whenever possible. Normalization is therefore explicit rather than implicit.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

GPS_SECONDS_PER_WEEK = 604800.0


@dataclass(frozen=True, slots=True)
class GpsTime:
    """GPS week plus seconds-of-week.

    ``sow`` is intentionally not normalized on construction so parsers can
    preserve the value that was present in the source log. Call ``normalized``
    when a canonical ``0 <= sow < 604800`` representation is required.
    """

    week: int
    sow: float

    @property
    def absolute_seconds(self) -> float:
        """Return seconds measured from GPS week 0."""
        return self.week * GPS_SECONDS_PER_WEEK + self.sow

    def normalized(self) -> "GpsTime":
        """Return an equivalent canonical GPS week/SOW pair."""
        week, sow = normalize_gpst(self.week, self.sow)
        return GpsTime(week=week, sow=sow)


def normalize_gpst(week: int, sow: float) -> tuple[int, float]:
    """Normalize a GPS week and seconds-of-week pair.

    Values outside the nominal week are carried into adjacent weeks. This is
    useful for boundary handling while keeping normalization an explicit
    downstream choice.
    """
    if not isinstance(week, int):
        raise TypeError("week must be an int")
    if not math.isfinite(sow):
        raise ValueError("sow must be finite")

    week_offset = math.floor(sow / GPS_SECONDS_PER_WEEK)
    normalized_week = week + week_offset
    normalized_sow = sow - week_offset * GPS_SECONDS_PER_WEEK

    # Guard against floating-point edge cases at the exact week boundary.
    if normalized_sow >= GPS_SECONDS_PER_WEEK:
        normalized_week += 1
        normalized_sow -= GPS_SECONDS_PER_WEEK
    elif normalized_sow < 0.0:
        normalized_week -= 1
        normalized_sow += GPS_SECONDS_PER_WEEK

    return normalized_week, normalized_sow
