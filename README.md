# gnss-data-parser

Reusable parsers for fixed-format GNSS logs and the **single source of truth** for raw parsing shared by analysis projects and ChatGPT conversations.

## Core rules

- parsing only; analysis/plotting stays downstream
- streaming-first APIs for multi-GB logs
- stable semantic field names
- preserve source time tags and units
- no hidden status/quality filtering
- representative tests and PR-based changes

## Language support

| Message / capability | Python | MATLAB |
|---|---:|---:|
| NovAtel standard ASCII header | ✅ | ✅ |
| NovAtel CRC32 | ✅ | ✅ |
| PSRVELA | ✅ | ✅ |
| RANGEA + tracking status | ✅ | ✅ |
| INSPVAA | ✅ | ✅ |
| BESTPOSA | ✅ | ✅ |
| BESTVELA | ✅ | ✅ |
| NMEA/u-blox RMC | ✅ | ✅ |
| Streaming large-file API | ✅ | ✅ |

Python uses `iter_*` / `read_*`. MATLAB uses `scanNovatel*` / `readNovatel*` and `scanUbloxRmc` / `readUbloxRmc`.

## Tests

Python CI:

```bash
python -m unittest discover -s tests -v
```

MATLAB self-tests:

```matlab
addpath('matlab');
addpath('matlab/tests');
testNovatelAscii;
testPsrvel;
testRange;
testInspva;
testBestposBestvel;
testRmc;
testCrossLanguageConsistency;
```

`tests/fixtures/cross_language/sample.log` and `expected.json` are the shared sanitized regression source. Python CI validates the manifest automatically. MATLAB `testCrossLanguageConsistency` consumes the same log and manifest, preventing the two language implementations from silently drifting in field meanings, units or time semantics.

The cross-language MATLAB regression uses `jsondecode` (MATLAB R2016b+); the parser functions themselves do not depend on `jsondecode`.

## Supported semantics

### NovAtel

- standard `#...A` ASCII envelope with exact message-name matching
- optional CRC verification
- PSRVEL/BESTVEL preserve header time and latency separately
- RANGE preserves every syntactically valid observation and decoded/raw tracking status
- INSPVA preserves exact data-block applicability time plus header time
- BESTPOS preserves MSL height and undulation separately

### u-blox / NMEA

- direct `$xxRMC` sentences with alphanumeric talker IDs such as `GP` and `GN`
- optional XOR checksum verification
- signed decimal-degree coordinates plus source UTC/date semantics
- invalid (`V`) records are preserved
- parser does not infer UTC century or convert UTC to GPST

See [`docs/parser_interface.md`](docs/parser_interface.md), [`docs/novatel.md`](docs/novatel.md), [`docs/ublox.md`](docs/ublox.md), and [`matlab/README.md`](matlab/README.md).

Development remains pre-1.0 until the parser interfaces have been exercised against representative real logs.
