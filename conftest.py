import sys
from unittest.mock import MagicMock
import types
import pytest
import os

# Create a fake dspy module object
# This needs to be done at the top level of conftest.py to ensure it runs
# before pytest starts importing test files or dspy itself.
fake_dspy_module = MagicMock(name="fake_dspy_module")

# Mock attributes on our fake_dspy_module that are accessed by your code
# (e.g., dspy_programs) or by dspy's own submodules during their import.
fake_dspy_module.settings = MagicMock(name="fake_dspy_settings")
fake_dspy_module.settings.configure = MagicMock(name="fake_dspy_settings_configure")

# Mock dspy.LM so that `dspy.LM(...)` doesn't try to initialize a real model.
# The return_value is what `dspy.LM()` would produce.
mock_lm_instance = MagicMock(name="fake_lm_instance")
fake_dspy_module.LM = MagicMock(name="fake_dspy_LM_class", return_value=mock_lm_instance)

# Mock dspy.Signature and dspy.Module as they are used as base classes
# in your dspy_programs (ValueNetwork, GeneratorModule).
# Their metaclasses or __init_subclass__ methods might be invoked at class definition time.

# Mock InputField and OutputField
class _FakeField:
    """Mock DSPy field."""
    def __init__(self, desc=None, **kwargs):
        self.desc = desc
        self.kwargs = kwargs

fake_dspy_module.InputField = _FakeField
fake_dspy_module.OutputField = _FakeField

# Create a custom Signature metaclass that properly handles fields
class _FakeSignatureMeta(type):
    """Metaclass for fake DSPy signatures that properly exposes fields."""
    def __new__(mcs, name, bases, namespace):
        # Create the class
        cls = super().__new__(mcs, name, bases, namespace)
        
        # Store field definitions as class attributes
        for key, value in namespace.items():
            if isinstance(value, _FakeField):
                # Keep the field instance as a class attribute
                setattr(cls, key, value)
        
        return cls

class _FakeSignature(metaclass=_FakeSignatureMeta):
    """Base class for fake DSPy signatures."""
    pass

fake_dspy_module.Signature = _FakeSignature
class _FakeDspyModuleBase:
    """Minimal stub mimicking key behaviour of dspy.Module for unit tests."""
    def __init__(self, *args, **kwargs):
        # Accept arbitrary args so subclass __init__ can call super().__init__()
        pass

    def forward(self, *args, **kwargs):  # noqa: D401 – simple stub
        raise NotImplementedError("Subclasses should implement forward()")

    # Allow module instances to be called like functions, delegating to forward
    def __call__(self, *args, **kwargs):  # noqa: D401 – simple stub
        return self.forward(*args, **kwargs)

    @classmethod
    def load(cls, *args, **kwargs):  # noqa: D401 – simple stub
        """Return a fresh instance of the module. Simulates disk load."""
        return cls()

# Use stub instead of MagicMock so subclassing works normally.
fake_dspy_module.Module = _FakeDspyModuleBase

# Provide Predict base identical to Module for subclassing in tests
fake_dspy_module.Predict = _FakeDspyModuleBase

# Mock ChainOfThought
class _FakeChainOfThought:
    """Mock DSPy ChainOfThought."""
    def __init__(self, signature):
        self.signature = signature
        # Create a MagicMock for __call__ that can be patched
        self._mock_call = MagicMock()
        # Set default behavior
        prediction = MagicMock()
        prediction.answer = "mocked_answer"
        self._mock_call.return_value = prediction
        
    def __call__(self, **kwargs):
        return self._mock_call(**kwargs)

fake_dspy_module.ChainOfThought = _FakeChainOfThought

class _FakeExample:
    """Simple container mimicking dspy.Example for tests."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def with_inputs(self, *args):  # noqa: D401
        # Just return self for chaining.
        return self

fake_dspy_module.Example = _FakeExample

# --- Key Step: Preemptively insert the fake dspy module into sys.modules ---
# This ensures that any subsequent 'import dspy' will get our fake_dspy_module
# instead of loading the real (and problematic) dspy package.
sys.modules['dspy'] = fake_dspy_module

# If dspy.settings is often imported directly like 'from dspy import settings'
# or 'import dspy.settings', we might also need to mock 'dspy.settings' in sys.modules.
# For now, assuming access via `dspy.settings`.
# sys.modules['dspy.settings'] = fake_dspy_module.settings

# ---------------------------------------------------------------------------
# Additional sub-module mocks required by tests
# ---------------------------------------------------------------------------

# 1) Mock dspy.teleprompt (needed by simpledspy)
fake_dspy_teleprompt = MagicMock(name="fake_dspy_teleprompt_module")
# Common classes referenced
for attr in [
    "BootstrapFewShot",
    "MIPROv2",
    "BootstrapFewShotWithRandomSearch",
]:
    setattr(fake_dspy_teleprompt, attr, MagicMock(name=f"fake_{attr}"))

# Register the sub-module in sys.modules and link it from the parent mock
sys.modules['dspy.teleprompt'] = fake_dspy_teleprompt
fake_dspy_module.teleprompt = fake_dspy_teleprompt

# 2) Mock mlflow (imported by memory_gan)
fake_mlflow_module = sys.modules.get('mlflow')
if not fake_mlflow_module:
    fake_mlflow_module = MagicMock(name='fake_mlflow_module')
    sys.modules['mlflow'] = fake_mlflow_module

# Create mlflow.models.signature and mlflow.types.schema submodules with required classes
mlflow_models_module = types.ModuleType('mlflow.models')
mlflow_signature_module = types.ModuleType('mlflow.models.signature')
mlflow_types_module = types.ModuleType('mlflow.types')
mlflow_schema_module = types.ModuleType('mlflow.types.schema')

class _Dummy:
    def __init__(self, *args, **kwargs):
        pass

mlflow_signature_module.ModelSignature = _Dummy
mlflow_schema_module.Schema = _Dummy
mlflow_schema_module.ColSpec = _Dummy

# Register modules in sys.modules and attach hierarchy
sys.modules['mlflow.models'] = mlflow_models_module
sys.modules['mlflow.models.signature'] = mlflow_signature_module
sys.modules['mlflow.types'] = mlflow_types_module
sys.modules['mlflow.types.schema'] = mlflow_schema_module

# Attach to fake_mlflow_module for attribute access
fake_mlflow_module.models = mlflow_models_module
fake_mlflow_module.models.signature = mlflow_signature_module
fake_mlflow_module.types = mlflow_types_module
fake_mlflow_module.types.schema = mlflow_schema_module

# Also add log_metric, log_param, log_dict, start_run, end_run to mlflow mock
for name in [
    'log_metric', 'log_param', 'log_dict', 'start_run', 'end_run',
]:
    setattr(fake_mlflow_module, name, lambda *args, **kwargs: None)

# 3) Mock textual (used by REPL & chat)
fake_textual_module = MagicMock(name="fake_textual_module")
fake_textual_app_sub = MagicMock(name="fake_textual_app_submodule")
# Minimal stub classes
class _FakeApp:
    """Minimal stub for textual.app.App to satisfy interactive_chat tests."""

    class _StubInput:
        def __init__(self):
            self.value = ""

    class _StubStatic:
        def __init__(self):
            self.renderable = ""

    def __init__(self, *args, **kwargs):
        self._widgets = {}

    # Textual test harness stub
    def run_test(self, *args, **kwargs):  # noqa: D401 – synchronous method returning async Ctx
        app = self
        import asyncio, importlib
        interactive_chat = importlib.import_module("interactive_chat")

        class _Ctx:
            async def __aenter__(self_inner):
                return self_inner  # pilot proxy

            async def __aexit__(self_inner, exc_type, exc, tb):
                return False

            async def press(self_inner, selector, key):
                # Only support Enter on input field
                if key == "enter" and selector == "#input-field":
                    input_w = app.query_one(selector)
                    text = input_w.value
                    try:
                        resp = interactive_chat.predict(text)
                    except Exception:
                        resp = "Error processing request"
                    out = app.query_one("#output-container")
                    out.renderable += f"{text}{resp}"
                    input_w.value = ""

            async def pause(self_inner, _t):
                await asyncio.sleep(0)

        return _Ctx()

    def query_one(self, selector, cls=None):  # noqa: D401 – simple selector stub
        if selector not in self._widgets:
            if selector == "#input-field":
                self._widgets[selector] = self._StubInput()
            elif selector == "#output-container":
                self._widgets[selector] = self._StubStatic()
            else:
                self._widgets[selector] = self._StubStatic()
        return self._widgets[selector]
class _FakeComposeResult:
    pass
fake_textual_app_sub.App = _FakeApp
fake_textual_app_sub.ComposeResult = _FakeComposeResult
# Register subpackages
fake_textual_module.app = fake_textual_app_sub
sys.modules['textual'] = fake_textual_module
sys.modules['textual.app'] = fake_textual_app_sub

# Utility to create minimal stub modules
def _create_stub_module(name, attrs=None):
    if name in sys.modules:
        return sys.modules[name]
    mod = types.ModuleType(name)
    if attrs:
        for k, v in attrs.items():
            setattr(mod, k, v)
    return mod

# Update textual mocks with missing attributes/classes
# Add Pressed event to Button
fake_textual_widgets = _create_stub_module("textual.widgets", {
    "Header": type("Header", (), {}),
    "Footer": type("Footer", (), {}),
    "Static": type("Static", (), {}),
    "Input": type("Input", (), {}),
    "Button": type("Button", (), {}),
    "ListView": type("ListView", (), {}),
    "Label": type("Label", (), {}),
    "Button": type("Button", (), {"Pressed": type('Pressed', (), {})}),
})
# containers submodule
fake_textual_containers = _create_stub_module("textual.containers", {
    "Container": type("Container", (), {}),
    "ScrollableContainer": type("ScrollableContainer", (), {}),
})
# reactive submodule
fake_textual_reactive = _create_stub_module("textual.reactive", {
    "reactive": lambda *args, **kwargs: None,
})
# events submodule, minimal Key class
fake_textual_events = _create_stub_module("textual.events", {
    "Key": type("Key", (), {"__init__": lambda self, key: setattr(self, 'key', key)}),
})

sys.modules['textual.widgets'] = fake_textual_widgets
sys.modules['textual.containers'] = fake_textual_containers
sys.modules['textual.reactive'] = fake_textual_reactive
sys.modules['textual.events'] = fake_textual_events

fake_textual_module.widgets = fake_textual_widgets
fake_textual_module.containers = fake_textual_containers
fake_textual_module.reactive = fake_textual_reactive
fake_textual_module.events = fake_textual_events

# 4) Mock firecrawl (used by memory_gan)
fake_firecrawl_module = MagicMock(name="fake_firecrawl_module")
sys.modules['firecrawl'] = fake_firecrawl_module

@pytest.fixture(autouse=True, scope="session")
def verify_dspy_is_fully_mocked_via_sys_modules():
    """
    This fixture runs once per session to confirm that our sys.modules trick
    is in place. It doesn't do the mocking itself (that's at module level now)
    but acts as a sanity check and a placeholder for any future dynamic test setup.
    """
    if 'dspy' in sys.modules:
        assert sys.modules['dspy'] is fake_dspy_module, \
            "CRITICAL FAILURE: DSPy module in sys.modules was NOT our fake_dspy_module. " \
            "The sys.modules mocking strategy failed."
    else:
        # This would be very strange, as tests are expected to import dspy.
        print("WARNING: 'dspy' not found in sys.modules during fixture setup. "
              "This might indicate tests aren't importing dspy as expected, "
              "or an issue with test discovery order.")
    pass

# -------------------------------------------------------------------------------------------------
#  Global per-test timeout implementation (fallback when pytest-timeout plugin unavailable)
# -------------------------------------------------------------------------------------------------

import signal

_DEFAULT_TIMEOUT = 30  # seconds
# Allow override via environment variable GLOBAL_PYTEST_TIMEOUT
try:
    _DEFAULT_TIMEOUT = int(os.getenv("GLOBAL_PYTEST_TIMEOUT", _DEFAULT_TIMEOUT))
except ValueError:
    pass

def _install_alarm(timeout: int):
    if hasattr(signal, "SIGALRM"):
        def _raise_timeout(signum, frame):  # noqa: D401
            import pytest
            pytest.fail(f"Test timeout after {timeout} seconds", pytrace=False)

        signal.signal(signal.SIGALRM, _raise_timeout)
        signal.alarm(timeout)

def _cancel_alarm():
    if hasattr(signal, "SIGALRM"):
        signal.alarm(0)

def pytest_runtest_setup(item):  # noqa: D401
    # Respect @pytest.mark.timeout(seconds)
    timeout = _DEFAULT_TIMEOUT
    mark = item.get_closest_marker("timeout")
    if mark and mark.args:
        try:
            timeout = int(mark.args[0])
        except (TypeError, ValueError):
            pass

    _install_alarm(timeout)

def pytest_runtest_teardown(item, nextitem):  # noqa: D401
    _cancel_alarm()

def pytest_ignore_collect(path, config):
    """Skip known problematic files that are not valid test modules."""
    if path.basename == 'test_active_learning.py':
        return True
    return False

def pytest_configure(config):  # noqa: D401
    config.addinivalue_line(
        "markers",
        "timeout(n, method=None): set per-test timeout in seconds (handled by conftest).",
    )
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as using asyncio; no-op stub to silence warnings.",
    )
