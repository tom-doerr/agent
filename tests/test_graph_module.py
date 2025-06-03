import dspy
from graph_module import GraphOrchestrator


class MockGraphModule(dspy.Module):
    def __init__(self, fixed_output):
        super().__init__()
        self.fixed_output = fixed_output

    def forward(self, system_context, data, notes):
        return dspy.Prediction(
            next_module=str(self.fixed_output["next_module"]),
            updated_data=self.fixed_output["updated_data"],
            updated_notes=self.fixed_output["updated_notes"],
        )


def test_graph_orchestration():
    # Create mock modules
    mock_modules = [
        MockGraphModule(
            {"next_module": 1, "updated_data": "data1", "updated_notes": "notes1"}
        ),
        MockGraphModule(
            {"next_module": 2, "updated_data": "data2", "updated_notes": "notes2"}
        ),
        MockGraphModule(
            {
                "next_module": 0,
                "updated_data": "final_data",
                "updated_notes": "final_notes",
            }
        ),
    ]

    # Create orchestrator with mock modules
    orchestrator = GraphOrchestrator(num_modules=3, max_steps=3)
    orchestrator.modules = mock_modules

    # Execute
    result = orchestrator(initial_data="initial_data")

    # Verify outputs
    assert result.final_data == "final_data"
    assert result.final_notes == "final_notes"


def test_module_cycling():
    mock_modules = [
        MockGraphModule(
            {"next_module": 1, "updated_data": "data", "updated_notes": "notes"}
        ),
        MockGraphModule(
            {"next_module": 0, "updated_data": "data", "updated_notes": "notes"}
        ),
    ]

    orchestrator = GraphOrchestrator(num_modules=2, max_steps=5)
    orchestrator.modules = mock_modules

    result = orchestrator(initial_data="initial_data")
    assert result.final_data == "data"
    assert result.final_notes == "notes"


def test_step_limiting():
    mock_modules = [
        MockGraphModule(
            {
                "next_module": 0,
                "updated_data": "data_0",
                "updated_notes": "notes_0",
            }
        ),
        MockGraphModule(
            {
                "next_module": 0,
                "updated_data": "data_1",
                "updated_notes": "notes_1",
            }
        ),
        MockGraphModule(
            {
                "next_module": 0,
                "updated_data": "data_2",
                "updated_notes": "notes_2",
            }
        ),
    ]

    orchestrator = GraphOrchestrator(num_modules=3, max_steps=2)
    orchestrator.modules = mock_modules

    result = orchestrator(initial_data="initial_data")
    assert result.final_data == "data_0"
    assert result.final_notes == "notes_0"
