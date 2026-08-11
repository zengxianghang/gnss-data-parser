# Parser interface contract

This document defines conventions for all message parsers in this repository.

## Scope

A parser converts vendor/raw log text into structured records. It may validate syntax, decode message fields and expose explicit parser diagnostics. It must not perform application-specific accuracy analysis, truth matching, plotting or scenario classification.

## Public API

Each supported message type should provide:

- `iter_<message>(source, ...)` — streaming iterator; primary API for large logs.
- `read_<message>(source, ...)` — convenience wrapper that collects all records.
- one immutable record dataclass describing normalized output fields.

Example:

```python
for record in iter_psrvel("receiver.log"):
    use(record)

records = read_psrvel("small.log")
```

`source` should accept either a filesystem path or an already-open text stream whenever practical.

## Timing rules

1. Preserve source GNSS week and seconds-of-week as separate values when the source provides them.
2. Do not silently round, interpolate or snap epochs to another message rate.
3. Do not silently repair duplicate or backward timestamps.
4. Cross-week handling should use explicit normalization/absolute-time helpers from `gnss_parser.common.gpst`.
5. Vendor time semantics must be documented in the message module, especially when the logged epoch may be receiver-clock-corrected or expressed in UTC rather than GPST.

## Filtering rules

Parsing and filtering are separate concepts.

A parser must not silently discard a syntactically valid record just because a solution status, positioning type, satellite count, lock time, CN0 or other quality field is undesirable. If a convenience filter is provided, it must be an explicit argument whose default preserves valid parsed records.

Malformed records may be skipped by an iterator only when the behavior is documented and the caller has a way to request strict failure or diagnostics.

## Field naming

Prefer stable physical/semantic names over vendor column positions. Include units in documentation and, where ambiguity is likely, in field names.

Examples:

- `week`
- `sow`
- `vel_n_mps`
- `vel_e_mps`
- `vel_u_mps`
- `std_n_mps`
- `tracked_sv`
- `used_sv`
- `sol_status`

Do not expose a downstream contract such as `field_13` when the vendor format gives that field a stable meaning.

## Coordinate conventions

Every velocity/position parser must state its coordinate frame and sign convention. Do not convert between ECEF, ENU, NED or geodetic coordinates unless the public API explicitly promises that conversion.

## Large-file behavior

`iter_*` implementations must process input incrementally and must not read the entire file into memory. Avoid retaining raw lines in every returned record unless a diagnostic/debug option explicitly requests them.

When a log contains mixed message types, parsers should reject non-matching lines cheaply before performing expensive tokenization.

## Error handling

Message iterators use two practical modes:

- tolerant mode for large operational logs: skip unrelated lines and malformed records of the requested type;
- strict mode for tests/debugging: raise a parser-specific exception containing the source line number when available.

The first concrete NovAtel implementation establishes `NovatelAsciiParseError` for standard OEM ASCII syntax/body errors. Direct single-line parsing is always strict. `iter_psrvel(..., strict=False)` is tolerant by default; `strict=True` raises on malformed `PSRVELA` records. Unrelated message names are skipped in either mode.

Optional validation that has a meaningful processing cost, such as full CRC checking, should be explicit rather than silently enabled for every multi-GB scan.

## Testing requirements

A new parser is not complete until tests cover at least:

1. one representative valid line;
2. malformed/truncated input;
3. unrelated message input;
4. timing boundary behavior when applicable;
5. status/filter behavior when applicable;
6. a regression sample for each parser bug fixed later.

Tests should use small synthetic or sanitized samples suitable for repository storage. Do not commit proprietary large logs merely for parser tests.

## Vendor layout

- `gnss_parser.novatel` — NovAtel/OEM-style messages such as RANGE, PSRVEL, INSPVA, BESTPOS and BESTVEL.
- `gnss_parser.ublox` — u-blox/NMEA-related parsing such as RMC, plus future binary/message-specific modules when required.

Message modules should document the authoritative format reference they implement and any known firmware/version differences.
