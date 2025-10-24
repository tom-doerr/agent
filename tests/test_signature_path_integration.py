from tests.helpers import install_fake_dspy, fresh_pkg, import_pkg
import types


def test_signature_path_runs_n_times_and_returns_one_output():
    fake = install_fake_dspy(best_choice=1)
    with fresh_pkg():
        m = import_pkg()
        dspy = __import__("dspy")

        class ToySig(dspy.Signature):
            pass

        # avoid threadpool by patching get_running_loop
        class _FakeLoop:
            def run_in_executor(self, executor, fn):
                async def _coro():
                    return fn()
                return _coro()

        m.asyncio.get_running_loop = lambda: _FakeLoop()  # type: ignore

        bo = m.BestOfBatch(n=2)
        result = bo(ToySig, foo="bar")
        assert isinstance(result, str) and result != ""
        assert len(dspy._calls) == 2  # two Predict calls for ToySig
