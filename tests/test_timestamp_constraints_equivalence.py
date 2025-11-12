from __future__ import annotations

from pathlib import Path

import timestamp_textual_app as wrap
import timestamp_app_core as core


def test_wrapper_and_core_render_same_tail(tmp_path: Path):
    # same file, same pane height -> identical rendered text
    c = tmp_path / "constraints.md"
    c.write_text("\n".join(f"L{i:03d}" for i in range(1, 41)), encoding="utf-8")

    w_app = wrap.TimestampLogApp(constraints_path=c)
    c_app = core.TimestampLogApp(constraints_path=c)

    w_cap, c_cap = {}, {}

    class Size:
        def __init__(self, h: int) -> None:
            self.height = h

    class WView:
        def __init__(self) -> None:
            self.size = Size(10)  # tail = 8
        def update(self, text: str):
            w_cap["txt"] = text

    class CView:
        def __init__(self) -> None:
            self.size = Size(10)
        def update(self, text: str):
            c_cap["txt"] = text

    class Title:
        def update(self, text: str):
            pass

    # Inject fake views with same height
    w_app._constraints_view = WView()
    w_app._constraints_title = Title()
    c_app._constraints_view = CView()
    c_app._constraints_title = Title()

    w_app._load_constraints()
    c_app._load_constraints()
    assert w_cap.get("txt") == c_cap.get("txt")

