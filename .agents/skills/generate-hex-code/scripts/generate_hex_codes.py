#!/usr/bin/env python3
"""Generate cryptographically random 8-hex-char codes for this codebase's
short-code conventions: log/diagnostic message codes (the first argument to
``App.create_log_message``, ``App.create_static_log_message``, and exception
constructors like ``exc.NoResultsError``/``exc.ServiceException``), and the
``gen_epix.etl.model.Result`` subclass registry (``ID``/``COMPLETED_CODE``
ClassVars).

Scans the repository for every existing quoted 8-hex-char string literal
(all of the above share the same ``"[0-9a-f]{8}"`` shape, so one scan covers
them all) so a freshly generated code is guaranteed not to collide with one
already in use, then prints the requested number of fresh codes.

Usage:
    python generate_hex_codes.py [--count N] [--root PATH]
"""

from __future__ import annotations

import argparse
import re
import secrets
from pathlib import Path

HEX_LITERAL_RE = re.compile(r'"([0-9a-f]{8})"')


def find_existing_codes(root: Path) -> set[str]:
    existing: set[str] = set()
    for path in root.rglob("*.py"):
        if any(part in {".venv", "venv", "node_modules", ".git"} for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        existing.update(HEX_LITERAL_RE.findall(text))
    return existing


def generate_codes(count: int, existing: set[str]) -> list[str]:
    codes: list[str] = []
    while len(codes) < count:
        candidate = secrets.token_hex(4)
        if candidate in existing or candidate in codes:
            continue
        codes.append(candidate)
    return codes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=5, help="Number of codes to generate (default: 5)")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="Repository root to scan for existing codes (default: repo root inferred from this script's location)",
    )
    args = parser.parse_args()

    existing = find_existing_codes(args.root)
    for code in generate_codes(args.count, existing):
        print(code)


if __name__ == "__main__":
    main()
