"""Language model management for the DSPy builder backend."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .models import LLMSettings


class LLMError(RuntimeError):
    """Raised when the language model cannot fulfil a request."""


class BaseLLM:
    """Simple interface implemented by all language model wrappers."""

    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings

    def complete(self, prompt: str, *, stop: Optional[str] = None) -> str:
        raise NotImplementedError


class MockLLM(BaseLLM):
    """Deterministic mock model used for testing and offline work."""

    def __init__(self, settings: LLMSettings) -> None:
        super().__init__(settings)
        seed_material = settings.model or "mock"
        self._seed = int(hashlib.sha256(seed_material.encode("utf-8")).hexdigest(), 16) % (2**32)

    def complete(self, prompt: str, *, stop: Optional[str] = None) -> str:
        random.seed(self._seed + len(prompt))
        tag = self.settings.model or "mock"
        body = prompt.strip()
        if stop and stop in body:
            body = body.split(stop, 1)[0]
        snippet = body[-160:]
        scrambled = "".join(reversed(snippet.split()))
        return f"[{tag}] {scrambled}"


@dataclass
class DSPyWrapper(BaseLLM):
    """Wrapper around dspy LMs with optional lazy imports."""

    lm: Any

    def __init__(self, settings: LLMSettings, lm: Any) -> None:
        super().__init__(settings)
        self.lm = lm

    def complete(self, prompt: str, *, stop: Optional[str] = None) -> str:
        params: Dict[str, Any] = {
            "temperature": self.settings.temperature,
            "max_new_tokens": self.settings.max_tokens,
        }
        params.update(self.settings.params)
        if stop:
            params["stop"] = stop

        # The dspy LM callable returns a dict with a "text" field for completions.
        response = self.lm(prompt=prompt, **params)
        if isinstance(response, dict):
            text = response.get("text") or response.get("completion")
        else:
            text = str(response)
        if text is None:
            raise LLMError("Language model returned no completion")
        return text


class LLMEngine:
    """Configure and invoke language models based on runtime settings."""

    def __init__(self, settings: Optional[LLMSettings] = None) -> None:
        self.settings = settings or LLMSettings()
        self._impl: BaseLLM = self._create_impl()

    def _create_impl(self) -> BaseLLM:
        engine = self.settings.engine
        if engine == "mock":
            return MockLLM(self.settings)

        try:
            import dspy  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise LLMError(
                "dspy is required for non-mock engines but could not be imported"
            ) from exc

        if engine == "dspy":
            model_name = self.settings.model or "openrouter/google/gemini-2.0-flash-thinking"
            lm = dspy.LM(model_name, **self.settings.params)
        elif engine == "openrouter":
            model_name = self.settings.model or "openrouter/google/gemini-2.0-flash-thinking"
            lm = dspy.LM(model_name, **self.settings.params)
        elif engine == "openai":
            model_name = self.settings.model or "openai/gpt-4o-mini"
            lm = dspy.LM(model_name, **self.settings.params)
        elif engine == "ollama":
            model_name = self.settings.model or "ollama/llama3.1"
            lm = dspy.LM(model_name, **self.settings.params)
        else:  # pragma: no cover - defensive
            raise LLMError(f"Unsupported LLM engine: {engine}")

        dspy.configure(lm=lm)
        return DSPyWrapper(self.settings, lm)

    def complete(self, prompt: str, *, stop: Optional[str] = None) -> str:
        return self._impl.complete(prompt, stop=stop)

