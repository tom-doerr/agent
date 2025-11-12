
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
import random
import math

@dataclass
class Theory:
    text: str
    weight: float = 1.0

@dataclass
class WorldModel:
    name: str
    theories: List[Theory] = field(default_factory=list)

    def normalize(self) -> None:
        s = sum(max(t.weight, 0.0) for t in self.theories)
        if s <= 0.0 and self.theories:
            u = 1.0 / len(self.theories)
            for t in self.theories:
                t.weight = u
            return
        s = s or 1.0
        for t in self.theories:
            t.weight = max(t.weight, 0.0) / s

    def as_bullets(self, theories: List['Theory']) -> str:
        if not theories:
            return "(empty)"
        return "\n".join(f"- {t.text}" for t in theories)

    def to_dict(self) -> Dict:
        return {"name": self.name, "theories": [{"text": t.text, "weight": float(t.weight)} for t in self.theories]}

    @staticmethod
    def from_dict(d: Dict) -> "WorldModel":
        wm = WorldModel(d.get("name", "X"))
        wm.theories = [Theory(x["text"], float(x.get("weight", 1.0))) for x in d.get("theories", [])]
        wm.normalize()
        return wm

def _gumbel():
    u = min(max(random.random(), 1e-12), 1.0 - 1e-12)
    return -math.log(-math.log(u))

def weighted_sample_without_replacement(theories: List[Theory], k: int) -> List[Theory]:
    if not theories or k <= 0:
        return []
    k = min(k, len(theories))
    scored = []
    for t in theories:
        w = max(t.weight, 1e-12)
        score = math.log(w) + _gumbel()
        scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:k]]

def multiplicative_update(winner_sample: List[Theory], loser_sample: List[Theory], eta: float = 0.1, eps: float = 1e-6) -> None:
    eta = max(1e-9, min(eta, 0.999))
    for t in winner_sample:
        t.weight = max(eps, t.weight * (1.0 + eta))
    for t in loser_sample:
        t.weight = max(eps, t.weight * (1.0 - eta))
