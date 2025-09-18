"""Unit tests for the lightweight LLM engine helpers."""

from __future__ import annotations

import builtins
import sys
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from web_dspy_builder.llm import (
    DSPyWrapper,
    LLMEngine,
    LLMError,
    LLMSettings,
)


def test_mock_llm_is_deterministic() -> None:
    """The mock engine should produce deterministic completions per prompt."""

    engine = LLMEngine(LLMSettings(engine="mock", model="demo"))

    first = engine.complete("hello world")
    second = engine.complete("hello world")
    alternate = engine.complete("a longer alternate prompt")
    truncated = engine.complete("stop sequence included", stop="sequence")

    assert first == second
    assert alternate != first
    assert "sequence" not in truncated


def test_dspy_engine_configures_and_calls_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-mock engines should import dspy, configure the LM, and pass parameters."""

    configure_calls: list[dict[str, object]] = []
    lm_instances: list[DummyLM] = []

    class DummyLM:
        def __init__(self, model: str, **kwargs: object) -> None:
            self.model = model
            self.kwargs = kwargs
            self.calls: list[tuple[str, dict[str, object]]] = []

        def __call__(self, *, prompt: str, **params: object) -> dict[str, object]:
            self.calls.append((prompt, params))
            return {"text": prompt.upper()}

    def lm_factory(model: str, **kwargs: object) -> DummyLM:
        instance = DummyLM(model, **kwargs)
        lm_instances.append(instance)
        return instance

    def configure(**kwargs: object) -> None:
        configure_calls.append(kwargs)

    monkeypatch.setitem(sys.modules, "dspy", SimpleNamespace(LM=lm_factory, configure=configure))

    settings = LLMSettings(
        engine="openai",
        model="custom-model",
        temperature=0.42,
        max_tokens=77,
        params={"foo": "bar"},
    )
    engine = LLMEngine(settings)
    result = engine.complete("prompt text", stop="END")

    assert result == "PROMPT TEXT"
    assert configure_calls == [{"lm": lm_instances[0]}]

    lm_instance = lm_instances[0]
    assert lm_instance.model == "custom-model"
    assert lm_instance.kwargs == {"foo": "bar"}
    prompt, params = lm_instance.calls[0]
    assert prompt == "prompt text"
    assert params["temperature"] == pytest.approx(0.42)
    assert params["max_new_tokens"] == 77
    assert params["foo"] == "bar"
    assert params["stop"] == "END"


def test_dspy_wrapper_accepts_plain_strings() -> None:
    """DSPyWrapper should accept raw string responses."""

    settings = LLMSettings(engine="dspy")

    class PlainLM:
        def __call__(self, *, prompt: str, **params: object) -> str:  # noqa: D401 - simple stub
            return prompt[::-1]

    wrapper = DSPyWrapper(settings, PlainLM())
    assert wrapper.complete("abc") == "cba"


def test_dspy_wrapper_rejects_empty_payload() -> None:
    """A missing text payload should raise an error."""

    settings = LLMSettings(engine="dspy")

    class EmptyLM:
        def __call__(self, *, prompt: str, **params: object) -> dict[str, object]:
            return {}

    wrapper = DSPyWrapper(settings, EmptyLM())
    with pytest.raises(LLMError):
        wrapper.complete("hello")


def test_llm_engine_requires_dspy_for_remote_engines(monkeypatch: pytest.MonkeyPatch) -> None:
    """Import errors from dspy should surface as configuration problems."""

    real_import = builtins.__import__

    def failing_import(name: str, *args: object, **kwargs: object):  # type: ignore[override]
        if name == "dspy":
            raise ModuleNotFoundError("No module named 'dspy'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", failing_import)

    with pytest.raises(LLMError):
        LLMEngine(LLMSettings(engine="openai"))


def test_llm_engine_rejects_unknown_engine() -> None:
    """Pydantic validation should block unsupported engine names."""

    with pytest.raises(ValidationError):
        LLMSettings(engine="mystery")
