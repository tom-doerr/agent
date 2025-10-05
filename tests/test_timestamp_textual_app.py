from datetime import datetime
from pathlib import Path
import sys

import pytest
from textual.widgets import Input, TextArea, Static

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from timestamp_textual_app import TimestampLogApp, VimInput


def make_app(tmp_path, content="Artifact line", refresh=0.5) -> TimestampLogApp:
    artifact_file = tmp_path / "artifact.md"
    artifact_file.write_text(content)
    constraints_file = tmp_path / "constraints.md"
    constraints_file.write_text("")
    return TimestampLogApp(
        artifact_path=artifact_file,
        constraints_path=constraints_file,
        artifact_refresh_seconds=refresh,
    )


@pytest.mark.asyncio
async def test_timestamp_app_formats_entries(monkeypatch, tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        log = app.query_one("#log")
        input_widget = app.query_one("#input", Input)

        monkeypatch.setattr(app, "_current_time", lambda: datetime(2025, 10, 5, 9, 30))

        input_widget.value = "Check autoposter"
        await pilot.press("enter")
        await pilot.pause()

        lines = [str(line) for line in log.lines]
        assert "# 2025-10-05" in lines
        assert "0930 Check autoposter" in lines
        assert input_widget.value == ""

        constraints_text = app._constraints_path.read_text()
        assert "# 2025-10-05" in constraints_text
        assert "0930 Check autoposter" in constraints_text


@pytest.mark.asyncio
async def test_multiple_entries_same_day_add_single_heading(monkeypatch, tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        log = app.query_one("#log")
        input_widget = app.query_one("#input", Input)

        timestamps = iter(
            [
                datetime(2025, 10, 5, 9, 30),
                datetime(2025, 10, 5, 10, 15),
            ]
        )
        monkeypatch.setattr(app, "_current_time", lambda: next(timestamps))

        input_widget.value = "Morning check"
        await pilot.press("enter")
        await pilot.pause()

        input_widget.value = "Mid-morning update"
        await pilot.press("enter")
        await pilot.pause()

        lines = [str(line) for line in log.lines]
        assert lines.count("# 2025-10-05") == 1
        assert "0930 Morning check" in lines
        assert "1015 Mid-morning update" in lines

        constraints_lines = app._constraints_path.read_text().splitlines()
        assert constraints_lines.count("# 2025-10-05") == 1
        assert "0930 Morning check" in constraints_lines
        assert "1015 Mid-morning update" in constraints_lines


@pytest.mark.asyncio
async def test_blank_submission_does_not_log(tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        log = app.query_one("#log")
        input_widget = app.query_one("#input", Input)

        input_widget.value = "   "
        await pilot.press("enter")
        await pilot.pause()

        assert not log.lines
        assert app._constraints_path.read_text().strip() == ""


@pytest.mark.asyncio
async def test_new_day_inserts_date_heading(monkeypatch, tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        log = app.query_one("#log")
        input_widget = app.query_one("#input", Input)

        timestamps = iter(
            [
                datetime(2025, 10, 5, 23, 55),
                datetime(2025, 10, 6, 0, 5),
            ]
        )
        monkeypatch.setattr(app, "_current_time", lambda: next(timestamps))

        input_widget.value = "Wrap up day"
        await pilot.press("enter")
        await pilot.pause()

        input_widget.value = "Start new day"
        await pilot.press("enter")
        await pilot.pause()

        lines = [str(line) for line in log.lines]
        assert "# 2025-10-05" in lines
        assert "# 2025-10-06" in lines
        assert any(line.startswith("2355 Wrap up day") for line in lines)
        assert any(line.startswith("0005 Start new day") for line in lines)

        constraints_text = app._constraints_path.read_text()
        assert constraints_text.count("# 2025-10-05") == 1
        assert constraints_text.count("# 2025-10-06") == 1
        assert "2355 Wrap up day" in constraints_text
        assert "0005 Start new day" in constraints_text


@pytest.mark.asyncio
async def test_artifact_displayed_on_mount(tmp_path):
    app = make_app(tmp_path, content="Line A\nLine B")

    async with app.run_test() as pilot:
        await pilot.pause()
        artifact_view = app.query_one("#artifact-view", TextArea)
        assert "Line A" in artifact_view.text
        assert "Line B" in artifact_view.text
        help_panel = app.query_one("#help-panel", Static)
        assert help_panel.visible
        assert app._help_message
        assert "Ctrl+H" in app._help_message
        assert "Esc" in app._help_message
        assert app._artifact_status_message.startswith("Artifact updated")


@pytest.mark.asyncio
async def test_artifact_refreshes_on_change(tmp_path):
    app = make_app(tmp_path, content="Initial", refresh=0.05)
    artifact_path = app._artifact_path
    constraints_path = app._constraints_path

    async with app.run_test() as pilot:
        artifact_view = app.query_one("#artifact-view", TextArea)
        await pilot.pause()
        assert "Initial" in artifact_view.text
        assert app._artifact_status_message.startswith("Artifact updated")

        artifact_path.write_text("Updated content")

        updated = False
        for _ in range(20):
            await pilot.pause()
            if "Updated content" in artifact_view.text:
                updated = True
                break

        assert updated, "artifact view did not refresh with latest content"
        assert app._artifact_status_message.startswith("Artifact updated")
        assert constraints_path.read_text().strip() == ""


@pytest.mark.asyncio
async def test_help_toggle(tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        help_panel = app.query_one("#help-panel", Static)
        await pilot.pause()
        assert help_panel.visible

        await pilot.press("ctrl+h")
        await pilot.pause()
        assert not help_panel.visible
        assert app._help_message == ""

        await pilot.press("ctrl+h")
        await pilot.pause()
        assert help_panel.visible
        assert "Ctrl+H" in app._help_message
        assert "Esc" in app._help_message


@pytest.mark.asyncio
async def test_vim_input_navigation(tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        input_widget = app.query_one(VimInput)
        text = "hello"
        input_widget.value = text
        input_widget.cursor_position = len(text)

        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("h")
        await pilot.pause()
        assert input_widget.value == text
        assert input_widget._vim_normal

        await pilot.press("0")
        await pilot.pause()
        assert input_widget._vim_normal

        await pilot.press("x")
        await pilot.pause()
        assert input_widget.value == "ello"

        await pilot.press("i")
        await pilot.pause()
        assert not input_widget._vim_normal
        await pilot.press("!")
        await pilot.pause()
        assert input_widget.value.startswith("!ello")


@pytest.mark.asyncio
async def test_vim_dw_diW_ciw(tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        input_widget = app.query_one(VimInput)

        input_widget.value = "hello world"
        input_widget.cursor_position = 0
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("d")
        await pilot.press("w")
        await pilot.pause()
        assert input_widget.value == "world"
        assert input_widget.cursor_position == 0

        input_widget.value = "alpha beta"
        input_widget.cursor_position = len("alpha ") + 1
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("d")
        await pilot.press("i")
        await pilot.press("w")
        await pilot.pause()
        assert input_widget.value == "alpha "
        assert input_widget.cursor_position == len("alpha ")

        input_widget.value = "foo bar"
        input_widget.cursor_position = len("foo ") + 1
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("c")
        await pilot.press("i")
        await pilot.press("w")
        await pilot.pause()
        assert input_widget.value == "foo "
        assert not input_widget._vim_normal
        await pilot.press("B")
        await pilot.pause()
        assert input_widget.value == "foo B"


@pytest.mark.asyncio
async def test_vim_capital_c(tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        input_widget = app.query_one(VimInput)
        input_widget.value = "foo bar baz"
        input_widget.cursor_position = len("foo ")
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("C")
        await pilot.pause()
        assert input_widget.value == "foo "
        assert not input_widget._vim_normal
        await pilot.press("X")
        await pilot.pause()
        assert input_widget.value == "foo X"


@pytest.mark.asyncio
async def test_vim_motions_w_b(tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        input_widget = app.query_one(VimInput)
        input_widget.value = "alpha beta gamma"
        input_widget.cursor_position = 0
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("w")
        await pilot.pause()
        assert input_widget.cursor_position == len("alpha ")
        await pilot.press("w")
        await pilot.pause()
        assert input_widget.cursor_position == len("alpha beta ")
        await pilot.press("b")
        await pilot.pause()
        assert input_widget.cursor_position == len("alpha ")


@pytest.mark.asyncio
async def test_vim_delete_aw(tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        input_widget = app.query_one(VimInput)
        input_widget.value = "foo  bar"
        input_widget.cursor_position = len("foo  ")
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("d")
        await pilot.press("a")
        await pilot.press("w")
        await pilot.pause()
        assert input_widget.value == "foo"


@pytest.mark.asyncio
async def test_vim_counted_delete(tmp_path):
    app = make_app(tmp_path)

    async with app.run_test() as pilot:
        input_widget = app.query_one(VimInput)
        input_widget.value = "one two three four"
        input_widget.cursor_position = 0
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("2")
        await pilot.press("d")
        await pilot.press("w")
        await pilot.pause()
        assert input_widget.value == "three four"
