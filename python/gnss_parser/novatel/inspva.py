"""Parser for the NovAtel OEM7 INSPVA ASCII log.

Reference:
https://docs.novatel.com/OEM7/Content/SPAN_Logs/INSPVA.htm

INS logs include an applicability time in the data block. NovAtel documents the
data-block time as the exact time of applicability, so ``week`` and ``sow`` on
``InspvaRecord`` refer to the data block while the complete standard header is
also preserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from gnss_parser.common.io import TextSource, iter_text_lines

from .ascii import NovatelAsciiHeader, NovatelAsciiParseError, parse_ascii_line, peek_ascii_message_name

_MESSAGE = "INSPVAA"


@dataclass(frozen=True, slots=True)
class InspvaRecord:
    """One NovAtel INSPVAA record."""

    header: NovatelAsciiHeader
    week: int
    sow: float
    latitude_deg: float
    longitude_deg: float
    ellipsoidal_height_m: float
    vel_n_mps: float
    vel_e_mps: float
    vel_u_mps: float
    roll_deg: float
    pitch_deg: float
    azimuth_deg: float
    ins_status: str
    crc: int

    @property
    def header_week(self) -> int:
        return self.header.week

    @property
    def header_sow(self) -> float:
        return self.header.sow

    @property
    def time_status(self) -> str:
        return self.header.time_status


def parse_inspva_line(
    line: str,
    *,
    verify_crc: bool = False,
    line_number: int | None = None,
) -> InspvaRecord:
    """Parse one exact ``#INSPVAA`` standard ASCII sentence."""
    message = parse_ascii_line(
        line,
        expected_message=_MESSAGE,
        verify_crc=verify_crc,
        line_number=line_number,
    )
    if len(message.fields) != 12:
        raise NovatelAsciiParseError(
            f"INSPVAA requires 12 body fields, got {len(message.fields)}",
            line_number=line_number,
        )
    fields = message.fields
    try:
        return InspvaRecord(
            header=message.header,
            week=int(fields[0], 10),
            sow=float(fields[1]),
            latitude_deg=float(fields[2]),
            longitude_deg=float(fields[3]),
            ellipsoidal_height_m=float(fields[4]),
            vel_n_mps=float(fields[5]),
            vel_e_mps=float(fields[6]),
            vel_u_mps=float(fields[7]),
            roll_deg=float(fields[8]),
            pitch_deg=float(fields[9]),
            azimuth_deg=float(fields[10]),
            ins_status=fields[11],
            crc=message.crc,
        )
    except ValueError as exc:
        raise NovatelAsciiParseError(
            f"invalid INSPVAA body value: {exc}", line_number=line_number
        ) from exc


def iter_inspva(
    source: TextSource,
    *,
    strict: bool = False,
    verify_crc: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Iterator[InspvaRecord]:
    """Yield INSPVAA records incrementally from a mixed text log."""
    for line_number, line in iter_text_lines(source, encoding=encoding, errors=errors):
        if peek_ascii_message_name(line) != _MESSAGE:
            continue
        try:
            yield parse_inspva_line(line, verify_crc=verify_crc, line_number=line_number)
        except NovatelAsciiParseError:
            if strict:
                raise


def read_inspva(
    source: TextSource,
    *,
    strict: bool = False,
    verify_crc: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> list[InspvaRecord]:
    """Collect all INSPVAA records from ``source`` into a list."""
    return list(iter_inspva(source, strict=strict, verify_crc=verify_crc, encoding=encoding, errors=errors))
