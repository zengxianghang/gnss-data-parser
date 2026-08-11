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
| Single-message streaming API | ✅ | ✅ |
| Multi-message single-pass API | ✅ | ✅ |
| Real-log validation artifacts | ✅ | ✅ |

## Multi-message single-pass parsing

When one large mixed log contains several needed message types, prefer the mixed-log API so the source is scanned only once.

Python collection:

```python
from gnss_parser import read_gnss_log

result = read_gnss_log(
    "receiver.log",
    messages={"RANGE", "PSRVEL", "INSPVA"},
)
range_epochs = result["range"]
psrvel = result["psrvel"]
print(result.stats.total_lines, result.stats.records)
```

Python streaming:

```python
from gnss_parser import GnssLogStats, iter_gnss_log

stats = GnssLogStats()
for event in iter_gnss_log(
    "receiver.log",
    messages={"RANGE", "PSRVEL", "INSPVA"},
    stats=stats,
):
    consume(event.message_type, event.record)
```

`GnssLogEvent` also exposes `line_number` and `raw_line` for validation/debugging without rescanning the source.

MATLAB collection:

```matlab
[data, stats] = readGnssLog('receiver.log', ...
    'Messages', {'RANGE', 'PSRVEL', 'INSPVA'});
```

MATLAB streaming/callback processing:

```matlab
handlers = struct();
handlers.range = @consumeRange;
handlers.psrvel = @consumePsrvel;
stats = scanGnssLog('receiver.log', handlers);
```

Stable grouped keys are `psrvel`, `range`, `inspva`, `bestpos`, `bestvel`, and `rmc`. Configuration aliases such as `RANGE`/`RANGEA` are accepted; unsupported requested message names are rejected explicitly. NovAtel CRC and NMEA checksum verification remain opt-in.

The existing single-message APIs remain supported. They are convenient when only one type is needed; avoid calling several of them sequentially on the same multi-GB file when the mixed-log API can perform one scan instead.

## Validate against a real data file

Synthetic fixtures are necessary but not sufficient. For a real receiver log, run both implementations against the same file and compare their normalized validation artifacts.

Python:

```bash
python tools/validate_real_log.py D:\data\receiver.log --verify-crc --verify-checksum
```

MATLAB:

```matlab
addpath('matlab');
validateRealLog('D:\data\receiver.log', ...
    'VerifyCrc', true, 'VerifyChecksum', true);
```

Default output directories are `<stem>_validation_python` and `<stem>_validation_matlab`. Each contains `summary.json` plus one CSV per selected message type. The default CSV mode is deliberately sampled: first 5 records, every 1000th record, and last 5 records. Each sampled row contains the source line number and raw source sentence. For RANGE, every observation in a sampled epoch is flattened, including raw/decoded tracking status.

Compare the two outputs:

```bash
python tools/compare_validation_results.py ^
    D:\data\receiver_validation_python ^
    D:\data\receiver_validation_matlab ^
    --output D:\data\receiver_validation_compare.json
```

The comparator checks target/parsed/malformed counts, exact text/integer fields, source lines, and floating-point fields with a tolerance. Exit code 0 means PASS; a mismatch returns exit code 1 and reports the affected message/field.

For exhaustive normalized CSV output, add `--full-export` in Python or `'FullExport', true` in MATLAB. This is intentionally opt-in because flattened RANGE output can be substantially larger than the original log.

Recommended validation order:

1. run parser unit/regression tests;
2. run Python and MATLAB real-log validation on the same file;
3. compare the generated validation directories;
4. manually inspect sampled `raw_line` + parsed columns, especially RANGE, low-CN0/zero-lock records, invalid RMC fixes, malformed/partial records, and file beginning/end.

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
testGnssLog;
testValidateRealLog;
```

`tests/fixtures/cross_language/sample.log` and `expected.json` are the shared sanitized regression source. Python CI validates the manifest automatically. MATLAB `testCrossLanguageConsistency` consumes the same log and manifest, preventing the two language implementations from silently drifting in field meanings, units or time semantics. `testGnssLog` additionally checks that the single-pass mixed reader matches the existing individual MATLAB readers. `testValidateRealLog` exercises the real-log validation output schema on the same fixture.

The cross-language MATLAB regression and real-log JSON validation require `jsondecode`/`jsonencode` (MATLAB R2016b+); the parser functions themselves do not depend on JSON support.

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
