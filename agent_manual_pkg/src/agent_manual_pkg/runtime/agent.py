from __future__ import annotations

from typing import Any, Dict, List

import dspy


class ReadableReAct:
    """Thin wrapper around DSPy's ReAct to expose intermediate steps."""

    def __init__(self, signature, tools, max_iters: int = 8) -> None:
        self.signature = signature
        self.tools = tools
        self.max_iters = max_iters
        self._build()

    def _build(self) -> None:
        self._core = dspy.ReAct(self.signature, tools=self.tools, max_iters=self.max_iters)

    def run(self, prompt: str) -> Dict[str, Any]:
        prediction = self._core(prompt=prompt)
        steps: List[Dict[str, Any]] = []
        idx = 0
        while f"thought_{idx}" in prediction.trajectory:
            steps.append(
                {
                    "thought": prediction.trajectory.get(f"thought_{idx}", ""),
                    "tool": prediction.trajectory.get(f"tool_name_{idx}", ""),
                    "args": prediction.trajectory.get(f"tool_args_{idx}", {}),
                    "observation": prediction.trajectory.get(f"observation_{idx}", ""),
                }
            )
            idx += 1

        answer = getattr(prediction, "answer", None)
        for attr in ("final_answer", "content", "response"):
            if not answer and hasattr(prediction, attr):
                answer = getattr(prediction, attr)

        return {"answer": answer or "", "steps": steps, "prediction": prediction}

