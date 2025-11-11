from pathlib import Path
from typing import List


def tail_lines(path: Path, n: int) -> List[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()[-n:]


def append_line(path: Path, text: str) -> None:
    text = (text or "").rstrip("\n")
    if not text:
        return
    try:
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
    except Exception:
        existing = ""
    sep = "\n" if existing and not existing.endswith("\n") else ""
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{sep}{text}\n")

