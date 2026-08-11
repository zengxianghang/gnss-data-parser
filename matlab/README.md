# MATLAB parsers

MATLAB is a first-class parser target alongside Python. Field meanings, units and raw-time semantics must stay aligned with `docs/parser_interface.md` and the Python implementation.

## Common layer

```matlab
msg = gnssparser.novatel.parseAsciiLine(line, 'PSRVELA', true);
name = gnssparser.novatel.peekMessageName(line);
crc = gnssparser.novatel.crc32(payload);
```

CRC verification is opt-in for large-log performance.

## PSRVEL

```matlab
records = readNovatelPsrvel('receiver.log');
scanNovatelPsrvel('receiver.log', @consume, 'Strict', false, 'VerifyCrc', false);
```

Header week/SOW and latency remain separate; no hidden solution filtering is applied.

## RANGE

```matlab
epochs = readNovatelRange('receiver.log');
scanNovatelRange('receiver.log', @consumeEpoch);
```

Each epoch contains raw observations and fully decoded tracking status with no hidden observation-quality filtering.

## INSPVA

```matlab
records = readNovatelInspva('receiver.log');
scanNovatelInspva('receiver.log', @consumeIns);
```

`week` and `sow` are the INSPVA data-block applicability time. `header_week` and `header_sow` preserve the standard ASCII header time separately. Records expose latitude/longitude, ellipsoidal height, north/east/up velocity, roll/pitch/azimuth, INS status, CRC and full header. INS status is never silently filtered.

## Streaming large logs

`gnssparser.common.scanTargetLines` reads line by line and cheaply rejects unrelated message names before full parsing.

## Tests

```matlab
addpath('matlab');
addpath('matlab/tests');
testNovatelAscii;
testPsrvel;
testRange;
testInspva;
```

## Rules

- keep parsing separate from analysis/plotting;
- preserve source time tags and units;
- do not silently filter records or observations;
- keep MATLAB and Python field semantics aligned;
- add sanitized regression samples for every parser.
