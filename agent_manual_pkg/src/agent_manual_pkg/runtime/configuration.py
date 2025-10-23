from __future__ import annotations

from typing import Any, Dict

import dspy

from ..config import get_config, load_config, update_config
from ..signatures import AgentSignature
from .agent import ReadableReAct
from .models import MODEL_PRESETS, MODULE_INFO, MODULE_ORDER
from .tools import TOOLS

cfg_initial = load_config()
CURRENT_MODEL = cfg_initial.model if cfg_initial.model in MODEL_PRESETS else "chat"
if cfg_initial.model != CURRENT_MODEL:
    update_config(model=CURRENT_MODEL)

LM: dspy.LM | None = None
_AGENT: ReadableReAct | None = None


def _resolve_tokens(model_key: str, max_tokens: int | None) -> int:
    preset = MODEL_PRESETS[model_key]
    cfg = get_config()
    if max_tokens is not None:
        return max_tokens
    if cfg.max_tokens is not None:
        return cfg.max_tokens
    return preset["max_tokens"]


def build_lm(model_key: str, max_tokens: int | None = None) -> dspy.LM:
    preset = MODEL_PRESETS[model_key]
    tokens = _resolve_tokens(model_key, max_tokens)
    extra_kwargs: Dict[str, Any] = {}
    if "reasoning" in preset:
        extra_kwargs["reasoning"] = preset["reasoning"]
    return dspy.LM(
        model=preset["slug"],
        max_tokens=tokens,
        temperature=preset["temperature"],
        **extra_kwargs,
    )


def configure_model(model_key: str, max_tokens: int | None = None, persist: bool = True) -> None:
    if model_key not in MODEL_PRESETS:
        raise ValueError(f"unknown model '{model_key}'")

    tokens = _resolve_tokens(model_key, max_tokens)
    dspy.configure(lm=build_lm(model_key, tokens))

    cfg_current = get_config()
    module_map = dict(cfg_current.module_models)
    module_map["agent"] = model_key
    updates: Dict[str, Any] = {"model": model_key, "module_models": module_map}
    if max_tokens is not None:
        updates["max_tokens"] = tokens

    cfg = update_config(persist=persist, **updates)

    global CURRENT_MODEL, LM, _AGENT
    CURRENT_MODEL = cfg.model
    LM = dspy.settings.lm
    _AGENT = ReadableReAct(AgentSignature, tools=TOOLS, max_iters=8)


def configure_memory_model(model_key: str, persist: bool = True) -> None:
    _set_module_model("memory", model_key, persist=persist)


def get_module_model(name: str) -> str:
    cfg = get_config()
    return cfg.module_models.get(name, cfg.model)


def _set_module_model(module_name: str, model_key: str, *, persist: bool) -> None:
    if model_key not in MODEL_PRESETS:
        raise ValueError(f"unknown model '{model_key}'")
    cfg_current = get_config()
    module_map = dict(cfg_current.module_models)
    module_map[module_name] = model_key
    update_config(module_models=module_map, persist=persist)


def configure_satisfaction_goals_model(model_key: str, persist: bool = True) -> None:
    _set_module_model("satisfaction_goals", model_key, persist=persist)


def configure_satisfaction_score_model(model_key: str, persist: bool = True) -> None:
    _set_module_model("satisfaction_score", model_key, persist=persist)


configure_model(CURRENT_MODEL, persist=False)


def get_agent() -> ReadableReAct:
    if _AGENT is None:
        configure_model(get_config().model, persist=False)
    return _AGENT  # type: ignore[return-value]
