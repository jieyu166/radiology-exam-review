#!/usr/bin/env python3
"""Copy static review-site sources into an already compiled publication root."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def build_static_site(repo_root: Path, output_root: Path) -> None:
    repo_root = Path(repo_root).resolve()
    output_root = Path(output_root).resolve()
    if output_root == repo_root:
        raise ValueError("static output must not be inside the repository source root")
    output_root.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "css", "js"):
        source = repo_root / name
        target = output_root / name
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        else:
            raise FileNotFoundError(source)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build static site files into a publication artifact")
    parser.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args()
    build_static_site(Path(__file__).resolve().parent.parent, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
