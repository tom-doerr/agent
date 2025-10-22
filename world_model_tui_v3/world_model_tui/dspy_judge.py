
from __future__ import annotations
import json, re
import dspy

class ChooseWorldModel(dspy.Signature):
    """Given two candidate world models (bullet lists) and an observation, choose which model better explains the observation.
    Respond with EXACT JSON on a single line (no markdown fences):
    {"winner": "A"|"B", "justification": "one sentence"}
    """
    model_a: str = dspy.InputField(desc="Bullet list of A's sampled theories")
    model_b: str = dspy.InputField(desc="Bullet list of B's sampled theories")
    observation: str = dspy.InputField(desc="Observation to evaluate against")
    winner: str = dspy.OutputField(desc="Either 'A' or 'B'")
    justification: str = dspy.OutputField(desc="Concise justification")

def _parse_ab_from_text(text: str) -> str | None:
    toks = [re.sub(r"^[,.;:()\[\]{}]+|[,.;:()\[\]{}]+$", "", t).upper() for t in text.split()]
    cand = [t for t in toks if t in {"A", "B"}]
    return cand[-1] if cand else None

class WorldModelJudge(dspy.Module):
    def __init__(self, force_json: bool = True):
        super().__init__()
        self.force_json = force_json
        self.decide = dspy.Predict(ChooseWorldModel)

    def forward(self, model_a: str, model_b: str, observation: str):
        pred = self.decide(model_a=model_a, model_b=model_b, observation=observation)
        winner = (getattr(pred, "winner", "") or "").strip().upper()
        just = (getattr(pred, "justification", "") or "").strip()
        blob = f"{getattr(pred, 'winner', '')} {getattr(pred, 'justification', '')}".strip()
        if self.force_json and (winner not in {"A","B"}):
            text_fields = [blob]
            for attr in ("text", "raw", "content"):
                v = getattr(pred, attr, None)
                if isinstance(v, str):
                    text_fields.append(v)
            joined = "\n".join(tf for tf in text_fields if tf)
            m = re.search(r"{[\s\S]*}", joined)
            if m:
                try:
                    doc = json.loads(m.group(0))
                    winner = str(doc.get("winner", "")).strip().upper()
                    just = str(doc.get("justification", "")).strip() or just
                except Exception:
                    pass
        if winner not in {"A","B"}:
            alt = _parse_ab_from_text(blob)
            if alt:
                winner = alt
        if winner not in {"A","B"}:
            winner = "A"
        return dspy.Prediction(winner=winner, justification=just or blob)

# Offline fallback judge for testing without an LLM
class LocalHeuristicJudge:
    def __call__(self, model_a: str, model_b: str, observation: str):
        obs = observation.lower()
        score = lambda s: sum(tok in obs for tok in s.lower().replace('-', ' ').split())
        sa, sb = score(model_a), score(model_b)
        winner = "A" if sa >= sb else "B"
        return type("Pred", (), {"winner": winner, "justification": f"token overlap A={sa} B={sb}"})()
