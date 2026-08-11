"""Streaming parser for NMEA RMC sentences as output by u-blox receivers.

The parser preserves NMEA UTC/date text and does not convert UTC to GPST or
infer a century for the two-digit RMC year.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from gnss_parser.common.io import TextSource, iter_text_lines


class NmeaParseError(ValueError):
    """Raised when a target NMEA sentence cannot be decoded."""

    def __init__(self, message: str, *, line_number: int | None = None) -> None:
        self.line_number = line_number
        prefix = f"line {line_number}: " if line_number is not None else ""
        super().__init__(prefix + message)


@dataclass(frozen=True, slots=True)
class RmcRecord:
    talker_id: str
    utc_time: str
    utc_seconds_of_day: float | None
    status: str
    latitude_deg: float | None
    longitude_deg: float | None
    speed_knots: float | None
    course_deg: float | None
    date_ddmmyy: str
    magnetic_variation_deg: float | None
    magnetic_variation_ew: str
    position_mode: str
    navigation_status: str
    checksum: int


def nmea_checksum(payload: str) -> int:
    """Return NMEA XOR checksum for text between ``$`` and ``*``."""
    value = 0
    for char in payload:
        value ^= ord(char)
    return value


def _optional_float(text: str, *, field_name: str, line_number: int | None) -> float | None:
    if text == "":
        return None
    try:
        return float(text)
    except ValueError as exc:
        raise NmeaParseError(f"invalid {field_name}: {text!r}", line_number=line_number) from exc


def _parse_utc_seconds(text: str, *, line_number: int | None) -> float | None:
    if text == "":
        return None
    if len(text) < 6:
        raise NmeaParseError("RMC UTC time must be hhmmss[.sss]", line_number=line_number)
    try:
        hour = int(text[0:2], 10)
        minute = int(text[2:4], 10)
        second = float(text[4:])
    except ValueError as exc:
        raise NmeaParseError(f"invalid RMC UTC time: {text!r}", line_number=line_number) from exc
    if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0.0 <= second < 60.0):
        raise NmeaParseError(f"RMC UTC time out of range: {text!r}", line_number=line_number)
    return hour * 3600.0 + minute * 60.0 + second


def _parse_coordinate(
    value_text: str,
    hemisphere: str,
    *,
    latitude: bool,
    line_number: int | None,
) -> float | None:
    if value_text == "":
        if hemisphere not in ("",):
            raise NmeaParseError("hemisphere present while coordinate is empty", line_number=line_number)
        return None
    try:
        value = float(value_text)
    except ValueError as exc:
        raise NmeaParseError(f"invalid NMEA coordinate: {value_text!r}", line_number=line_number) from exc
    degrees = int(value // 100)
    minutes = value - degrees * 100
    if not (0.0 <= minutes < 60.0):
        raise NmeaParseError(f"coordinate minutes out of range: {value_text!r}", line_number=line_number)
    if latitude:
        if hemisphere not in ("N", "S") or not (0 <= degrees <= 90):
            raise NmeaParseError("invalid latitude hemisphere/range", line_number=line_number)
        sign = -1.0 if hemisphere == "S" else 1.0
    else:
        if hemisphere not in ("E", "W") or not (0 <= degrees <= 180):
            raise NmeaParseError("invalid longitude hemisphere/range", line_number=line_number)
        sign = -1.0 if hemisphere == "W" else 1.0
    result = sign * (degrees + minutes / 60.0)
    limit = 90.0 if latitude else 180.0
    if abs(result) > limit:
        raise NmeaParseError("coordinate out of range", line_number=line_number)
    return result


def peek_rmc(line: str) -> bool:
    """Cheaply identify direct ``$xxRMC`` sentences."""
    return len(line) >= 6 and line[0] == "$" and line[3:6] == "RMC"


def parse_rmc_line(
    line: str,
    *,
    verify_checksum: bool = False,
    line_number: int | None = None,
) -> RmcRecord:
    line = line.rstrip("\r\n")
    if not peek_rmc(line):
        raise NmeaParseError("expected $xxRMC sentence", line_number=line_number)

    star = line.rfind("*")
    if star < 0:
        raise NmeaParseError("missing NMEA checksum delimiter '*'", line_number=line_number)
    checksum_text = line[star + 1 :]
    if len(checksum_text) != 2:
        raise NmeaParseError("NMEA checksum must be two hexadecimal digits", line_number=line_number)
    try:
        checksum = int(checksum_text, 16)
    except ValueError as exc:
        raise NmeaParseError("NMEA checksum is not hexadecimal", line_number=line_number) from exc

    payload = line[1:star]
    if verify_checksum:
        calculated = nmea_checksum(payload)
        if calculated != checksum:
            raise NmeaParseError(
                f"NMEA checksum mismatch: expected {checksum:02X}, calculated {calculated:02X}",
                line_number=line_number,
            )

    fields = payload.split(",")
    message_id = fields[0]
    if len(message_id) != 5 or message_id[2:] != "RMC":
        raise NmeaParseError(f"invalid RMC message ID: {message_id!r}", line_number=line_number)
    talker_id = message_id[:2]
    if not talker_id.isalnum():
        raise NmeaParseError(f"invalid RMC talker ID: {talker_id!r}", line_number=line_number)

    # Required RMC core runs through date. Later NMEA versions append magnetic
    # variation, position mode and navigation status; missing trailing fields
    # are represented as empty strings for legacy compatibility.
    if len(fields) < 10:
        raise NmeaParseError(
            f"RMC requires at least 10 comma fields including message ID, got {len(fields)}",
            line_number=line_number,
        )
    padded = fields + [""] * max(0, 14 - len(fields))
    if len(padded) > 14:
        raise NmeaParseError(
            f"RMC has unexpected extra fields: {len(fields)} total",
            line_number=line_number,
        )

    utc_time = padded[1]
    status = padded[2]
    if status not in ("A", "V", ""):
        raise NmeaParseError(f"invalid RMC status: {status!r}", line_number=line_number)

    latitude_deg = _parse_coordinate(
        padded[3], padded[4], latitude=True, line_number=line_number
    )
    longitude_deg = _parse_coordinate(
        padded[5], padded[6], latitude=False, line_number=line_number
    )
    magnetic_variation = _optional_float(
        padded[10], field_name="magnetic variation", line_number=line_number
    )
    magnetic_ew = padded[11]
    if magnetic_ew not in ("", "E", "W"):
        raise NmeaParseError(
            f"invalid magnetic variation direction: {magnetic_ew!r}",
            line_number=line_number,
        )
    if magnetic_variation is not None and magnetic_ew == "W":
        magnetic_variation = -magnetic_variation

    return RmcRecord(
        talker_id=talker_id,
        utc_time=utc_time,
        utc_seconds_of_day=_parse_utc_seconds(utc_time, line_number=line_number),
        status=status,
        latitude_deg=latitude_deg,
        longitude_deg=longitude_deg,
        speed_knots=_optional_float(padded[7], field_name="speed over ground", line_number=line_number),
        course_deg=_optional_float(padded[8], field_name="course over ground", line_number=line_number),
        date_ddmmyy=padded[9],
        magnetic_variation_deg=magnetic_variation,
        magnetic_variation_ew=magnetic_ew,
        position_mode=padded[12],
        navigation_status=padded[13],
        checksum=checksum,
    )


def iter_rmc(
    source: TextSource,
    *,
    strict: bool = False,
    verify_checksum: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Iterator[RmcRecord]:
    for line_number, line in iter_text_lines(source, encoding=encoding, errors=errors):
        if not peek_rmc(line):
            continue
        try:
            yield parse_rmc_line(line, verify_checksum=verify_checksum, line_number=line_number)
        except NmeaParseError:
            if strict:
                raise


def read_rmc(
    source: TextSource,
    *,
    strict: bool = False,
    verify_checksum: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> list[RmcRecord]:
    return list(iter_rmc(source, strict=strict, verify_checksum=verify_checksum, encoding=encoding, errors=errors))
