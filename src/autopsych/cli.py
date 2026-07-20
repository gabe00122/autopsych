from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import audit_run
from .status import build_execution_snapshot
from .synthetic import validate_cases, validate_gold_cases, write_cases


def main() -> None:
    parser = argparse.ArgumentParser(prog="autopsych")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate-synthetic")
    generate.add_argument("output", type=Path)

    validate = subparsers.add_parser("validate-synthetic")
    validate.add_argument("library", type=Path)

    validate_gold = subparsers.add_parser("validate-gold")
    validate_gold.add_argument("library", type=Path)

    audit = subparsers.add_parser("audit-run")
    audit.add_argument("manifest", type=Path)
    audit.add_argument("records", type=Path)

    status = subparsers.add_parser("status")
    status.add_argument("--root", type=Path, default=Path.cwd())

    args = parser.parse_args()
    if args.command == "generate-synthetic":
        write_cases(args.output)
        print(json.dumps({"written": str(args.output), "n": 500}, indent=2))
    elif args.command == "validate-synthetic":
        result = validate_cases(args.library)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["passes_98_percent"] and result["n"] == 500 else 1)
    elif args.command == "validate-gold":
        result = validate_gold_cases(args.library)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["passes_98_percent"] else 1)
    elif args.command == "audit-run":
        result = audit_run(args.manifest, args.records)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["passes_99_percent"] else 1)
    elif args.command == "status":
        print(json.dumps(build_execution_snapshot(args.root), indent=2))


if __name__ == "__main__":
    main()
