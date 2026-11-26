#!/usr/bin/env python3
"""Write this entry's one-line roast to /output/entry.txt for make.fun."""
from pathlib import Path

# One line, UTF-8, no trailing newline: the gate counts characters, not bytes alone.
ROAST = "My agent backs up its memory every five minutes, then forgets where the backup is."

OUTPUT_DIR = Path("/output")
OUTPUT_FILE = OUTPUT_DIR / "entry.txt"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(ROAST, encoding="utf-8")
    OUTPUT_FILE.chmod(0o644)


if __name__ == "__main__":
    main()
