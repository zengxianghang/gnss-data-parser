"""Parser for the NovAtel OEM7 RANGE ASCII log.

Reference:
https://docs.novatel.com/OEM7/Content/Logs/RANGE.htm
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

_MESSAGE = "RANGEA"
_FIELDS_PER_OBSERVATION = 10

_SYSTEM_NAMES = {
    0: "GPS",
    1: "GLONASS",
    2: "SBAS",
    3: "GALILEO",
    4: "BEIDOU",
    5: "QZSS",
    6: "NAVIC",
    7: "OTHER",
}

_SIGNAL_NAMES = {
    0: {0: "L1CA", 5: "L2P", 9: "L2P_Y", 14: "L5Q", 16: "L1CP", 17: "L2CM"},
    1: {0: "L1CA", 1: "L2CA", 5: "L2P", 6: "L3Q"},
    2: {0: "L1CA", 6: "L5I"},
    3: {2: "E1C", 6: "E6B", 7: "E6C", 12: "E5AQ", 17: "E5BQ", 20: "E5ALTBOCQ"},
    4: {0: "B1I_D1", 1: "B2I_D1", 2: "B3I_D1", 4: "B1I_D2", 5: "B2I_D2", 6: "B3I_D2", 7: "B1CP", 9: "B2AP", 11: "B2BI"},
    5: {0: "L1CA", 14: "L5Q", 16: "L1CP", 17: "L2CM", 27: "L6P", 28: "L6D"},
    6: {0: "L5SPS"},
    7: {19: "LBAND"},
}


@dataclass(frozen=True, slots=True)
class TrackingStatus:
    raw: int
    tracking_state: int
    sv_channel: int
    phase_locked: bool
    parity_known: bool
    code_locked: bool
    correlator_type: int
    satellite_system: int
    satellite_system_name: str
    grouped: bool
    signal_type: int
    signal_name: str
    primary_l1: bool
    half_cycle_added: bool
    digital_filter: bool
    prn_locked_out: bool
    forced_assignment: bool


@dataclass(frozen=True, slots=True)
class RangeObservation:
    prn: int
    glofreq: int
    pseudorange_m: float
    pseudorange_std_m: float
    adr_cycles: float
    adr_std_cycles: float
    doppler_hz: float
    cn0_dbhz: float
    lock_time_s: float
    tracking: TrackingStatus


@dataclass(frozen=True, slots=True)
class RangeRecord:
    header: NovatelAsciiHeader
    observations: tuple[RangeObservation, ...]
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

    @property
    def observation_count(self) -> int:
        return len(self.observations)


def decode_tracking_status(value: int) -> TrackingStatus:
    """Decode the OEM7 32-bit RANGE channel tracking status word."""
    system = (value >> 16) & 0x7
    signal = (value >> 21) & 0x1F
    return TrackingStatus(
        raw=value,
        tracking_state=value & 0x1F,
        sv_channel=(value >> 5) & 0x1F,
        phase_locked=bool(value & (1 << 10)),
        parity_known=bool(value & (1 << 11)),
        code_locked=bool(value & (1 << 12)),
        correlator_type=(value >> 13) & 0x7,
        satellite_system=system,
        satellite_system_name=_SYSTEM_NAMES.get(system, f"SYSTEM_{system}"),
        grouped=bool(value & (1 << 20)),
        signal_type=signal,
        signal_name=_SIGNAL_NAMES.get(system, {}).get(signal, f"SIGNAL_{signal}"),
        primary_l1=bool(value & (1 << 27)),
        half_cycle_added=bool(value & (1 << 28)),
        digital_filter=bool(value & (1 << 29)),
        prn_locked_out=bool(value & (1 << 30)),
        forced_assignment=bool(value & (1 << 31)),
    )


def parse_range_line(
    line: str,
    *,
    verify_crc: bool = False,
    line_number: int | None = None,
) -> RangeRecord:
    """Parse one exact ``#RANGEA`` standard ASCII sentence."""
    message = parse_ascii_line(
        line,
        expected_message=_MESSAGE,
        verify_crc=verify_crc,
        line_number=line_number,
    )
    if not message.fields:
        raise NovatelAsciiParseError("RANGEA body is empty", line_number=line_number)

    try:
        count = int(message.fields[0], 10)
    except ValueError as exc:
        raise NovatelAsciiParseError(
            f"invalid RANGEA observation count: {exc}", line_number=line_number
        ) from exc
    if count < 0:
        raise NovatelAsciiParseError(
            "RANGEA observation count cannot be negative", line_number=line_number
        )

    expected_fields = 1 + count * _FIELDS_PER_OBSERVATION
    if len(message.fields) != expected_fields:
        raise NovatelAsciiParseError(
            f"RANGEA declares {count} observations but body has {len(message.fields) - 1} observation fields; expected {count * _FIELDS_PER_OBSERVATION}",
            line_number=line_number,
        )

    observations: list[RangeObservation] = []
    for index in range(count):
        start = 1 + index * _FIELDS_PER_OBSERVATION
        fields = message.fields[start : start + _FIELDS_PER_OBSERVATION]
        try:
            tracking_raw = int(fields[9], 16)
            observation = RangeObservation(
                prn=int(fields[0], 10),
                glofreq=int(fields[1], 10),
                pseudorange_m=float(fields[2]),
                pseudorange_std_m=float(fields[3]),
                adr_cycles=float(fields[4]),
                adr_std_cycles=float(fields[5]),
                doppler_hz=float(fields[6]),
                cn0_dbhz=float(fields[7]),
                lock_time_s=float(fields[8]),
                tracking=decode_tracking_status(tracking_raw),
            )
        except ValueError as exc:
            raise NovatelAsciiParseError(
                f"invalid RANGEA observation {index + 1}: {exc}",
                line_number=line_number,
            ) from exc
        observations.append(observation)

    return RangeRecord(
        header=message.header,
        observations=tuple(observations),
        crc=message.crc,
    )


def iter_range(
    source: TextSource,
    *,
    strict: bool = False,
    verify_crc: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Iterator[RangeRecord]:
    """Yield RANGEA epochs incrementally from a mixed text log."""
    for line_number, line in iter_text_lines(source, encoding=encoding, errors=errors):
        if peek_ascii_message_name(line) != _MESSAGE:
            continue
        try:
            yield parse_range_line(
                line, verify_crc=verify_crc, line_number=line_number
            )
        except NovatelAsciiParseError:
            if strict:
                raise


def read_range(
    source: TextSource,
    *,
    strict: bool = False,
    verify_crc: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> list[RangeRecord]:
    """Collect all RANGEA epochs from ``source`` into a list."""
    return list(
        iter_range(
            source,
            strict=strict,
            verify_crc=verify_crc,
            encoding=encoding,
            errors=errors,
        )
    )
