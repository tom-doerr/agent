from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import fcntl


@contextmanager
def locked_file(path: Path, mode: str = "a+"):
    """Advisory exclusive lock around file IO (minimal; Linux).

    Opens the file with ``mode`` (default a+), acquires LOCK_EX, yields the
    handle, then unlocks. No fallbacks.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open(mode, encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            yield fh
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

