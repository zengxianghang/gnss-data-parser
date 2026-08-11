"""Parser for the NovAtel OEM7 BESTVEL ASCII log.

Reference:
https://docs.novatel.com/OEM7/Content/Logs/BESTVEL.htm

The source header time and latency are preserved separately. The parser does
not silently subtract latency from the logged time tag.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from gnss_parser.common.io import TextSource, iter_text_lines

from .ascii import NovatelAsciiHeader, NovatelAsciiParseError, parse_ascii_line, peek_ascii_message_name

_MESSAGE = "BESTVELA"


@dataclass(frozen=True, slots=True)
class BestvelRecord:
    header: NovatelAsciiHeader
    sol_status: str
    vel_type: str
    latency_s: float
    age_s: float
    hor_speed_mps: float
    track_deg: float
    vert_speed_mps: float
    reserved: float
    crc: int

    @property
    def week(self) -> int:
        return self.header.week

    @property
    def sow(self) -> float:
        return self.header.sow

    @property
    def time_status(self) -> str:
        return self.header.time_status


def parse_bestvel_line(line: str, *, verify_crc: bool = False, line_number: int | None = None) -> BestvelRecord:
    message = parse_ascii_line(
        line,
        expected_message=_MESSAGE,
        verify_crc=verify_crc,
        line_number=line_number,
    )
    if len(message.fields) != 8:
        raise NovatelAsciiParseError(
            f"BESTVELA requires 8 body fields, got {len(message.fields)}",
            line_number=line_number,
        )
    f = message.fields
    try:
        return BestvelRecord(
            header=message.header,
            sol_status=f[0],
            vel_type=f[1],
            latency_s=float(f[2]),
            age_s=float(f[3]),
            hor_speed_mps=float(f[4]),
            track_deg=float(f[5]),
            vert_speed_mps=float(f[6]),
            reserved=float(f[7]),
            crc=message.crc,
        )
    except ValueError as exc:
        raise NovatelAsciiParseError(
            f"invalid BESTVELA body value: {exc}", line_number=line_number
        ) from exc


def iter_bestvel(
    source: TextSource,
    *,
    strict: bool = False,
    verify_crc: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Iterator[BestvelRecord]:
    for line_number, line in iter_text_lines(source, encoding=encoding, errors=errors):
        if peek_ascii_message_name(line) != _MESSAGE:
            continue
        try:
            yield parse_bestvel_line(line, verify_crc=verify_crc, line_number=line_number)
        except NovatelAsciiParseError:
            if strict:
                raise


def read_bestvel(
    source: TextSource,
    *,
    strict: bool = False,
    verify_crc: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> list[BestvelRecord]:
    return list(iter_bestvel(source, strict=strict, verify_crc=verify_crc, encoding=encoding, errors=errors))
