#!/usr/bin/env python3
"""CLI entry point for the vault-native review-site compiler."""
from __future__ import annotations

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.vault_site.compiler import main


if __name__ == "__main__":
    raise SystemExit(main())
