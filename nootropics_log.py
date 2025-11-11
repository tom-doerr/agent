import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional


def _default_path() -> Path:
    p = os.getenv("NLCO_NOOTROPICS_LOG")
    return Path(p).expanduser() if p else (Path.home() / ".nootropics_log.jsonl")


def load_recent_nootropics_lines(hours: int = 72, limit: int = 30, path: Optional[Path | str] = None) -> List[str]:
    """Return last `limit` JSONL lines from the nootropics log within `hours`.

    - Read-only: never writes or truncates the source file.
    - Minimal schema handling: requires an ISO `ts` field per JSON line.
    """
    src = Path(path).expanduser() if path else _default_path()
    if not src.exists():
        return []
    cutoff = datetime.now() - timedelta(hours=hours)
    recent: List[str] = []
    with src.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                ts = obj.get("ts")
                if not isinstance(ts, str):
                    continue
                dt = datetime.fromisoformat(ts)
                if dt >= cutoff:
                    recent.append(line)
            except Exception:
                # Keep it simple: skip malformed lines.
                continue
    if not recent:
        return []
    return recent[-limit:]


def append_nootropics_section(context: str, *, hours: int = 72, limit: int = 30, path: Optional[Path | str] = None) -> str:
    lines = load_recent_nootropics_lines(hours=hours, limit=limit, path=path)
    if not lines:
        return context
    return context + "\n\nNootropics (last 72h)\n" + "\n".join(lines)
