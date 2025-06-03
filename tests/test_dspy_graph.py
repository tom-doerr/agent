import pytest
import dspy
from unittest.mock import MagicMock
from dspy_graph import GraphModule, NodeModule

class TestDSPyGraph:
    @pytest.fixture
    def mock_lm(self, monkeypatch):
        mock_lm = MagicMock()
        monkeypatch.setattr("dspy.settings.configure", MagicMock(return_value=mock_lm))
        return mock_lm

    def test_node_module_forward(self, mock_lm):
        node = NodeModule()
        result = node(system_context="3 modules, step 1/5", data="input", notes="")
        
        assert "next_module" in result
        assert "output_data" in result
        assert "output_notes" in result

    def test_graph_execution(self, mock_lm):
        graph = GraphModule(num_modules=3, max_steps=5)
        final_data = graph(data="start", notes="initial")
        
        assert isinstance(final_data, str)
        assert "Step 0" in final_data or "Final" in final_data

    def test_system_context_format(self):
        context = GraphModule.format_context(3, 1, 5)
        assert context == "3 modules, step 1/5"
