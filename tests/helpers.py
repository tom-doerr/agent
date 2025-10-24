import sys
import types
import importlib
from contextlib import contextmanager


def install_fake_dspy(best_choice: int = 1):
    m = types.ModuleType("dspy")

    class Signature:  # minimal base
        pass

    class Module:  # minimal base with call-through
        def __call__(self, *a, **kw):
            if hasattr(self, "forward"):
                return self.forward(*a, **kw)
            raise TypeError("module not callable: missing forward()")

    class OpenAI:  # constructor only; no network
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    def configure(lm=None):  # record configured LM
        m._configured = lm

    m.best_choice = best_choice
    m._calls = []  # (sig, kwargs) for non-PickBest
    m._configured = None

    class Predict:
        def __init__(self, sig):
            self.sig = sig

        def __call__(self, **kwargs):
            if getattr(self.sig, "__name__", "") == "PickBest":
                class Obj:
                    def __init__(self, v):
                        self.best = v

                return Obj(m.best_choice)
            if getattr(self.sig, "__name__", "") == "PairwiseBetter":
                left, right = kwargs.get("left", ""), kwargs.get("right", "")
                better = "left" if str(left) > str(right) else "right"
                class Obj:
                    def __init__(self, b):
                        self.better = b
                return Obj(better)
            # record and return a printable object
            idx = len(m._calls)
            m._calls.append((self.sig, kwargs))

            class Out:
                def __str__(self):
                    if "previous" in kwargs:
                        return f"{kwargs['previous']}+"
                    return "BASE"

            return Out()

    m.Signature = Signature
    m.Module = Module
    m.Predict = Predict
    m.OpenAI = OpenAI
    m.configure = configure

    sys.modules["dspy"] = m
    # Provide a tiny httpx stub if missing (tests never call it)
    if "httpx" not in sys.modules:
        httpx = types.ModuleType("httpx")

        class AsyncClient:
            def __init__(self, *a, **kw):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *exc):
                return False

            async def post(self, *a, **kw):
                class Resp:
                    def raise_for_status(self):
                        pass

                    def json(self):
                        return {"choices": [{"message": {"content": "stub"}}]}

                return Resp()

        httpx.AsyncClient = AsyncClient
        sys.modules["httpx"] = httpx
    return m


@contextmanager
def fresh_pkg():
    for name in [
        "deepseek_batch",
        "deepseek_batch.cli",
    ]:
        sys.modules.pop(name, None)
    try:
        yield
    finally:
        for name in [
            "deepseek_batch",
            "deepseek_batch.cli",
        ]:
            sys.modules.pop(name, None)


def import_pkg():
    import os
    root = os.path.dirname(os.path.dirname(__file__))
    src = os.path.join(root, "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    return importlib.import_module("deepseek_batch")
