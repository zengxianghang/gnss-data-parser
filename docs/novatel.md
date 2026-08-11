# NovAtel parser notes

This document records the format assumptions used by `gnss_parser.novatel`.

## Authoritative references

- Standard OEM ASCII message format: <https://docs.novatel.com/OEM7/Content/Messages/ASCII.htm>
- PSRVEL: <https://docs.novatel.com/OEM7/Content/Logs/PSRVEL.htm>
- RANGE: <https://docs.novatel.com/OEM7/Content/Logs/RANGE.htm>

The implementation targets the standard `#...A` ASCII format, not abbreviated ASCII and not binary messages.

## Standard ASCII header

`parse_ascii_line()` decodes the standard header into `NovatelAsciiHeader`:

- `message`
- `port`
- `sequence`
- `idle_time_pct`
- `time_status`
- `week`
- `sow`
- `receiver_status`
- `reserved`
- `software_version`

The header/data `;` delimiter and trailing `*xxxxxxxx` CRC field are required. Message matching is exact.

### CRC

`novatel_crc32()` implements the NovAtel 32-bit CRC algorithm. Message parsers expose `verify_crc=False` by default so multi-GB processing does not pay the CRC cost unless the caller requests it.

## PSRVELA

Public APIs:

```python
from gnss_parser.novatel import iter_psrvel, parse_psrvel_line, read_psrvel
```

`PsrvelRecord` exposes solution status/type, latency, differential age, horizontal speed, track over ground, vertical speed, reserved field, CRC and the complete standard header.

The source `week` and `sow` are preserved. NovAtel defines the PSRVEL time of validity as the header time tag minus the latency field; the parser deliberately does not modify the source timestamp automatically.

No solution-quality filter is applied.

## RANGEA

Public APIs:

```python
from gnss_parser.novatel import iter_range, parse_range_line, read_range
```

Each `RangeRecord` represents one RANGE epoch and contains a tuple of `RangeObservation` objects. The parser verifies that the declared observation count matches the exact number of observation fields.

Each observation exposes:

- `prn`
- `glofreq` — NovAtel GLONASS frequency representation (`frequency + 7`)
- `pseudorange_m`, `pseudorange_std_m`
- `adr_cycles`, `adr_std_cycles`
- `doppler_hz`
- `cn0_dbhz`
- `lock_time_s`
- `tracking` — decoded `TrackingStatus`

`TrackingStatus.raw` preserves the original 32-bit `ch-tr-status`. The decoded object also exposes tracking state, SV channel, phase/parity/code lock flags, correlator type, satellite system, signal type, grouping, primary-L1, half-cycle-added, digital-filter, PRN-lock and forced-assignment flags.

`signal_name` is a convenience label derived from the OEM7 RANGE tracking-status table. The numeric `satellite_system` and `signal_type` remain the stable source values and must be preferred if future firmware introduces a signal code not yet named by this library.

No quality filtering is applied: low CN0, zero lock time, unknown parity, non-locked tracking states and any constellation/signal are returned if the sentence is syntactically valid.

## Streaming behavior

All message iterators scan incrementally and reject unrelated message names before full tokenization. Default tolerant mode skips malformed target-message records. `strict=True` raises `NovatelAsciiParseError` with the 1-based source line number. CRC validation is explicit through `verify_crc=True`.
