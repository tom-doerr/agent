
from __future__ import annotations
from typing import List, Tuple
import math

def cursor_row_key(table) -> str | None:
    # Support multiple Textual versions
    if hasattr(table, "cursor_row_key"):
        return table.cursor_row_key
    return getattr(table, "cursor_row", None)

def cursor_row_index(table) -> int | None:
    rk = cursor_row_key(table)
    if rk is None:
        return None
    keys = list(table.rows.keys())
    try:
        return keys.index(rk)
    except ValueError:
        return None

def topk_sorted(weights: List[Tuple[str, float]], k: int = 5) -> List[Tuple[str, float]]:
    return sorted(weights, key=lambda x: x[1], reverse=True)[:k]

def kl_divergence(p: List[float], q: List[float], eps: float = 1e-12) -> float:
    # KL(p||q) = sum p_i log(p_i/q_i)
    s = 0.0
    for pi, qi in zip(p, q):
        pi = max(pi, eps)
        qi = max(qi, eps)
        s += pi * math.log(pi/qi)
    return s

def gini(x: List[float], eps: float = 1e-12) -> float:
    # Gini coefficient [0,1]
    n = len(x)
    if n == 0:
        return 0.0
    xs = sorted(max(v, eps) for v in x)
    cum = 0.0
    for i, v in enumerate(xs, 1):
        cum += i * v
    total = sum(xs)
    if total <= 0:
        return 0.0
    return (2*cum)/(n*total) - (n+1)/n
