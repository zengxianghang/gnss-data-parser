# MATLAB parsers

MATLAB is a first-class parser target alongside Python. Field meanings, units and raw-time semantics must stay aligned with `docs/parser_interface.md` and the Python implementation.

## Recommended mixed-log API

When one file contains several needed message types, use the single-pass API instead of calling multiple single-message readers sequentially.

Collection API:

```matlab
[data, stats] = readGnssLog('receiver.log', ...
    'Messages', {'RANGE', 'PSRVEL', 'INSPVA'});
```

`data` always has stable fields:

```matlab
data.psrvel
data.range
data.inspva
data.bestpos
data.bestvel
data.rmc
```

Unselected message fields are empty. `stats` reports total/unrelated lines plus target, parsed, and malformed counts for every supported type.

For multi-GB logs, prefer callback streaming so parsed records are not retained:

```matlab
handlers = struct();
handlers.range = @consumeRange;
handlers.psrvel = @consumePsrvel;
stats = scanGnssLog('receiver.log', handlers);
```

`scanGnssLog` reads the source once, cheaply identifies the message type, and invokes only the corresponding existing parser. If the `Messages` option is omitted, nonempty handler fields determine the selected types; with no handlers, all supported types are selected.

Options shared by the mixed API:

- `'Messages'`: canonical keys or aliases such as `RANGE`, `RANGEA`, `PSRVEL`, `INSPVA`, `BESTPOS`, `BESTVEL`, `RMC`
- `'Strict'`: raise on malformed selected records instead of counting/skipping them
- `'VerifyCrc'`: opt-in NovAtel CRC32 verification
- `'VerifyChecksum'`: opt-in NMEA checksum verification

Unknown requested message names are rejected explicitly.

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
```

`testCrossLanguageConsistency` reads the same sanitized `tests/fixtures/cross_language/sample.log` and `expected.json` that Python CI uses. This regression test requires `jsondecode` (MATLAB R2016b+); normal parser functions do not. `testGnssLog` verifies that mixed single-pass collection is equivalent to the existing individual readers and exercises subset/callback behavior.

## Rules

- keep parsing separate from analysis/plotting;
- preserve source time tags and units;
- do not silently filter records or observations;
- keep MATLAB and Python field semantics aligned;
- add sanitized regression samples for every parser.
