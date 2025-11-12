from __future__ import annotations

import json
from pathlib import Path
import types
import subprocess


def test_gen_radon_report_monkeypatched(tmp_path, monkeypatch):
    # Fake radon outputs
    fake_cc = json.dumps({
        "a.py": [
            {"type": "function", "rank": "C", "lineno": 1, "col_offset": 0, "complexity": 12, "name": "f", "endline": 10, "closures": []}
        ]
    })
    fake_mi = json.dumps({"a.py": {"mi": 42.0, "rank": "A"}})

    class Res:
        def __init__(self, out: str):
            self.stdout = out

    def fake_run(cmd, check=True, capture_output=True, text=True):
        if cmd[:2] == ["radon", "cc"]:
            return Res(fake_cc)
        if cmd[:2] == ["radon", "mi"]:
            return Res(fake_mi)
        raise AssertionError("unexpected command")

    from scripts import gen_radon_report as script
    monkeypatch.setenv("NLCO_META_DIR", str(tmp_path / ".nlco/meta"))
    monkeypatch.setattr(script.subprocess, "run", fake_run)
    script.main()

    out_dir = tmp_path / ".nlco/meta"
    assert (out_dir / "radon_cc.json").exists()
    assert (out_dir / "radon_mi.json").exists()
    html = (out_dir / "radon_summary.html").read_text(encoding="utf-8")
    assert "C–F" in html and "a.py:f" in html

