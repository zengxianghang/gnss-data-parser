# NovAtel parser notes

This document records the format assumptions used by `gnss_parser.novatel`.

## Authoritative references

- Standard OEM ASCII message format: <https://docs.novatel.com/OEM7/Content/Messages/ASCII.htm>
- PSRVEL: <https://docs.novatel.com/OEM7/Content/Logs/PSRVEL.htm>

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

The header/data `;` delimiter and trailing `*xxxxxxxx` CRC field are required.
Message matching is exact. For example, a PSRVEL parser accepts `PSRVELA`; it does not treat `PSRVEL2A` or another name containing `PSRVEL` as the same message.

### CRC

`novatel_crc32()` implements the NovAtel 32-bit CRC algorithm. Message parsers expose `verify_crc=False` by default so multi-GB processing does not pay the CRC cost unless the caller requests it.

With `verify_crc=True`, a mismatch raises `NovatelAsciiParseError` in direct parsing. In a streaming parser, tolerant/strict behavior then follows the parser's `strict` option.

## PSRVELA

Public APIs:

```python
from gnss_parser.novatel import iter_psrvel, parse_psrvel_line, read_psrvel
```

`PsrvelRecord` exposes:

- `header` — complete `NovatelAsciiHeader`
- `sol_status`
- `vel_type`
- `latency_s`
- `age_s`
- `hor_speed_mps`
- `track_deg` — direction of motion over ground relative to True North
- `vert_speed_mps` — positive upward
- `reserved`
- `crc`
- convenience properties `week`, `sow`, and `time_status`

The source `week` and `sow` are preserved. NovAtel defines the PSRVEL time of validity as the header time tag minus the latency field; the parser deliberately does not modify the source timestamp automatically.

No solution-quality filter is applied. A syntactically valid record with `sol_status != SOL_COMPUTED` is still returned.

### Streaming behavior

```python
for record in iter_psrvel("receiver.log"):
    process(record)
```

The iterator scans the file incrementally and cheaply rejects unrelated message names before full tokenization.

Default tolerant mode skips malformed `PSRVELA` records:

```python
for record in iter_psrvel("receiver.log", strict=False):
    process(record)
```

Strict mode raises `NovatelAsciiParseError` and includes the 1-based source line number:

```python
for record in iter_psrvel("receiver.log", strict=True):
    process(record)
```

CRC validation is explicit:

```python
records = read_psrvel("receiver.log", verify_crc=True)
```
