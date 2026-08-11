# MATLAB parsers

MATLAB is a first-class parser target alongside Python. The MATLAB implementation must keep field meanings, units and raw-time semantics aligned with `docs/parser_interface.md` and the Python implementation.

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
scanNovatelRange('receiver.log', @consumeEpoch, 'Strict', false, 'VerifyCrc', false);
```

Each RANGE epoch contains `week`, `sow`, `time_status`, `observation_count`, `observations`, `crc`, and the complete header. Each observation exposes PRN, GLONASS frequency representation, pseudorange/std, ADR/std, Doppler, C/N0, lock time, and decoded `tracking` status.

`tracking.raw` preserves the original 32-bit channel status. The decoded struct matches Python semantics for tracking state, SV channel, phase/parity/code lock, correlator type, satellite system/name, grouping, signal type/name, primary L1, half-cycle, digital filter, PRN lockout, and forced assignment. No CN0/lock/status filtering is performed.

## Streaming large logs

`gnssparser.common.scanTargetLines` reads line by line and cheaply rejects unrelated message names before full parsing.

## Tests

```matlab
addpath('matlab');
addpath('matlab/tests');
testNovatelAscii;
testPsrvel;
testRange;
```

## Rules

- keep parsing separate from analysis/plotting;
- preserve source time tags and units;
- do not silently filter records or observations;
- keep MATLAB and Python field semantics aligned;
- add sanitized regression samples for every parser.
