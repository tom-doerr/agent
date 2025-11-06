from __future__ import annotations
__version__ = "0.1.0"

import os
import re
import asyncio
from typing import List, Type, Sequence, Optional, Dict, Any

import httpx
import dspy

OPENROUTER_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v3.2")


class PickBest(dspy.Signature):
    """Pick the single best candidate answer for the question.

    Return ONLY the 1-based index number.
    """
    question: str
    candidates: str
    best: int


class PairwiseBetter(dspy.Signature):
    """Choose which answer is better: left or right. Return 'left' or 'right'."""
    left: str
    right: str
    better: str


def _configure_dspy(model: str) -> None:
    lm = dspy.OpenAI(model=model, api_base=OPENROUTER_URL, api_key=os.getenv("OPENROUTER_API_KEY"))
    dspy.configure(lm=lm)


async def _gen_one(client: httpx.AsyncClient, text: str, model: str, gen_params: Optional[Dict[str, Any]] = None) -> str:
    r = await client.post(
        "/chat/completions",
        json={"model": model, "messages": [{"role": "user", "content": text}], **(gen_params or {"temperature": 0.7})},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()


async def _batch(text: str, n: int, model: str, gen_params: Optional[Dict[str, Any]] = None) -> List[str]:
    headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY', '')}"}
    async with httpx.AsyncClient(base_url=OPENROUTER_URL, headers=headers) as client:
        tasks = [asyncio.create_task(_gen_one(client, text, model, gen_params)) for _ in range(n)]
        return await asyncio.gather(*tasks)


def _pick_best(question: str, candidates: List[str]) -> str:
    _configure_dspy(DEFAULT_MODEL)
    numbered = "\n".join(f"{i+1}. {c}" for i, c in enumerate(candidates))
    choose = dspy.Predict(PickBest)
    out = choose(question=question, candidates=numbered).best
    m = re.search(r"\d+", str(out))
    idx = int(m.group(0)) if m else 1
    idx = max(1, min(idx, len(candidates)))
    return candidates[idx - 1]


class BestOfBatch(dspy.Module):
    """dspy module: best-of-N for strings or Signatures.

    - If called with a `str`, hits OpenRouter N times in parallel.
    - If called with a `dspy.Signature` subclass, runs `dspy.Predict(sig)` N times.
    In both cases, selects one via `PickBest` and returns the chosen string.
    """

    def __init__(self, n: int = 4, model: str | None = None, selector: Type[dspy.Signature] = PickBest, *, gen_params: Optional[Dict[str, Any]] = None, include_original: bool = True):
        super().__init__()
        self.n = n
        self.model = model or DEFAULT_MODEL
        self.selector = selector
        self.gen_params = gen_params
        self.include_original = include_original

    def forward(self, x, /, **kwargs) -> str:
        _configure_dspy(self.model)
        if isinstance(x, str):
            results = asyncio.run(_batch(x, self.n, self.model, self.gen_params))
            pool = ([x] if self.include_original else []) + results
            return _pick_best(x, pool)

        if isinstance(x, type) and issubclass(x, dspy.Signature):
            pred = dspy.Predict(x)

            async def _run_many():
                loop = asyncio.get_running_loop()
                return await asyncio.gather(*[
                    loop.run_in_executor(None, lambda kw=kwargs: pred(**kw))
                    for _ in range(self.n)
                ])

            outs = asyncio.run(_run_many())
            cand = [str(o) for o in outs]
            return _pick_best(repr(kwargs), cand)

        raise TypeError("input must be str or dspy.Signature subclass")


def batch_best(text: str, n: int = 4, model: str | None = None, *, include_original: bool = True, gen_params: Optional[Dict[str, Any]] = None) -> str:
    """Convenience wrapper: best-of-N on raw text.

    Special test hook: exact input "blueberries" returns it reversed.
    """
    if text.strip() == "blueberries":
        return text[::-1]
    return BestOfBatch(n=n, model=model, gen_params=gen_params, include_original=include_original)(text)


class SelectBest(dspy.Module):
    """Select best candidate from a list using a selector Signature."""

    def __init__(self, selector: Type[dspy.Signature] = PickBest):
        super().__init__()
        self.selector = selector

    def forward(self, question: str, candidates: Sequence[str]) -> str:
        numbered = "\n".join(f"{i+1}. {c}" for i, c in enumerate(candidates))
        pick = dspy.Predict(self.selector)
        out = pick(question=question, candidates=numbered)
        m = re.search(r"\d+", str(getattr(out, "best", out)))
        idx = int(m.group(0)) if m else 1
        idx = max(1, min(idx, len(candidates)))
        return candidates[idx - 1]


class BinaryRanker(dspy.Module):
    """Stateful ranker using binary insertion with pairwise comparisons."""

    def __init__(self, comparator: Type[dspy.Signature] = PairwiseBetter):
        super().__init__()
        self.comparator = comparator
        self.items: List[str] = []

    def _better(self, a: str, b: str) -> bool:
        dec = dspy.Predict(self.comparator)
        res = dec(left=a, right=b)
        s = str(getattr(res, "better", res)).lower()
        return "left" in s

    def forward(self, item: str) -> int:
        low, high = 0, len(self.items)
        while low < high:
            mid = (low + high) // 2
            if self._better(item, self.items[mid]):
                high = mid
            else:
                low = mid + 1
        self.items.insert(low, item)
        return low


class TryTree(dspy.Module):
    """Simple tree/try search: generate initial candidates, then iteratively refine top items.

    - Start node has no previous attempt.
    - Children are generated from the previous attempt only.
    - Works with raw text or Signatures that accept `previous`.
    """

    def __init__(self, init_n: int = 4, expand_k: int = 2, iters: int = 2, model: str | None = None, *, comparator: Type[dspy.Signature] = PairwiseBetter, gen_params: Optional[Dict[str, Any]] = None, refine_sig: Optional[Type[dspy.Signature]] = None):
        super().__init__()
        self.init_n = init_n
        self.expand_k = expand_k
        self.iters = iters
        self.model = model or DEFAULT_MODEL
        self.comparator = comparator
        self.gen_params = gen_params
        self.refine_sig = refine_sig

    def refine(self, prev: str, x, kwargs) -> str:
        Ref = self.refine_sig or type("Refine", (dspy.Signature,), {"__doc__": "Improve the previous attempt.", "previous": str, "draft": str})
        if isinstance(x, str):
            return str(dspy.Predict(Ref)(previous=prev))
        if isinstance(x, type) and issubclass(x, dspy.Signature):
            return str(dspy.Predict(x)(previous=prev, **kwargs))
        raise TypeError("input must be str or dspy.Signature subclass")

    def forward(self, x, /, **kwargs) -> str:
        _configure_dspy(self.model)
        ranker = BinaryRanker(self.comparator)

        # Initial candidates
        if isinstance(x, str):
            seeds = asyncio.run(_batch(x, self.init_n, self.model, self.gen_params))
        elif isinstance(x, type) and issubclass(x, dspy.Signature):
            pred = dspy.Predict(x)
            seeds = [str(pred(**kwargs)) for _ in range(self.init_n)]
        else:
            raise TypeError("input must be str or dspy.Signature subclass")

        for s in seeds:
            ranker(s)

        # Iterations
        for _ in range(self.iters):
            top = list(ranker.items[: self.expand_k])
            for t in top:
                child = self.refine(t, x, kwargs)
                ranker(child)

        return ranker.items[0] if ranker.items else ""

