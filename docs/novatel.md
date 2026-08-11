# NovAtel parser notes

This document records the format assumptions used by `gnss_parser.novatel`.

## Authoritative references

- Standard OEM ASCII: <https://docs.novatel.com/OEM7/Content/Messages/ASCII.htm>
- PSRVEL: <https://docs.novatel.com/OEM7/Content/Logs/PSRVEL.htm>
- RANGE: <https://docs.novatel.com/OEM7/Content/Logs/RANGE.htm>
- INSPVA: <https://docs.novatel.com/OEM7/Content/SPAN_Logs/INSPVA.htm>
- BESTPOS: <https://docs.novatel.com/OEM7/Content/Logs/BESTPOS.htm>

The implementation targets standard `#...A` ASCII messages. CRC verification is opt-in for large-file scans.

## PSRVELA

Preserves source header time and latency separately; no hidden solution filtering.

## RANGEA

Returns immutable epochs/observations with raw and decoded channel tracking status; no hidden observation-quality filtering.

## INSPVAA

`InspvaRecord.week/sow` use the INS data-block applicability time. `header_week/header_sow` preserve the standard header time tag. Latitude/longitude, ellipsoidal height, N/E/U velocity, roll/pitch/azimuth and INS status are exposed without hidden status filtering.

## BESTPOSA

Public APIs:

```python
from gnss_parser.novatel import iter_bestpos, parse_bestpos_line, read_bestpos
```

`BestposRecord` exposes the complete standard header plus:

- solution status and position type
- latitude/longitude in degrees
- `msl_height_m` exactly as logged
- `undulation_m` exactly as logged
- datum
- latitude/longitude/height standard deviations in metres
- base-station ID
- differential age and solution age
- tracked, used, L1-used and multi-frequency-used satellite counts
- reserved byte, extended solution status, Galileo/BeiDou signal mask, GPS/GLONASS signal mask
- CRC

The parser deliberately does not convert MSL height plus undulation into an ellipsoidal height field. Downstream code that needs that derived quantity must calculate it explicitly.

A syntactically valid record is returned regardless of solution status/type; `SOL_COMPUTED` filtering belongs to analysis code.

## Streaming behavior

All iterators scan incrementally and reject unrelated message names before full tokenization. Tolerant mode skips malformed target records; `strict=True` raises `NovatelAsciiParseError` with source line number. CRC validation is explicit through `verify_crc=True`.
