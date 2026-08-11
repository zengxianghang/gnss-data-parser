# NovAtel parser notes

This document records the format assumptions used by `gnss_parser.novatel`.

## Authoritative references

- Standard OEM ASCII message format: <https://docs.novatel.com/OEM7/Content/Messages/ASCII.htm>
- PSRVEL: <https://docs.novatel.com/OEM7/Content/Logs/PSRVEL.htm>
- RANGE: <https://docs.novatel.com/OEM7/Content/Logs/RANGE.htm>
- INSPVA: <https://docs.novatel.com/OEM7/Content/SPAN_Logs/INSPVA.htm>

The implementation targets the standard `#...A` ASCII format, not abbreviated ASCII and not binary messages.

## Standard ASCII header and CRC

`parse_ascii_line()` decodes the standard header into `NovatelAsciiHeader`. The header/data `;` delimiter and trailing `*xxxxxxxx` CRC field are required. Message matching is exact. `novatel_crc32()` implements the NovAtel CRC; verification remains opt-in for large-file scans.

## PSRVELA

`PsrvelRecord` exposes solution status/type, latency, differential age, horizontal speed, track over ground, vertical speed, reserved field, CRC and the complete standard header. Source header week/SOW is preserved and latency is not silently applied.

## RANGEA

Each `RangeRecord` represents one RANGE epoch and contains immutable `RangeObservation` objects. Each observation exposes PRN, GLONASS frequency representation, pseudorange/std, ADR/std, Doppler, C/N0, lock time and decoded channel tracking status. The raw 32-bit tracking word is also preserved. No observation-quality filtering is applied.

## INSPVAA

Public APIs:

```python
from gnss_parser.novatel import iter_inspva, parse_inspva_line, read_inspva
```

`InspvaRecord` exposes:

- `header` — complete standard ASCII header
- `week`, `sow` — GNSS week/SOW from the INSPVA data block
- `header_week`, `header_sow` — header time tag
- latitude/longitude in degrees
- ellipsoidal height in metres
- north/east/up velocity in m/s
- roll, pitch and azimuth in degrees
- `ins_status`
- CRC

SPAN logs carry an INS time tag in the data block in addition to the log header. The data-block time is the exact time of applicability, so `InspvaRecord.week/sow` use that time while the header time remains separately accessible. No attempt is made to force the two time tags to match.

No INS-status filtering is applied. Records such as alignment/inactive states remain available if syntactically valid.

## Streaming behavior

All message iterators scan incrementally and reject unrelated message names before full tokenization. Default tolerant mode skips malformed target-message records. `strict=True` raises `NovatelAsciiParseError` with the 1-based source line number. CRC validation is explicit through `verify_crc=True`.
