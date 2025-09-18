import json

import pytest

from textual.widgets import Input, TextArea

from textual_dspy.app import DSpyProgramApp
from textual_dspy.widgets import FlowTable, NodeDetail


@pytest.mark.asyncio
async def test_app_run_populates_flow_table():
    app = DSpyProgramApp()
    async with app.run_test() as pilot:
        await pilot.press("ctrl+r")
        for _ in range(5):
            if any(event["type"] == "run_complete" for event in app.controller.event_history):
                break
            await pilot.pause()
        await pilot.pause()
        table = app.query_one(FlowTable)
        assert table.row_count > 0
        assert any(event["type"] == "run_complete" for event in app.controller.event_history)


@pytest.mark.asyncio
async def test_app_override_controls_update_controller():
    app = DSpyProgramApp()
    async with app.run_test():
        node_detail = app.query_one(NodeDetail)
        # Select cognition node
        app.selected_node = "typed_cognition"
        node_detail.display_node(app.controller.node("typed_cognition"), {})
        override_field = node_detail.query_one("#detail-override", TextArea)
        override_field.text = json.dumps({"observation": "manually set"})
        app._apply_override()
        assert app.controller.overrides["typed_cognition"]["observation"] == "manually set"


@pytest.mark.asyncio
async def test_app_save_action(tmp_path):
    app = DSpyProgramApp()
    async with app.run_test():
        file_input = app.query_one("#file-path", Input)
        target = tmp_path / "graph.json"
        file_input.value = str(target)
        await app.action_save()
        assert target.exists()


@pytest.mark.asyncio
async def test_run_settings_inputs_update_controller():
    app = DSpyProgramApp()
    async with app.run_test():
        engine_input = app.query_one("#llm-engine", Input)
        model_input = app.query_one("#llm-model", Input)
        temperature_input = app.query_one("#llm-temperature", Input)
        tokens_input = app.query_one("#llm-max-tokens", Input)
        engine_input.value = "openai"
        model_input.value = "gpt-test"
        temperature_input.value = "0.7"
        tokens_input.value = "512"
        assert app._apply_run_settings_from_inputs()
        settings = app.controller.document.settings.llm
        assert settings.engine == "openai"
        assert settings.model == "gpt-test"
        assert settings.temperature == pytest.approx(0.7)
        assert settings.max_tokens == 512
