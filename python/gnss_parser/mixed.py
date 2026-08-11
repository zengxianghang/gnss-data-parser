"""Single-pass dispatcher for mixed GNSS text logs.

This module routes supported message types to the existing message-specific
parsers while reading the source only once. It intentionally contains no
vendor-format parsing rules of its own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, Sequence

from gnss_parser.common.io import TextSource, iter_text_lines
from gnss_parser.novatel.ascii import NovatelAsciiParseError, peek_ascii_message_name
from gnss_parser.novatel.bestpos import parse_bestpos_line
from gnss_parser.novatel.bestvel import parse_bestvel_line
from gnss_parser.novatel.inspva import parse_inspva_line
from gnss_parser.novatel.psrvel import parse_psrvel_line
from gnss_parser.novatel.range import parse_range_line
from gnss_parser.ublox.rmc import NmeaParseError, parse_rmc_line, peek_rmc

SUPPORTED_MESSAGE_KEYS = (
    "psrvel",
    "range",
    "inspva",
    "bestpos",
    "bestvel",
    "rmc",
)

_NOVATEL_NAME_TO_KEY = {
    "PSRVELA": "psrvel",
    "RANGEA": "range",
    "INSPVAA": "inspva",
    "BESTPOSA": "bestpos",
    "BESTVELA": "bestvel",
}

_ALIASES = {
    "psrvel": "psrvel",
    "psrvela": "psrvel",
    "range": "range",
    "rangea": "range",
    "inspva": "inspva",
    "inspvaa": "inspva",
    "bestpos": "bestpos",
    "bestposa": "bestpos",
    "bestvel": "bestvel",
    "bestvela": "bestvel",
    "rmc": "rmc",
    "xxrmc": "rmc",
    "$xxrmc": "rmc",
}


def _zero_counts() -> dict[str, int]:
    return {key: 0 for key in SUPPORTED_MESSAGE_KEYS}


@dataclass(slots=True)
class GnssLogStats:
    """Counters collected during one mixed-log scan."""

    selected_messages: tuple[str, ...] = ()
    total_lines: int = 0
    unrelated_lines: int = 0
    target_lines: dict[str, int] = field(default_factory=_zero_counts)
    records: dict[str, int] = field(default_factory=_zero_counts)
    malformed: dict[str, int] = field(default_factory=_zero_counts)

    def reset(self, selected_messages: Sequence[str]) -> None:
        self.selected_messages = tuple(selected_messages)
        self.total_lines = 0
        self.unrelated_lines = 0
        self.target_lines = _zero_counts()
        self.records = _zero_counts()
        self.malformed = _zero_counts()


@dataclass(frozen=True, slots=True)
class GnssLogEvent:
    """One parsed record yielded by :func:`iter_gnss_log`."""

    message_type: str
    record: object
    line_number: int


@dataclass(frozen=True, slots=True)
class GnssLogResult:
    """Collected records plus statistics from :func:`read_gnss_log`."""

    records: dict[str, list[object]]
    stats: GnssLogStats

    def __getitem__(self, message_type: str) -> list[object]:
        key = normalize_message_selection((message_type,))[0]
        return self.records[key]


def normalize_message_selection(messages: str | Iterable[str] | None) -> tuple[str, ...]:
    """Normalize user-facing names to stable lower-case message keys.

    Examples accepted for NovAtel include ``RANGE``, ``RANGEA`` and ``range``.
    RMC accepts ``RMC`` and ``$xxRMC``. Unknown names are rejected explicitly.
    Returned keys always follow ``SUPPORTED_MESSAGE_KEYS`` order, including
    when the caller supplies an unordered container such as ``set``.
    """
    if messages is None:
        return SUPPORTED_MESSAGE_KEYS
    values: Iterable[str] = (messages,) if isinstance(messages, str) else messages

    selected_set: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            raise TypeError("message names must be strings")
        alias = value.strip().lower()
        key = _ALIASES.get(alias)
        if key is None:
            supported = ", ".join(SUPPORTED_MESSAGE_KEYS)
            raise ValueError(f"unsupported message type {value!r}; supported keys: {supported}")
        selected_set.add(key)
    return tuple(key for key in SUPPORTED_MESSAGE_KEYS if key in selected_set)


def _identify_message(line: str) -> str | None:
    if line.startswith("#"):
        return _NOVATEL_NAME_TO_KEY.get(peek_ascii_message_name(line))
    if peek_rmc(line):
        return "rmc"
    return None


def _parse_target_line(
    key: str,
    line: str,
    *,
    verify_crc: bool,
    verify_checksum: bool,
    line_number: int,
) -> object:
    if key == "psrvel":
        return parse_psrvel_line(line, verify_crc=verify_crc, line_number=line_number)
    if key == "range":
        return parse_range_line(line, verify_crc=verify_crc, line_number=line_number)
    if key == "inspva":
        return parse_inspva_line(line, verify_crc=verify_crc, line_number=line_number)
    if key == "bestpos":
        return parse_bestpos_line(line, verify_crc=verify_crc, line_number=line_number)
    if key == "bestvel":
        return parse_bestvel_line(line, verify_crc=verify_crc, line_number=line_number)
    if key == "rmc":
        return parse_rmc_line(
            line, verify_checksum=verify_checksum, line_number=line_number
        )
    raise AssertionError(f"unregistered message key: {key}")


def iter_gnss_log(
    source: TextSource,
    *,
    messages: str | Iterable[str] | None = None,
    strict: bool = False,
    verify_crc: bool = False,
    verify_checksum: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
    stats: GnssLogStats | None = None,
) -> Iterator[GnssLogEvent]:
    """Yield selected supported records while scanning ``source`` exactly once.

    ``messages=None`` selects every currently supported message type. Pass a
    :class:`GnssLogStats` instance when scan statistics are needed after the
    iterator is exhausted.
    """
    selected = normalize_message_selection(messages)
    selected_set = set(selected)
    scan_stats = stats if stats is not None else GnssLogStats()
    scan_stats.reset(selected)

    for line_number, line in iter_text_lines(source, encoding=encoding, errors=errors):
        scan_stats.total_lines += 1
        key = _identify_message(line)
        if key is None or key not in selected_set:
            scan_stats.unrelated_lines += 1
            continue

        scan_stats.target_lines[key] += 1
        try:
            record = _parse_target_line(
                key,
                line,
                verify_crc=verify_crc,
                verify_checksum=verify_checksum,
                line_number=line_number,
            )
        except (NovatelAsciiParseError, NmeaParseError):
            scan_stats.malformed[key] += 1
            if strict:
                raise
            continue

        scan_stats.records[key] += 1
        yield GnssLogEvent(
            message_type=key,
            record=record,
            line_number=line_number,
        )


def read_gnss_log(
    source: TextSource,
    *,
    messages: str | Iterable[str] | None = None,
    strict: bool = False,
    verify_crc: bool = False,
    verify_checksum: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> GnssLogResult:
    """Collect selected message types from one physical/logical source scan."""
    selected = normalize_message_selection(messages)
    records: dict[str, list[object]] = {
        key: [] for key in SUPPORTED_MESSAGE_KEYS
    }
    stats = GnssLogStats()
    for event in iter_gnss_log(
        source,
        messages=selected,
        strict=strict,
        verify_crc=verify_crc,
        verify_checksum=verify_checksum,
        encoding=encoding,
        errors=errors,
        stats=stats,
    ):
        records[event.message_type].append(event.record)
    return GnssLogResult(records=records, stats=stats)
