#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def main() -> None:
    out_dir = Path(os.getenv("NLCO_META_DIR", ".nlco/meta"))
    out_dir.mkdir(parents=True, exist_ok=True)

    cc_json = json.loads(run(["radon", "cc", "-j", "."]))
    (out_dir / "radon_cc.json").write_text(json.dumps(cc_json, indent=2), encoding="utf-8")

    mi_json = json.loads(run(["radon", "mi", "-j", "."]))
    (out_dir / "radon_mi.json").write_text(json.dumps(mi_json, indent=2), encoding="utf-8")

    # Minimal HTML summary
    def hotspots(data: dict) -> list[tuple[str, int]]:
        items: list[tuple[str, int]] = []
        for path, blocks in data.items():
            for blk in blocks:
                if not isinstance(blk, dict):
                    continue
                rank = blk.get("rank")
                comp = blk.get("complexity", 0)
                name = blk.get("name") or blk.get("type", "?")
                if rank in {"C", "D", "E", "F"}:
                    items.append((f"{path}:{name}", int(comp)))
        return sorted(items, key=lambda x: -x[1])[:20]

    top = hotspots(cc_json)
    lines = [
        "<html><head><meta charset='utf-8'><title>Radon Report</title></head><body>",
        "<h1>Radon Cyclomatic Complexity (C–F)</h1>",
        "<ol>",
        *[f"<li>{name} — {score}</li>" for name, score in top],
        "</ol>",
        "</body></html>",
    ]
    (out_dir / "radon_summary.html").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
