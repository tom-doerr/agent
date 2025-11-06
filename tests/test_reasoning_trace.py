import importlib


def test_extract_reasoning_deepseek_shape(monkeypatch):
    mod = importlib.import_module('nlco_iter')
    msg = {
        "role": "assistant",
        "reasoning_content": "Step 1: think... Step 2: result.",
        "content": "Final answer text",
    }
    out = mod._extract_reasoning_from_message(msg)
    assert out == "Step 1: think... Step 2: result."


def test_extract_reasoning_openrouter_shape(monkeypatch):
    mod = importlib.import_module('nlco_iter')
    msg = {
        "role": "assistant",
        "reasoning": {"type": "reasoning.text", "text": "Chain: a -> b -> c"},
        "content": "Done",
    }
    out = mod._extract_reasoning_from_message(msg)
    assert out == "Chain: a -> b -> c"
