# gnss-data-parser

Reusable parsers for fixed-format GNSS logs.

The repository is intended to be the **single source of truth** for raw GNSS log parsing shared by different analysis projects and ChatGPT conversations. Analysis code should consume structured parser output instead of re-implementing message parsing.

## Design principles

1. **Parsing only** — convert raw logs into structured records; do not put project-specific accuracy analysis or plotting here.
2. **Streaming first** — parsers provide `iter_*` APIs so multi-GB logs can be processed without loading the whole file.
3. **Convenience second** — `read_*` helpers may collect iterator output for small files.
4. **Stable field names** — downstream analysis depends on normalized semantics, not vendor column positions.
5. **Preserve raw timing** — do not silently round, interpolate or replace source time tags.
6. **No hidden filtering** — quality/status filtering belongs to callers.
7. **Test representative cases** — valid, malformed, boundary and regression samples.
8. **PR workflow** — `main` is the approved parser baseline.

## Python package

No third-party runtime dependency is required.

```bash
python -m unittest discover -s tests -v
```

## Supported parsers

### NovAtel OEM ASCII

- shared standard ASCII header/envelope parser
- exact message-name matching
- optional NovAtel CRC32 verification
- `PSRVELA`
- `RANGEA`, including decoded channel tracking status
- `INSPVAA`, preserving both header time and exact INS data-block applicability time

Typical large-file usage:

```python
from gnss_parser.novatel import iter_inspva, iter_psrvel, iter_range

for record in iter_inspva("receiver.log"):
    print(record.week, record.sow, record.vel_n_mps, record.vel_e_mps, record.vel_u_mps)
```

See [`docs/parser_interface.md`](docs/parser_interface.md) and [`docs/novatel.md`](docs/novatel.md).

## Message roadmap

NovAtel:

- [x] common standard ASCII header
- [x] PSRVEL
- [x] RANGE
- [x] INSPVA
- [ ] BESTPOS
- [ ] BESTVEL

u-blox / NMEA:

- [ ] RMC

## Versioning

Development remains pre-1.0 until the initial parser set is stable.
