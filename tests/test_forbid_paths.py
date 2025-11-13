import subprocess
from pathlib import Path


def run_forbid(paths):
    script = Path("scripts/forbid_paths.sh").resolve()
    assert script.exists()
    res = subprocess.run(["bash", str(script), *[str(p) for p in paths]], capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr


def test_allow_safe_file(tmp_path: Path):
    p = tmp_path / "safe.txt"
    p.write_text("ok\n", encoding="utf-8")
    code, out, err = run_forbid([p])
    assert code == 0


def test_block_sensitive_root_names(tmp_path: Path):
    # Only exact repo-root names are blocked; simulate by basename match
    for name in [
        "constraints.md",
        "memory.md",
        "short_term_memory.md",
        "notes.md",
        "info.md",
    ]:
        p = tmp_path / name
        p.write_text("content\n", encoding="utf-8")
        code, out, err = run_forbid([p])
        assert code == 1
        assert "Blocked committing sensitive" in (out + err)

