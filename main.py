#!/usr/bin/env python3
"""Write this entry's one-line roast to /output/entry.txt for make.fun.

The entry gate accepts UTF-8 text of 1 to 200 characters that is not only
white space.  We enforce the same shape here, before anything is written, so
a bad edit fails in this program instead of at grading time.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROAST = "My agent backs up its memory every five minutes, then forgets where the backup is."

MIN_CHARS = 1
MAX_CHARS = 200
OUTPUT_DIR = Path("/output")
OUTPUT_FILE = OUTPUT_DIR / "entry.txt"


def validate(text: str) -> str:
    """Return *text* when it passes the entry gate; raise ValueError otherwise."""
    if "\n" in text or "\r" in text:
        raise ValueError("the entry must be a single line")
    stripped = text.strip()
    if not MIN_CHARS <= len(stripped) <= MAX_CHARS:
        raise ValueError(
            f"the entry must be {MIN_CHARS}-{MAX_CHARS} characters, got {len(stripped)}"
        )
    return text


def write_entry(text: str, output_file: Path = OUTPUT_FILE) -> Path:
    """Validate *text* and write it as UTF-8, mode 0644, without a trailing newline."""
    payload = validate(text).encode("utf-8")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_bytes(payload)
    output_file.chmod(0o644)
    return output_file


def main() -> int:
    try:
        path = write_entry(ROAST)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    written = path.read_bytes().decode("utf-8")
    if written != ROAST:
        print(f"error: wrote {written!r}, expected {ROAST!r}", file=sys.stderr)
        return 1
    print(written)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
