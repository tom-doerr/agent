from __future__ import annotations

import json
from typing import Any, Dict, List, Literal

import dspy
from dspy.adapters.chat_adapter import ChatAdapter
from dspy.adapters.types.tool import Tool
from dspy.signatures.signature import ensure_signature


class ReadableReAct(dspy.Module):
    """Custom ReAct-style module that exposes rich trajectories and raw history."""

    def __init__(self, signature, tools, max_iters: int = 8) -> None:
        super().__init__()
        self.signature = ensure_signature(signature)
        self.max_iters = max_iters
        self.tools = self._prepare_tools(list(tools))
        self._step = dspy.Predict(self._step_signature())

    def forward(self, **inputs):
        trajectory: Dict[str, Any] = {}
        raw_history: List[str] = []
        adapter = dspy.settings.adapter or ChatAdapter()
        tool_names = list(self.tools.keys())

        for idx in range(self.max_iters):
            formatted = self._format_prompt(adapter, inputs, trajectory)
            raw_history.append(formatted)
            prediction = self._step(trajectory=self._render_trajectory(trajectory), **inputs)
            raw_history.append(self._format_prediction(prediction))

            tool_name: Literal[tuple(tool_names)] = prediction.next_tool_name
            tool_args: Dict[str, Any] = prediction.next_tool_args or {}
            step = {
                "thought": prediction.next_thought,
                "tool": tool_name,
                "args": tool_args,
                "observation": None,
            }

            tool = self.tools.get(tool_name)
            try:
                observation = tool(**tool_args) if tool else None
            except Exception as exc:  # pragma: no cover - defensive reporting
                observation = f"Execution error in {tool_name}: {exc}"
            step["observation"] = observation

            trajectory[f"thought_{idx}"] = step["thought"]
            trajectory[f"tool_name_{idx}"] = step["tool"]
            trajectory[f"tool_args_{idx}"] = step["args"]
            trajectory[f"observation_{idx}"] = observation

            if tool_name == "finish":
                break

        outputs = self._extract_outputs(trajectory)
        result = dspy.Prediction(**outputs, trajectory=trajectory)
        result.steps = self._trajectory_steps(trajectory)
        result.raw_history = raw_history
        return result

    def _extract_outputs(self, trajectory: Dict[str, Any]) -> Dict[str, Any]:
        outputs: Dict[str, Any] = {}
        last_observation = None
        idx = 0
        while f"observation_{idx}" in trajectory:
            last_observation = trajectory.get(f"observation_{idx}")
            idx += 1
        for name in self.signature.output_fields:
            if name == "answer":
                outputs[name] = last_observation or ""
            else:
                outputs[name] = trajectory.get(name, "")
        return outputs

    def _prepare_tools(self, tools: List[Any]) -> Dict[str, Tool]:
        prepared = {}
        for tool in tools:
            tool_obj = tool if isinstance(tool, Tool) else Tool(tool)
            prepared[tool_obj.name] = tool_obj
        if "finish" not in prepared:
            def finish(answer: str = "") -> str:
                return answer
            prepared["finish"] = Tool(
                finish,
                name="finish",
                desc="Signal completion by providing the final answer via answer=<text>.",
                args={"answer": "Final answer string."},
            )
        return prepared

    def _step_signature(self) -> dspy.Signature:
        inputs = dict(self.signature.input_fields)
        instructions = self._instructions()
        signature = dspy.Signature(inputs, instructions)
        signature = signature.append("trajectory", dspy.InputField(), type_=str)
        signature = signature.append("next_thought", dspy.OutputField(), type_=str)
        signature = signature.append("next_tool_name", dspy.OutputField(), type_=Literal[tuple(self.tools.keys())])
        signature = signature.append("next_tool_args", dspy.OutputField(), type_=dict[str, Any])
        return signature

    def _instructions(self) -> str:
        inputs = ", ".join(f"`{k}`" for k in self.signature.input_fields.keys()) or "the inputs"
        outputs = ", ".join(f"`{k}`" for k in self.signature.output_fields.keys()) or "the requested outputs"
        tool_lines = [f"- `{tool.name}`: {tool.desc}" for tool in self.tools.values()]
        tool_text = "\n".join(tool_lines)
        return (
            f"You are an Agent. Use the tools to reason about {inputs} and deliver {outputs}.\n"
            "For every turn you must produce a chain of thought, select the next tool, and provide JSON arguments.\n"
            "The available tools are:\n"
            f"{tool_text}\n"
            "Invoke `finish` when you have everything you need, providing `answer` with the final response.\n"
        )

    def _render_trajectory(self, trajectory: Dict[str, Any]) -> str:
        return json.dumps(trajectory, indent=2, default=str)

    def _format_prompt(self, adapter: ChatAdapter, inputs: Dict[str, Any], trajectory: Dict[str, Any]) -> str:
        signature = dspy.Signature(
            {**self.signature.input_fields, "trajectory": dspy.InputField()},
            self._instructions(),
        )
        content = adapter.format_user_message_content(signature, {**inputs, "trajectory": self._render_trajectory(trajectory)})
        return f"PROMPT:\n{content}"

    @staticmethod
    def _format_prediction(prediction: dspy.Prediction) -> str:
        payload = {
            "next_thought": getattr(prediction, "next_thought", ""),
            "next_tool_name": getattr(prediction, "next_tool_name", ""),
            "next_tool_args": getattr(prediction, "next_tool_args", {}),
        }
        return f"PREDICTION:\n{json.dumps(payload, indent=2, default=str)}"

    @staticmethod
    def _trajectory_steps(trajectory: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps: List[Dict[str, Any]] = []
        idx = 0
        while f"thought_{idx}" in trajectory:
            steps.append(
                {
                    "thought": trajectory.get(f"thought_{idx}", ""),
                    "tool": trajectory.get(f"tool_name_{idx}", ""),
                    "args": trajectory.get(f"tool_args_{idx}", {}),
                    "observation": trajectory.get(f"observation_{idx}", ""),
                }
            )
            idx += 1
        return steps
