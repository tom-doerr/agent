from __future__ import annotations

from pathlib import Path
import os
import subprocess


def _run(cmd: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, env=env, check=False)


def test_constraints_add_entry_appends_with_heading(tmp_path: Path):
    target = tmp_path / "constraints.md"
    env = os.environ.copy()
    env["NLCO_CONSTRAINTS_PATH"] = str(target)

    script = Path("scripts/constraints_add_entry.py").absolute()

    # first line of the day creates a date heading and the line
    r1 = _run(["python3", str(script), "--now", "2025-11-12 12:34:56", "hello"], env)
    assert r1.returncode == 0, r1.stderr
    text = target.read_text(encoding="utf-8")
    assert "# 2025-11-12\n" in text
    assert "12:34:56 hello\n" in text

    # second line same day: no duplicate heading
    r2 = _run(["python3", str(script), "--now", "2025-11-12 12:35:00", "world"], env)
    assert r2.returncode == 0, r2.stderr
    text2 = target.read_text(encoding="utf-8")
    assert text2.count("# 2025-11-12\n") == 1
    assert "12:35:00 world\n" in text2

    # next day adds a new heading
    r3 = _run(["python3", str(script), "--now", "2025-11-13 00:01:00", "next"], env)
    assert r3.returncode == 0, r3.stderr
    text3 = target.read_text(encoding="utf-8")
    assert "# 2025-11-13\n" in text3
    assert "00:01:00 next\n" in text3

