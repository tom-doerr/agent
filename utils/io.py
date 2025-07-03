"""Common I/O utilities for NDJSON handling."""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def ndjson_iter(path: Path) -> Iterable[Dict[str, Any]]:
    """Yield json objects from an NDJSON file."""
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    yield json.loads(line)


def append_ndjson(path: Path, obj: Dict[str, Any]) -> None:
    """Append object as JSON line to path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_ndjson(filepath: Path) -> List[Dict[str, Any]]:
    """Load entire NDJSON file into a list."""
    return list(ndjson_iter(filepath))


def save_ndjson(data: List[Dict[str, Any]], filepath: Path) -> None:
    """Save list of objects as NDJSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")