#!/usr/bin/env python3
"""Validate a generated vault-native publication package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.vault_site.compiler import validate_package


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a vault-native publication package")
    parser.add_argument("--vault", type=Path, default=Path("vault"))
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = validate_package(args.vault, args.output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result.report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result.report["status"], "counts": result.report["counts"], "output": str(args.output)}, ensure_ascii=False))
    for error in result.errors[:20]:
        print(f"ERROR {error.get('code')}: {error.get('sourcePath')} {error.get('message')}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
