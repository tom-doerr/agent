import os
import subprocess
import tempfile
from pathlib import Path


def run_scan(paths):
    script = Path("scripts/secrets_scan.sh").resolve()
    assert script.exists()
    res = subprocess.run(["bash", str(script), *[str(p) for p in paths]], capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr


def test_scan_all_clear(tmp_path: Path):
    p = tmp_path / "safe.txt"
    p.write_text("hello world\nno secrets here\n", encoding="utf-8")
    code, out, err = run_scan([p])
    assert code == 0


def test_scan_detects_github_token(tmp_path: Path):
    # 36+ chars after ghp_
    token = "ghp_" + ("A" * 40)
    p = tmp_path / "leak.txt"
    p.write_text(f"commit with {token}\n", encoding="utf-8")
    code, out, err = run_scan([p])
    assert code == 1
    assert "Secret-like strings" in (out + err)

