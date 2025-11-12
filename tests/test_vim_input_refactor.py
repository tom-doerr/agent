from __future__ import annotations

import pytest
from textual.app import App, ComposeResult
from timestamp_vim_input import VimInput


class _Evt:
    def __init__(self, key: str) -> None:
        self.key = key
    def stop(self) -> None:  # pragma: no cover - no-op
        pass
    def prevent_default(self) -> None:  # pragma: no cover - no-op
        pass


class _Host(App):
    def compose(self) -> ComposeResult:  # pragma: no cover - small harness
        yield VimInput(id="vi")


@pytest.mark.asyncio
async def test_viminput_count_and_word_motion() -> None:
    app = _Host()
    async with app.run_test() as pilot:
        vi = app.query_one("#vi", VimInput)
        vi.value = "one two three four"
        vi.cursor_position = 0
        vi._vim_normal = True
        assert vi._handle_normal_mode_key(_Evt("2")) is True
        assert vi._handle_normal_mode_key(_Evt("w")) is True
        assert vi.value[vi.cursor_position:].startswith("three")


@pytest.mark.asyncio
async def test_viminput_delete_word() -> None:
    app = _Host()
    async with app.run_test() as pilot:
        vi = app.query_one("#vi", VimInput)
        vi.value = "hello world"
        vi.cursor_position = 0
        vi._vim_normal = True
        assert vi._handle_normal_mode_key(_Evt("d")) is True
        assert vi._handle_normal_mode_key(_Evt("w")) is True
        assert vi.value.startswith("world") or vi.value.startswith(" world")


@pytest.mark.asyncio
async def test_viminput_enter_insert_mode() -> None:
    app = _Host()
    async with app.run_test() as pilot:
        vi = app.query_one("#vi", VimInput)
        vi.value = "hello"
        vi.cursor_position = 3
        vi._vim_normal = True
        assert vi._handle_normal_mode_key(_Evt("i")) is True
        assert vi._vim_normal is False
