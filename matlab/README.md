# MATLAB parsers

MATLAB is a first-class parser target alongside Python. Field meanings, units and raw-time semantics must stay aligned with `docs/parser_interface.md` and the Python implementation.

## Recommended mixed-log API

When one file contains several needed message types, use the single-pass API instead of calling multiple single-message readers sequentially.

Collection API:

```matlab
[data, stats] = readGnssLog('receiver.log', ...
    'Messages', {'RANGE', 'PSRVEL', 'INSPVA'});
```

`data` always has stable fields `psrvel`, `range`, `inspva`, `bestpos`, `bestvel`, and `rmc`. Unselected fields are empty. `stats` reports total/unrelated lines plus target, parsed, and malformed counts.

For multi-GB logs, prefer callback streaming:

```matlab
handlers = struct();
handlers.range = @consumeRange;
handlers.psrvel = @consumePsrvel;
stats = scanGnssLog('receiver.log', handlers);
```

Options shared by the mixed API:

- `'Messages'`: canonical keys or aliases such as `RANGE`, `RANGEA`, `PSRVEL`, `INSPVA`, `BESTPOS`, `BESTVEL`, `RMC`
- `'Strict'`: raise on malformed selected records instead of counting/skipping them
- `'VerifyCrc'`: opt-in NovAtel CRC32 verification
- `'VerifyChecksum'`: opt-in NMEA checksum verification
- `'PassSourceInfo'`: default false; when true, callback receives `(record, source)` where `source.line_number` and `source.raw_line` support validation/debugging without a second scan

Unknown requested message names are rejected explicitly.

## Real-log validation

Use `validateRealLog` to validate the MATLAB parser on an actual receiver log and generate artifacts compatible with the Python validator.

```matlab
addpath('matlab');
summary = validateRealLog('D:\data\receiver.log', ...
    'VerifyCrc', true, ...
    'VerifyChecksum', true);
```

Default output is `receiver_validation_matlab` beside the input file. It contains:

```text
summary.json
psrvel.csv
range.csv
inspva.csv
bestpos.csv
bestvel.csv
rmc.csv
```

By default the CSV files are deterministic samples: first 5 records, every 1000th record, and last 5 records. Every sampled row includes the original source line number and raw sentence. RANGE expands every observation from each sampled RANGE epoch and includes raw/decoded tracking status.

Useful options:

```matlab
validateRealLog(file, 'Messages', {'RANGE','PSRVEL'});
validateRealLog(file, 'SampleFirst', 10, 'SampleLast', 10, 'SampleEvery', 500);
validateRealLog(file, 'FullExport', true);  % may be very large
```

Run the Python validator on the same source file, then compare both output directories with `tools/compare_validation_results.py`. Exact strings/integers and raw source lines must match; floating-point columns are compared with tolerance.

The validation JSON tools require `jsonencode`/`jsondecode` (MATLAB R2016b+). Normal parser APIs do not require JSON support.

## Supported single-message readers

```matlab
psrvel = readNovatelPsrvel('receiver.log');
range = readNovatelRange('receiver.log');
inspva = readNovatelInspva('receiver.log');
bestpos = readNovatelBestpos('receiver.log');
bestvel = readNovatelBestvel('receiver.log');
rmc = readUbloxRmc('receiver.log');
```

These remain useful when only one message type is needed. For large mixed logs requiring several types, prefer `readGnssLog`/`scanGnssLog` so the file is not rescanned once per type.

## Timing and filtering rules

- PSRVEL/BESTVEL keep header week/SOW and latency separate; latency is not silently subtracted.
- INSPVA `week`/`sow` are the data-block applicability time; header time remains in `header_week`/`header_sow`.
- BESTPOS preserves MSL height and undulation separately; no implicit ellipsoidal-height conversion is performed.
- RANGE preserves all observations and raw/decoded channel tracking status.
- RMC preserves UTC text and `ddmmyy` date; it does not infer a century or convert UTC to GPST.
- RMC invalid (`V`) records and empty fix fields are preserved. Missing numeric RMC values are represented by `NaN` in MATLAB.
- No parser silently filters solution status, INS status, CN0, lock time or fix validity.

## Common layer and streaming

`gnssparser.novatel.parseAsciiLine`, `peekMessageName`, `crc32`, and `gnssparser.common.scanTargetLines` provide the NovAtel low-level implementation. `gnssparser.nmea.checksum`, `peekRmc`, and `parseRmcLine` provide the NMEA layer. `gnssparser.common.identifyGnssLine` and `normalizeMessageSelection` provide cheap mixed-log routing/configuration.

## Tests

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

`testCrossLanguageConsistency` reads the shared sanitized fixture/manifest. `testGnssLog` verifies mixed single-pass collection against individual readers. `testValidateRealLog` verifies validation output generation, source-line preservation, RANGE flattening, and summary JSON.

## Rules

- keep parsing separate from analysis/plotting;
- preserve source time tags and units;
- do not silently filter records or observations;
- keep MATLAB and Python field semantics aligned;
- add sanitized regression samples for every parser.
