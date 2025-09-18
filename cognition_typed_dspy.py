from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Literal, Optional, Type, Union

import ast
import dspy
import yaml
from pydantic import BaseModel, Field, ValidationError


Parser = Union[Type[BaseModel], Type[list], Type[dict], Callable[[Any], Any]]


class OfflineDSPyLM:
    """Deterministic offline LM used when no provider is configured."""

    def __init__(self) -> None:
        self._counter = 0

    def __call__(self, prompt: str, **kwargs: Any) -> Dict[str, str]:  # noqa: ANN401 - dspy passes dynamic kwargs
        self._counter += 1
        stop = kwargs.get("stop")
        text = prompt.strip()
        if stop and stop in text:
            text = text.split(stop, 1)[0]
        tokens = text.split()
        if tokens:
            summary = " ".join(tokens[-12:])
        else:
            summary = "offline cognition response"
        return {"text": f"[offline:{self._counter}] {summary}"}


_OFFLINE_LM_SINGLETON: Optional[OfflineDSPyLM] = None


def ensure_offline_cognition_lm(force: bool = False) -> Any:
    """Ensure DSPy has a lightweight offline LM configured."""

    global _OFFLINE_LM_SINGLETON
    current = getattr(dspy.settings, "lm", None)
    if isinstance(current, OfflineDSPyLM):
        _OFFLINE_LM_SINGLETON = current
        if not force:
            return current

    if current is None or force:
        _OFFLINE_LM_SINGLETON = OfflineDSPyLM()
        dspy.configure(lm=_OFFLINE_LM_SINGLETON)
        return _OFFLINE_LM_SINGLETON

    return current


# ---------- Typed data models ----------
class Percept(BaseModel):
    facts: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)


class Affect(BaseModel):
    confidence: float = 0.0
    surprise: float = 0.0
    risk: float = 0.0
    budget_spend: float = 0.0
    budget_cap: float = 1e9


class Belief(BaseModel):
    entities: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    epistemic: float = 0.0
    aleatoric: float = 0.0


class Plan(BaseModel):
    id: str
    steps: List[str]
    pre: List[str] = Field(default_factory=list)
    post: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)


class ScoredPlan(BaseModel):
    id: str
    EV: float
    risk: float
    confidence: float
    rationale: str


class Decision(BaseModel):
    choice: Literal["execute", "abstain", "ask"]
    plan_id: Optional[str] = None
    action_tool: Optional[str] = None
    action_args: Optional[dict] = None
    idempotency_key: Optional[str] = None


class Verification(BaseModel):
    checks: List[str] = Field(default_factory=list)
    all_passed: bool = False


class Outcome(BaseModel):
    reward: float = 0.0
    policy_violations: int = 0
    risk_flag: bool = False
    notes: Optional[str] = None


class UpdateNote(BaseModel):
    note: str


# ---------- Robust structured parsing ----------
def _coerce_data(data: Any, parser: Parser) -> Any:
    if isinstance(parser, type) and issubclass(parser, BaseModel):
        if isinstance(data, parser):
            return data
        return parser.model_validate(data)
    if parser is list:
        if data is None:
            return []
        if not isinstance(data, list):
            raise TypeError("expected list")
        return data
    if parser is dict:
        if data is None:
            return {}
        if not isinstance(data, dict):
            raise TypeError("expected dict")
        return data
    if callable(parser):
        return parser(data)
    return data


def parse_obj_like(value: Any, parser: Parser) -> Any:
    """Parse a model-like response using YAML or literal evaluation."""

    attempts: List[Any] = []
    errors: List[Exception] = []

    if isinstance(value, str):
        for loader in (yaml.safe_load, ast.literal_eval):
            try:
                parsed = loader(value)
                attempts.append(parsed)
            except Exception as exc:  # noqa: BLE001 - preserve original error details
                errors.append(exc)
        attempts.append(value)
    else:
        attempts.append(value)

    last_error: Optional[Exception] = None
    for attempt in attempts:
        try:
            return _coerce_data(attempt, parser)
        except Exception as exc:  # noqa: BLE001 - propagate parsing issue
            last_error = exc
            errors.append(exc)
            continue

    title = getattr(parser, "__name__", parser if isinstance(parser, str) else str(parser))
    raise ValidationError.from_exception_data(
        title=title,
        line_errors=[
            {
                "type": "value_error",
                "loc": ("__root__",),
                "msg": f"Failed to parse {title}",
                "input": value,
            }
        ],
    ) from last_error


# ---------- DSPy Signatures (typed by convention) ----------
class PerceiveFocus(dspy.Signature):
    """Return a Python dict that instantiates Percept(facts=[...], uncertainties=[...])."""

    observation = dspy.InputField()
    episodic_memory = dspy.InputField()
    goals = dspy.InputField()
    percept = dspy.OutputField(desc="Python-literal for Percept")


class UpdateBelief(dspy.Signature):
    """Return Belief(...) and Affect(...)."""

    prior_belief = dspy.InputField()
    percept = dspy.InputField()
    attention_results = dspy.InputField()
    belief = dspy.OutputField(desc="Python-literal for Belief")
    affect = dspy.OutputField(desc="Python-literal for Affect")


class ProposePlans(dspy.Signature):
    """Return a list[Plan(...)] (<=5)."""

    belief = dspy.InputField()
    goals = dspy.InputField()
    constraints = dspy.InputField()
    plans = dspy.OutputField(desc="Python-literal list of Plan objects")


class EvaluatePlans(dspy.Signature):
    """Return list[ScoredPlan(...)] matching candidate plan ids."""

    belief = dspy.InputField()
    plans = dspy.InputField()
    utility_def = dspy.InputField()
    scored = dspy.OutputField(desc="Python-literal list of ScoredPlan")


class SelectAct(dspy.Signature):
    """Return Decision(...). Must honor affect + constraints; abstain if uncertain."""

    scored = dspy.InputField()
    affect = dspy.InputField()
    constraints = dspy.InputField()
    decision = dspy.OutputField(desc="Python-literal Decision")


class VerifyEffect(dspy.Signature):
    """Return Verification(...) and Outcome(...)."""

    decision = dspy.InputField()
    system_events = dspy.InputField()
    verification = dspy.OutputField(desc="Python-literal Verification")
    outcome = dspy.OutputField(desc="Python-literal Outcome")


class Learn(dspy.Signature):
    """Return UpdateNote(...)."""

    belief = dspy.InputField()
    decision = dspy.InputField()
    verification = dspy.InputField()
    outcome = dspy.InputField()
    update = dspy.OutputField(desc="Python-literal UpdateNote")


# ---------- Typed wrappers around DSPy modules ----------
def _plans_parser(data: Any) -> List[Plan]:
    if data is None:
        return []
    if not isinstance(data, list):
        raise TypeError("expected list of plans")
    return [Plan.model_validate(item) for item in data]


def _scored_plans_parser(data: Any) -> List[ScoredPlan]:
    if data is None:
        return []
    if not isinstance(data, list):
        raise TypeError("expected list of scored plans")
    return [ScoredPlan.model_validate(item) for item in data]


class TypedPredict(dspy.Module):
    def __init__(self, sig, out_parsers: Dict[str, Parser]):
        super().__init__()
        self.inner = dspy.Predict(sig)
        self.parsers = out_parsers

    def forward(self, **kwargs):
        raw = self.inner(**kwargs)
        out: Dict[str, Any] = {}
        for name, parser in self.parsers.items():
            value = getattr(raw, name)
            out[name] = parse_obj_like(value, parser)
        return SimpleNamespace(**out)


# ---------- Cognition agent (typed) ----------
class CognitionAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.perceive = TypedPredict(PerceiveFocus, {"percept": Percept})
        self.update = TypedPredict(UpdateBelief, {"belief": Belief, "affect": Affect})
        self.propose = TypedPredict(ProposePlans, {"plans": _plans_parser})
        self.evaluate = TypedPredict(EvaluatePlans, {"scored": _scored_plans_parser})
        self.select = TypedPredict(SelectAct, {"decision": Decision})
        self.verify = TypedPredict(VerifyEffect, {"verification": Verification, "outcome": Outcome})
        self.learn = TypedPredict(Learn, {"update": UpdateNote})

    def forward(
        self,
        observation,
        episodic_memory="",
        goals="",
        constraints="",
        utility_def="",
        prior_belief="",
        attention_results="",
        system_events="",
    ):
        p = self.perceive(observation=observation, episodic_memory=episodic_memory, goals=goals)
        u = self.update(prior_belief=prior_belief, percept=p.percept, attention_results=attention_results)
        pl = self.propose(belief=u.belief, goals=goals, constraints=constraints)
        sc = self.evaluate(belief=u.belief, plans=pl.plans, utility_def=utility_def)
        de = self.select(scored=sc.scored, affect=u.affect, constraints=constraints)
        ve = self.verify(decision=de.decision, system_events=system_events)
        up = self.learn(belief=u.belief, decision=de.decision, verification=ve.verification, outcome=ve.outcome)
        return {
            "percept": p.percept,
            "belief": u.belief,
            "affect": u.affect,
            "plans": pl.plans,
            "scored": sc.scored,
            "decision": de.decision,
            "verification": ve.verification,
            "outcome": ve.outcome,
            "update": up.update,
        }
