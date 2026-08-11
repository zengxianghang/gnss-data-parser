"""Parser for the NovAtel OEM7 PSRVEL ASCII log.

Reference:
https://docs.novatel.com/OEM7/Content/Logs/PSRVEL.htm

The source ``week`` and ``sow`` are preserved exactly as represented by the
header. The PSRVEL time of validity is header time minus ``latency_s``; this
module does not silently alter the source timestamp.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from gnss_parser.common.io import TextSource, iter_text_lines

from .ascii import (
    NovatelAsciiHeader,
    NovatelAsciiParseError,
    parse_ascii_line,
    peek_ascii_message_name,
)

_MESSAGE = "PSRVELA"


@dataclass(frozen=True, slots=True)
class PsrvelRecord:
    """One NovAtel PSRVELA record."""

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


def parse_psrvel_line(
    line: str,
    *,
    verify_crc: bool = False,
    line_number: int | None = None,
) -> PsrvelRecord:
    """Parse one exact ``#PSRVELA`` standard ASCII line."""
    message = parse_ascii_line(
        line,
        expected_message=_MESSAGE,
        verify_crc=verify_crc,
        line_number=line_number,
    )
    if len(message.fields) != 8:
        raise NovatelAsciiParseError(
            f"PSRVELA requires 8 body fields, got {len(message.fields)}",
            line_number=line_number,
        )

    fields = message.fields
    try:
        return PsrvelRecord(
            header=message.header,
            sol_status=fields[0],
            vel_type=fields[1],
            latency_s=float(fields[2]),
            age_s=float(fields[3]),
            hor_speed_mps=float(fields[4]),
            track_deg=float(fields[5]),
            vert_speed_mps=float(fields[6]),
            reserved=float(fields[7]),
            crc=message.crc,
        )
    except ValueError as exc:
        raise NovatelAsciiParseError(
            f"invalid PSRVELA body value: {exc}", line_number=line_number
        ) from exc


def iter_psrvel(
    source: TextSource,
    *,
    strict: bool = False,
    verify_crc: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Iterator[PsrvelRecord]:
    """Yield PSRVELA records incrementally from a mixed text log.

    Unrelated message types are always skipped. In tolerant mode (default),
    malformed PSRVELA records are skipped. With ``strict=True``, malformed
    PSRVELA records raise ``NovatelAsciiParseError`` with a 1-based line number.
    """
    for line_number, line in iter_text_lines(
        source, encoding=encoding, errors=errors
    ):
        if peek_ascii_message_name(line) != _MESSAGE:
            continue
        try:
            yield parse_psrvel_line(
                line, verify_crc=verify_crc, line_number=line_number
            )
        except NovatelAsciiParseError:
            if strict:
                raise


def read_psrvel(
    source: TextSource,
    *,
    strict: bool = False,
    verify_crc: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> list[PsrvelRecord]:
    """Collect all PSRVELA records from ``source`` into a list."""
    return list(
        iter_psrvel(
            source,
            strict=strict,
            verify_crc=verify_crc,
            encoding=encoding,
            errors=errors,
        )
    )
