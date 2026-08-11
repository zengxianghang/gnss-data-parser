#!/usr/bin/env python3
"""Validate a real mixed GNSS log and write normalized validation artifacts."""
from __future__ import annotations

import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from gnss_parser.validation import validate_real_log


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="mixed GNSS text log")
    p.add_argument("--output", help="output directory; default <stem>_validation_python")
    p.add_argument("--messages", help="comma-separated subset, e.g. RANGE,PSRVEL,INSPVA")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--verify-crc", action="store_true")
    p.add_argument("--verify-checksum", action="store_true")
    p.add_argument("--sample-first", type=int, default=5)
    p.add_argument("--sample-last", type=int, default=5)
    p.add_argument("--sample-every", type=int, default=1000)
    p.add_argument("--full-export", action="store_true", help="export every normalized record; can be very large")
    args = p.parse_args()
    source = Path(args.input)
    output = Path(args.output) if args.output else source.with_name(source.stem + "_validation_python")
    messages = None if not args.messages else [x.strip() for x in args.messages.split(",") if x.strip()]
    summary = validate_real_log(source, output, messages=messages, strict=args.strict,
        verify_crc=args.verify_crc, verify_checksum=args.verify_checksum,
        sample_first=args.sample_first, sample_last=args.sample_last,
        sample_every=args.sample_every, full_export=args.full_export)
    print(f"validation output: {output}")
    print(f"total lines: {summary['stats']['total_lines']}")
    for key in summary["stats"]["selected_messages"]:
        m = summary["messages"][key]
        print(f"{key:8s} records={m['records']} malformed={m['malformed']} exported_rows={m['exported_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
