# MATLAB parsers

MATLAB is a first-class parser target alongside Python. Field meanings, units and raw-time semantics must stay aligned with `docs/parser_interface.md` and the Python implementation.

## Supported readers

```matlab
psrvel = readNovatelPsrvel('receiver.log');
range = readNovatelRange('receiver.log');
inspva = readNovatelInspva('receiver.log');
bestpos = readNovatelBestpos('receiver.log');
bestvel = readNovatelBestvel('receiver.log');
rmc = readUbloxRmc('receiver.log');
```

For multi-GB logs use the corresponding `scanNovatel*` or `scanUbloxRmc` callback APIs instead of collecting the whole file.

## Timing and filtering rules

- PSRVEL/BESTVEL keep header week/SOW and latency separate; latency is not silently subtracted.
- INSPVA `week`/`sow` are the data-block applicability time; header time remains in `header_week`/`header_sow`.
- BESTPOS preserves MSL height and undulation separately; no implicit ellipsoidal-height conversion is performed.
- RANGE preserves all observations and raw/decoded channel tracking status.
- RMC preserves UTC text and `ddmmyy` date; it does not infer a century or convert UTC to GPST.
- RMC invalid (`V`) records and empty fix fields are preserved. Missing numeric RMC values are represented by `NaN` in MATLAB.
- No parser silently filters solution status, INS status, CN0, lock time or fix validity.

## RMC

`readUbloxRmc` and `scanUbloxRmc` accept standard `$xxRMC` talker IDs such as `GP` and `GN`. The record exposes talker ID, UTC text/seconds-of-day, validity status, decimal-degree latitude/longitude, speed in knots, course, date, magnetic variation, position mode, navigation status and checksum. NMEA XOR checksum verification is opt-in through `VerifyChecksum`.

## Common layer and streaming

`gnssparser.novatel.parseAsciiLine`, `peekMessageName`, `crc32`, and `gnssparser.common.scanTargetLines` provide the NovAtel low-level implementation. `gnssparser.nmea.checksum`, `peekRmc`, and `parseRmcLine` provide the NMEA layer.

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
```

## Rules

- keep parsing separate from analysis/plotting;
- preserve source time tags and units;
- do not silently filter records or observations;
- keep MATLAB and Python field semantics aligned;
- add sanitized regression samples for every parser.
