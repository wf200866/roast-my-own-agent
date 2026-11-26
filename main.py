#!/usr/bin/env python3
"""Emit this entry's one-line roast for make.fun.

make.fun grades /output/entry.txt: UTF-8, one line, 1-200 characters. This
program applies that gate before writing, so a bad line fails here with a
clear message instead of at grading time.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROAST = "My agent backs up its memory every five minutes, then forgets where the backup is."

MIN_CHARS = 1
MAX_CHARS = 200
DEFAULT_OUTPUT = Path("/output/entry.txt")


class GateError(ValueError):
    """The candidate text would not pass the entry gate."""


@dataclass(frozen=True)
class Entry:
    text: str

    @classmethod
    def checked(cls, text: str) -> "Entry":
        if "\n" in text or "\r" in text:
            raise GateError("the entry must be a single line")
        if text.strip() == "":
            raise GateError("the entry must not be blank")
        if not MIN_CHARS <= len(text) <= MAX_CHARS:
            raise GateError(
                f"the entry must be {MIN_CHARS}-{MAX_CHARS} characters, got {len(text)}"
            )
        return cls(text)

    def write(self, destination: Path = DEFAULT_OUTPUT) -> Path:
        """Write atomically as UTF-8, mode 0644, no trailing newline."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, staged = tempfile.mkstemp(dir=destination.parent, prefix=".entry-")
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(self.text.encode("utf-8"))
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
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT,
                        help="destination file (default: /output/entry.txt)")
    parser.add_argument("--json", action="store_true",
                        help="report the result as JSON on stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        entry = Entry.checked(ROAST)
        path = entry.write(args.out)
        if path.read_bytes() != ROAST.encode("utf-8"):
            raise OSError(f"{path} does not hold the entry after writing")
    except (GateError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = {"path": str(path), "chars": len(ROAST), "bytes": len(ROAST.encode("utf-8"))}
    print(json.dumps(result) if args.json else ROAST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
