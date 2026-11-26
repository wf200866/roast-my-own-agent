#!/usr/bin/env python3
"""Emit the one-line roast that make.fun grades from /output/entry.txt.

The gate is small but exact: UTF-8 text, a single line, 1-200 characters,
and not only white space.  We check all of that here, before writing, so a
bad edit fails loudly in this program instead of silently at grading time.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROAST = "My agent backs up its memory every five minutes, then forgets where the backup is."

MIN_CHARS = 1
MAX_CHARS = 200
DEFAULT_OUTPUT = Path("/output/entry.txt")

# Characters a reader (or a judge) can treat as ending a line.  \n and \r are
# the obvious ones; the rest are the Unicode line and paragraph separators.
LINE_BREAKS = ("\n", "\r", "\v", "\f", "\u0085", "\u2028", "\u2029")


class GateError(ValueError):
    """The text would fail make.fun's entry gate."""


def check_line(text: str) -> str:
    """Return *text* unchanged when it passes the gate; raise GateError otherwise."""
    if any(ch in text for ch in LINE_BREAKS):
        raise GateError("the entry must be a single line")
    if not text.strip():
        raise GateError("the entry must not be blank")
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        raise GateError(
            f"the entry must be {MIN_CHARS}-{MAX_CHARS} characters, got {len(text)}"
        )
    return text


def write_atomic(text: str, destination: Path) -> Path:
    """Write *text* as UTF-8, mode 0644, no trailing newline, atomically."""
    payload = text.encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, staged = tempfile.mkstemp(prefix=".entry-", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(staged, 0o644)
        os.replace(staged, destination)
    except BaseException:
        Path(staged).unlink(missing_ok=True)
        raise
    return destination


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write the make.fun roast entry.")
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="destination file (default: /output/entry.txt)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the entry without writing anything",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print a one-object JSON report instead of the line",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        entry = check_line(ROAST)
        if args.check:
            report = {"valid": True, "chars": len(entry), "bytes": len(entry.encode("utf-8"))}
            print(json.dumps(report) if args.json else entry)
            return 0

        path = write_atomic(entry, args.out)
        if path.read_bytes() != entry.encode("utf-8"):
            raise GateError(f"{path} does not hold the entry after writing")
    except (GateError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = {
        "path": str(path),
        "valid": True,
        "chars": len(entry),
        "bytes": len(entry.encode("utf-8")),
    }
    print(json.dumps(report) if args.json else entry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
