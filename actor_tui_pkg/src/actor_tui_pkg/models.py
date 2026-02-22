"""Model presets and LM construction."""

from __future__ import annotations

import urllib.request
import json
from typing import Optional

import dspy

SPARK2_API_BASE = "http://spark-2:8000/v1"


def _fetch_spark2_model() -> Optional[str]:
    """Query spark-2 vLLM for the currently loaded model."""
    try:
        req = urllib.request.Request(f"{SPARK2_API_BASE}/models", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            models = data.get("data", [])
            if models:
                return models[0]["id"]
    except Exception:
        return None
    return None


MODEL_PRESETS = {
    "spark2": {"dynamic": True},
    "flash": {
        "slug": "openrouter/google/gemini-2.5-flash-preview",
        "temperature": 0.3,
        "max_tokens": 4000,
    },
}


def build_lm(model_key: str, max_tokens: Optional[int] = None) -> dspy.LM:
    if model_key == "spark2":
        return _build_spark2_lm(max_tokens)
    preset = MODEL_PRESETS[model_key]
    kwargs = {"temperature": preset.get("temperature", 0.3)}
    tokens = max_tokens or preset.get("max_tokens")
    if tokens:
        kwargs["max_tokens"] = tokens
    return dspy.LM(preset["slug"], **kwargs)


def _build_spark2_lm(max_tokens: Optional[int] = None) -> dspy.LM:
    model_id = _fetch_spark2_model()
    if not model_id:
        raise RuntimeError("Cannot reach spark-2:8000 or no model loaded")
    return dspy.LM(
        f"openai/{model_id}",
        api_base=SPARK2_API_BASE,
        api_key="unused",
        temperature=0.3,
        max_tokens=max_tokens or 4000,
    )
