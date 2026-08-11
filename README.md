# gnss-data-parser

Reusable parsers for fixed-format GNSS logs.

The repository is intended to be the **single source of truth** for raw GNSS log parsing shared by different analysis projects and ChatGPT conversations. Analysis code should consume structured parser output instead of re-implementing message parsing.

## Design principles

1. **Parsing only** — convert raw logs into structured records; do not put project-specific accuracy analysis or plotting here.
2. **Streaming first** — parsers should provide `iter_*` APIs so multi-GB logs can be processed without loading the whole file into memory.
3. **Convenience second** — `read_*` helpers may collect iterator output for small files and interactive work.
4. **Stable field names** — downstream analysis should depend on normalized field names, not vendor-specific column positions.
5. **Preserve raw timing** — keep GNSS week and seconds-of-week when available; do not silently round or interpolate epochs.
6. **No hidden filtering** — parser-specific status filtering must be explicit and documented.
7. **Test with representative lines** — every supported message type should have valid, malformed, boundary and regression cases.
8. **PR workflow** — changes are developed on branches and merged through pull requests; `main` is the approved parser baseline.

## Planned layout

```text
gnss-data-parser/
├─ python/
│  └─ gnss_parser/
│     ├─ common/
│     ├─ novatel/
│     └─ ublox/
├─ matlab/
├─ cpp/
├─ docs/
└─ tests/
```

The first implementation focuses on the Python package and shared interface conventions. MATLAB/C++ implementations can be added while keeping equivalent output semantics.

## Python package

The package currently has no third-party runtime dependency.

From the repository root:

```bash
python -m unittest discover -s tests -v
```

For local imports without installing the package, add `python/` to `PYTHONPATH`. Packaging metadata is provided in `pyproject.toml` for editable installation when desired.

## Parser API convention

Message-specific modules should expose two levels of API:

```python
from gnss_parser.novatel import iter_psrvel, read_psrvel

for record in iter_psrvel("receiver.log"):
    process(record)

records = read_psrvel("small_receiver.log")
```

`iter_*` is the primary API for large files. `read_*` is a convenience wrapper that returns all records.

See [`docs/parser_interface.md`](docs/parser_interface.md) for the detailed contract.

## Initial message roadmap

NovAtel:

- RANGE
- PSRVEL
- INSPVA
- BESTPOS
- BESTVEL

u-blox / NMEA:

- RMC

Additional formats should be added only with format documentation and tests.

## Versioning

Until the first stable parser set is available, development is pre-1.0. Breaking parser-interface changes should be called out explicitly in pull requests.
