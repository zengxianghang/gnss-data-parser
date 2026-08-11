# MATLAB parsers

MATLAB is a first-class parser target alongside Python. The MATLAB implementation must keep field meanings, units and raw-time semantics aligned with `docs/parser_interface.md` and the Python implementation.

## Common layer

The shared NovAtel standard ASCII layer is under MATLAB package folders:

```matlab
msg = gnssparser.novatel.parseAsciiLine(line, 'PSRVELA', true);
name = gnssparser.novatel.peekMessageName(line);
crc = gnssparser.novatel.crc32(payload);
```

`parseAsciiLine` returns a struct containing:

- `header.message`
- `header.port`
- `header.sequence`
- `header.idle_time_pct`
- `header.time_status`
- `header.week`
- `header.sow`
- `header.receiver_status`
- `header.reserved`
- `header.software_version`
- `fields`
- `crc`

CRC verification is opt-in so multi-GB scans do not pay the cost unless requested.

## Streaming large logs

`gnssparser.common.scanTargetLines` reads a text log line by line, cheaply rejects unrelated message types, and calls a parser/callback only for the exact requested message. It supports `Strict` and `VerifyCrc` name/value options.

Message-specific `read*` convenience functions will collect records for smaller files, while their callback/scan counterparts remain the preferred path for large logs.

## Tests

Add the `matlab` directory to the MATLAB path, then run:

```matlab
addpath('matlab');
addpath('matlab/tests');
testNovatelAscii;
```

## Rules

- keep message-specific parsing separate from analysis/plotting;
- preserve source time tags and units; do not silently interpolate or shift epochs;
- do not silently filter records by status, CN0, lock time or fix validity;
- add regression tests or small sanitized validation samples for every parser;
- do not fork vendor-format rules silently from the Python implementation.
