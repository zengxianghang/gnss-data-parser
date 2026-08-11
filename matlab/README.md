# MATLAB parsers

MATLAB implementations can be added here when a downstream MATLAB workflow cannot conveniently consume the Python parser output.

Requirements:

- keep field meanings and units aligned with `docs/parser_interface.md`;
- keep message-specific parsing separate from analysis/plotting;
- add regression tests or small validation samples for every parser;
- do not fork vendor-format rules silently from the Python implementation.
