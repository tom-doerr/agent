
from __future__ import annotations
import os
import dspy

class LMConfigError(RuntimeError):
    pass

def configure_lm(provider: str, max_tokens: int = 1024, temperature: float = 0.0):
    """Configure DSPy to use the selected provider.
    Supported:
      - 'local-heuristic' (offline)
      - 'deepseek-chat'
      - 'deepseek-reasoner'
      - 'gemini-2.5-flash'
      - 'gemini-2.5-flash-lite'
    Returns the configured LM (or None for local-heuristic).
    """
    provider = (provider or "").strip()

    if provider == "local-heuristic":
        # No LM configuration needed
        return None

    if provider in {"deepseek-chat", "deepseek-reasoner"}:
        api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_TOKEN") or ""
        if not api_key:
            raise LMConfigError("Missing DEEPSEEK_API_KEY.")
        lm = dspy.LM(
            model=f"openai/{provider}",
            api_key=api_key,
            api_base="https://api.deepseek.com",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60,
        )
        dspy.settings.configure(lm=lm, max_tokens=max_tokens)
        return lm

    if provider in {"gemini-2.5-flash", "gemini-2.5-flash-lite"} or provider.startswith("gemini"):
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
        if not api_key:
            raise LMConfigError("Missing GOOGLE_API_KEY (or GEMINI_API_KEY).")
        lm = dspy.LM(
            model=f"gemini/{provider}",
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60,
        )
        dspy.settings.configure(lm=lm, max_tokens=max_tokens)
        return lm

    raise LMConfigError(f"Unsupported provider: {provider}")
