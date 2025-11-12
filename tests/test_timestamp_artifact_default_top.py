from __future__ import annotations

from pathlib import Path
import pytest

import timestamp_app_core as core
import timestamp_textual_app as wrap


@pytest.mark.asyncio
async def test_artifact_defaults_scrolled_top_core(tmp_path: Path):
    a = tmp_path / "artifact.md"
    a.write_text("\n".join(f"L{i}" for i in range(1, 51)), encoding="utf-8")
    c = tmp_path / "constraints.md"
    c.write_text("# 2025-11-12\n12:00:00 hello\n", encoding="utf-8")

    app = core.TimestampLogApp(artifact_path=a, constraints_path=c)
    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one("#artifact-view", core.Markdown)
        called = {"n": 0}

        def _spy_scroll_home(*args, **kwargs):  # noqa: ARG001
            called["n"] += 1

        try:
            view.scroll_home = _spy_scroll_home  # type: ignore[attr-defined]
        except Exception:
            pytest.skip("Markdown widget lacks scroll_home in this Textual version")

        app._load_artifact()
        assert called["n"] >= 1


@pytest.mark.asyncio
async def test_artifact_defaults_scrolled_top_wrapper(tmp_path: Path):
    a = tmp_path / "artifact.md"
    a.write_text("\n".join(f"L{i}" for i in range(1, 31)), encoding="utf-8")
    c = tmp_path / "constraints.md"
    c.write_text("# 2025-11-12\n12:00:00 hello\n", encoding="utf-8")

    app = wrap.TimestampLogApp(artifact_path=a, constraints_path=c)
    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one("#artifact-view", wrap.Markdown)
        called = {"n": 0}

        def _spy_scroll_home(*args, **kwargs):  # noqa: ARG001
            called["n"] += 1

        try:
            view.scroll_home = _spy_scroll_home  # type: ignore[attr-defined]
        except Exception:
            pytest.skip("Markdown widget lacks scroll_home in this Textual version")

        app._load_artifact()
        assert called["n"] >= 1

