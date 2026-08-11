# gnss-data-parser

Reusable parsers for fixed-format GNSS logs and the **single source of truth** for raw parsing shared by analysis projects and ChatGPT conversations.

## Core rules

- parsing only; analysis/plotting stays downstream
- streaming-first `iter_*` APIs for multi-GB logs
- stable semantic field names
- preserve source time tags and units
- no hidden status/quality filtering
- representative tests and PR-based changes

## Test

```bash
python -m unittest discover -s tests -v
```

## Supported NovAtel OEM ASCII parsers

- common standard ASCII header/envelope and optional CRC32 verification
- `PSRVELA`
- `RANGEA` with decoded channel tracking status
- `INSPVAA` with exact data-block applicability time plus preserved header time
- `BESTPOSA` with position/std/satellite-count/status-mask fields
- `BESTVELA` with preserved latency and source header time

## Supported u-blox / NMEA parsers

- RMC (`$xxRMC`) with `GP`/`GN` and other alphanumeric talker IDs
- optional NMEA XOR checksum verification
- signed decimal-degree coordinates plus preserved UTC/date semantics
- invalid (`V`) records are preserved rather than hidden

Example:

```python
from gnss_parser.ublox import iter_rmc

for rmc in iter_rmc("ublox.log"):
    print(rmc.utc_time, rmc.status, rmc.latitude_deg, rmc.longitude_deg, rmc.speed_knots)
```

See [`docs/parser_interface.md`](docs/parser_interface.md), [`docs/novatel.md`](docs/novatel.md), and [`docs/ublox.md`](docs/ublox.md).

## Initial message roadmap

NovAtel:

- [x] common standard ASCII header
- [x] PSRVEL
- [x] RANGE
- [x] INSPVA
- [x] BESTPOS
- [x] BESTVEL

u-blox / NMEA:

- [x] RMC

Development remains pre-1.0 until the parser interfaces have been exercised against representative real logs.
