"""Shared parser for standard NovAtel OEM ASCII message envelopes.

Reference:
https://docs.novatel.com/OEM7/Content/Messages/ASCII.htm
"""

from __future__ import annotations

import csv
from dataclasses import dataclass


class NovatelAsciiParseError(ValueError):
    """Raised when a NovAtel standard ASCII message cannot be decoded."""

    def __init__(self, message: str, *, line_number: int | None = None) -> None:
        self.line_number = line_number
        prefix = f"line {line_number}: " if line_number is not None else ""
        super().__init__(prefix + message)


@dataclass(frozen=True, slots=True)
class NovatelAsciiHeader:
    """Fields from the standard OEM ASCII message header."""

    message: str
    port: str
    sequence: int
    idle_time_pct: float
    time_status: str
    week: int
    sow: float
    receiver_status: int
    reserved: int
    software_version: int


@dataclass(frozen=True, slots=True)
class NovatelAsciiMessage:
    """Decoded standard OEM ASCII envelope plus untyped body fields."""

    header: NovatelAsciiHeader
    fields: tuple[str, ...]
    crc: int


def peek_ascii_message_name(line: str) -> str | None:
    """Return the exact standard ASCII message name without tokenizing the line."""
    if not line.startswith("#"):
        return None
    comma = line.find(",", 1)
    semicolon = line.find(";", 1)
    candidates = [index for index in (comma, semicolon) if index >= 0]
    if not candidates:
        return None
    return line[1:min(candidates)]


def novatel_crc32(data: bytes) -> int:
    """Calculate the 32-bit CRC used by NovAtel OEM ASCII/Binary messages."""
    crc = 0
    for byte in data:
        value = (crc ^ byte) & 0xFF
        for _ in range(8):
            if value & 1:
                value = (value >> 1) ^ 0xEDB88320
            else:
                value >>= 1
        crc = ((crc >> 8) & 0x00FFFFFF) ^ value
    return crc & 0xFFFFFFFF


def _split_csv(text: str, *, line_number: int | None) -> tuple[str, ...]:
    try:
        return tuple(next(csv.reader([text], delimiter=",", quotechar='"', strict=True)))
    except (csv.Error, StopIteration) as exc:
        raise NovatelAsciiParseError(
            f"invalid comma-delimited field syntax: {exc}", line_number=line_number
        ) from exc


def parse_ascii_line(
    line: str,
    *,
    expected_message: str | None = None,
    verify_crc: bool = False,
    line_number: int | None = None,
) -> NovatelAsciiMessage:
    """Parse one standard NovAtel ASCII line.

    ``expected_message`` is matched exactly, including the ASCII ``A`` suffix.
    ``verify_crc`` is opt-in so large-file callers control the CRC cost.
    """
    line = line.rstrip("\r\n")
    if not line.startswith("#"):
        raise NovatelAsciiParseError(
            "standard ASCII message must start with '#'", line_number=line_number
        )

    star = line.rfind("*")
    if star < 0:
        raise NovatelAsciiParseError(
            "missing CRC delimiter '*'", line_number=line_number
        )

    crc_text = line[star + 1 :]
    if len(crc_text) != 8:
        raise NovatelAsciiParseError(
            "CRC must contain exactly 8 hexadecimal digits", line_number=line_number
        )
    try:
        crc = int(crc_text, 16)
    except ValueError as exc:
        raise NovatelAsciiParseError(
            "CRC contains non-hexadecimal characters", line_number=line_number
        ) from exc

    content = line[1:star]
    semicolon = content.find(";")
    if semicolon < 0:
        raise NovatelAsciiParseError(
            "missing header/data delimiter ';'", line_number=line_number
        )

    header_fields = _split_csv(content[:semicolon], line_number=line_number)
    if len(header_fields) != 10:
        raise NovatelAsciiParseError(
            f"standard ASCII header requires 10 fields, got {len(header_fields)}",
            line_number=line_number,
        )

    try:
        header = NovatelAsciiHeader(
            message=header_fields[0],
            port=header_fields[1],
            sequence=int(header_fields[2], 10),
            idle_time_pct=float(header_fields[3]),
            time_status=header_fields[4],
            week=int(header_fields[5], 10),
            sow=float(header_fields[6]),
            receiver_status=int(header_fields[7], 16),
            reserved=int(header_fields[8], 16),
            software_version=int(header_fields[9], 10),
        )
    except ValueError as exc:
        raise NovatelAsciiParseError(
            f"invalid standard ASCII header value: {exc}", line_number=line_number
        ) from exc

    if expected_message is not None and header.message != expected_message:
        raise NovatelAsciiParseError(
            f"expected message {expected_message!r}, got {header.message!r}",
            line_number=line_number,
        )

    fields = _split_csv(content[semicolon + 1 :], line_number=line_number)

    if verify_crc:
        try:
            calculated = novatel_crc32(content.encode("ascii"))
        except UnicodeEncodeError as exc:
            raise NovatelAsciiParseError(
                "CRC verification requires ASCII message bytes", line_number=line_number
            ) from exc
        if calculated != crc:
            raise NovatelAsciiParseError(
                f"CRC mismatch: expected {crc:08x}, calculated {calculated:08x}",
                line_number=line_number,
            )

    return NovatelAsciiMessage(header=header, fields=fields, crc=crc)
