# NovAtel parser notes

This document records the format assumptions used by `gnss_parser.novatel`.

## Authoritative references

- Standard OEM ASCII: <https://docs.novatel.com/OEM7/Content/Messages/ASCII.htm>
- PSRVEL: <https://docs.novatel.com/OEM7/Content/Logs/PSRVEL.htm>
- RANGE: <https://docs.novatel.com/OEM7/Content/Logs/RANGE.htm>
- INSPVA: <https://docs.novatel.com/OEM7/Content/SPAN_Logs/INSPVA.htm>
- BESTPOS: <https://docs.novatel.com/OEM7/Content/Logs/BESTPOS.htm>
- BESTVEL: <https://docs.novatel.com/OEM7/Content/Logs/BESTVEL.htm>

The implementation targets standard `#...A` ASCII messages. CRC verification is opt-in for large-file scans.

## PSRVELA

Preserves source header time and latency separately; no hidden solution filtering.

## RANGEA

Returns immutable epochs/observations with raw and decoded channel tracking status; no hidden observation-quality filtering.

## INSPVAA

`InspvaRecord.week/sow` use the INS data-block applicability time. `header_week/header_sow` preserve the standard header time tag. Position, N/E/U velocity, attitude and INS status are exposed without hidden filtering.

## BESTPOSA

Returns all 21 ASCII body fields including MSL height and undulation separately, position standard deviations, satellite counts and status/signal masks. No implicit MSL-to-ellipsoidal conversion or solution filtering is performed.

## BESTVELA

Public APIs:

```python
from gnss_parser.novatel import iter_bestvel, parse_bestvel_line, read_bestvel
```

`BestvelRecord` exposes solution status/type, `latency_s`, differential age, horizontal speed, track over ground relative to True North, vertical speed (positive up), reserved field, CRC and the complete standard header.

The header week/SOW is preserved exactly. NovAtel defines the improved time of validity as header time minus latency; the parser deliberately does not apply that shift implicitly.

A syntactically valid record is returned regardless of solution status/type.

## Streaming behavior

All iterators scan incrementally and reject unrelated message names before full tokenization. Tolerant mode skips malformed target records; `strict=True` raises `NovatelAsciiParseError` with source line number. CRC validation is explicit through `verify_crc=True`.
