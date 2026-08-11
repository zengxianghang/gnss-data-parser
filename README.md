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

Typical usage:

```python
from gnss_parser.novatel import iter_bestpos, iter_bestvel, iter_inspva, iter_psrvel, iter_range

for vel in iter_bestvel("receiver.log"):
    print(vel.week, vel.sow, vel.latency_s, vel.hor_speed_mps, vel.vert_speed_mps)
```

See [`docs/parser_interface.md`](docs/parser_interface.md) and [`docs/novatel.md`](docs/novatel.md).

## Message roadmap

NovAtel:

- [x] common standard ASCII header
- [x] PSRVEL
- [x] RANGE
- [x] INSPVA
- [x] BESTPOS
- [x] BESTVEL

u-blox / NMEA:

- [ ] RMC

Development remains pre-1.0 until the initial parser set is stable.
