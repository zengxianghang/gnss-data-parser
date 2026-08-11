# MATLAB parsers

MATLAB is a first-class parser target alongside Python. Field meanings, units and raw-time semantics must stay aligned with `docs/parser_interface.md` and the Python implementation.

## Supported NovAtel readers

```matlab
psrvel = readNovatelPsrvel('receiver.log');
range = readNovatelRange('receiver.log');
inspva = readNovatelInspva('receiver.log');
bestpos = readNovatelBestpos('receiver.log');
bestvel = readNovatelBestvel('receiver.log');
```

For multi-GB logs use the corresponding `scanNovatel*` callback APIs instead of collecting the whole file.

### Timing and filtering rules

- PSRVEL/BESTVEL keep header week/SOW and latency separate; latency is not silently subtracted.
- INSPVA `week`/`sow` are the data-block applicability time; header time remains in `header_week`/`header_sow`.
- BESTPOS preserves MSL height and undulation separately; no implicit ellipsoidal-height conversion is performed.
- RANGE preserves all observations and raw/decoded channel tracking status.
- No parser silently filters solution status, INS status, CN0, lock time or fix validity.

### BESTPOS fields

The MATLAB record mirrors Python fields for solution/position type, latitude/longitude, `msl_height_m`, `undulation_m`, datum, position standard deviations, station ID, ages, tracked/used satellite counts, reserved/extended status and signal masks.

### BESTVEL fields

The MATLAB record mirrors Python fields for solution/velocity type, `latency_s`, `age_s`, horizontal speed, track angle, vertical speed and reserved field.

## Common layer and streaming

`gnssparser.novatel.parseAsciiLine`, `peekMessageName`, `crc32`, and `gnssparser.common.scanTargetLines` provide the shared low-level implementation. CRC verification is opt-in.

## Tests

```matlab
addpath('matlab');
addpath('matlab/tests');
testNovatelAscii;
testPsrvel;
testRange;
testInspva;
testBestposBestvel;
```

## Rules

- keep parsing separate from analysis/plotting;
- preserve source time tags and units;
- do not silently filter records or observations;
- keep MATLAB and Python field semantics aligned;
- add sanitized regression samples for every parser.
