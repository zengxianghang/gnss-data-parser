# MATLAB parsers

MATLAB is a first-class parser target alongside Python. The MATLAB implementation must keep field meanings, units and raw-time semantics aligned with `docs/parser_interface.md` and the Python implementation.

## Common layer

The shared NovAtel standard ASCII layer is under MATLAB package folders:

```matlab
msg = gnssparser.novatel.parseAsciiLine(line, 'PSRVELA', true);
name = gnssparser.novatel.peekMessageName(line);
crc = gnssparser.novatel.crc32(payload);
```

`parseAsciiLine` returns the complete standard header, untyped body fields and CRC. CRC verification is opt-in so multi-GB scans do not pay the cost unless requested.

## PSRVEL

Convenience collection:

```matlab
records = readNovatelPsrvel('receiver.log');
```

Streaming large files:

```matlab
scanNovatelPsrvel('receiver.log', @consume, 'Strict', false, 'VerifyCrc', false);
```

Each record exposes `week`, `sow`, `time_status`, `sol_status`, `vel_type`, `latency_s`, `age_s`, `hor_speed_mps`, `track_deg`, `vert_speed_mps`, `reserved`, `crc`, and the full `header` struct. Header time and latency are preserved separately; the reader does not silently shift the timestamp or filter non-computed solutions.

## Streaming large logs

`gnssparser.common.scanTargetLines` reads a text log line by line, cheaply rejects unrelated message types, and calls a parser/callback only for the exact requested message. It supports `Strict` and `VerifyCrc` name/value options.

## Tests

```matlab
addpath('matlab');
addpath('matlab/tests');
testNovatelAscii;
testPsrvel;
```

## Rules

- keep message-specific parsing separate from analysis/plotting;
- preserve source time tags and units; do not silently interpolate or shift epochs;
- do not silently filter records by status, CN0, lock time or fix validity;
- add regression tests or small sanitized validation samples for every parser;
- do not fork vendor-format rules silently from the Python implementation.
