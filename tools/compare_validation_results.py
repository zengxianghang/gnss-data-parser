#!/usr/bin/env python3
"""Compare Python and MATLAB real-log validation directories."""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from gnss_parser.validation_compare import compare_validation_outputs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("python_dir")
    p.add_argument("matlab_dir")
    p.add_argument("--rtol", type=float, default=1e-9)
    p.add_argument("--atol", type=float, default=1e-12)
    p.add_argument("--output", help="optional JSON report path")
    args = p.parse_args()
    report = compare_validation_outputs(args.python_dir, args.matlab_dir, rtol=args.rtol, atol=args.atol)
    print(f"OVERALL: {report['status']}")
    for key, item in report["messages"].items():
        print(f"{key:8s} {item['status']}")
        for issue in item["issues"][:5]: print(f"  - {issue}")
    if args.output:
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
