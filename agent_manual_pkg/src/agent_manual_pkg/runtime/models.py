from __future__ import annotations

from typing import Any, Dict

MODEL_PRESETS: Dict[str, Dict[str, Any]] = {
    "chat": {
        "slug": "openrouter/deepseek/deepseek-v3.2-exp",
        "temperature": 0.3,
        "max_tokens": 7000,
        "reasoning": {"max_tokens": 2000},
    },
    "reasoner": {
        "slug": "openrouter/deepseek/deepseek-v3.2-exp",
        "temperature": 0.9,
        "max_tokens": 16000,
        "reasoning": {"max_tokens": 4000},
    },
}

MODULE_ORDER = ["agent", "memory", "satisfaction_goals", "satisfaction_score"]

MODULE_INFO: Dict[str, Dict[str, str]] = {
    "agent": {"label": "Agent ReAct pipeline", "configure": "configure_model"},
    "memory": {"label": "Memory summarizer", "configure": "configure_memory_model"},
    "satisfaction_goals": {"label": "Satisfaction goal planner", "configure": "configure_satisfaction_goals_model"},
    "satisfaction_score": {"label": "Satisfaction scoring", "configure": "configure_satisfaction_score_model"},
}
