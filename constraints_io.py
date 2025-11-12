from pathlib import Path
from typing import List
import os

from file_lock import locked_file


def tail_lines(path: Path, n: int) -> List[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()[-n:]


def append_line(path: Path, text: str) -> None:
    text = (text or "").rstrip("\n")
    if not text:
        return
    with locked_file(path, "a+") as fh:
        try:
            fh.seek(0)
            existing = fh.read()
        except Exception:
            existing = ""
        sep = "\n" if existing and not existing.endswith("\n") else ""
        fh.seek(0, os.SEEK_END)
        fh.write(f"{sep}{text}\n")
