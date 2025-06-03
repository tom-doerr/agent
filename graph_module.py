import dspy


class GraphModuleSignature(dspy.Signature):
    """Process data within a graph of modules. Each module decides next step."""

    system_context = dspy.InputField(
        desc="Context: num_modules, max_steps, current_step"
    )
    data = dspy.InputField(desc="Main data being processed")
    notes = dspy.InputField(desc="Additional notes passed between modules")
    next_module = dspy.OutputField(
        desc="Index of next module to execute (0 to num_modules-1)"
    )
    updated_data = dspy.OutputField(desc="Updated data after processing")
    updated_notes = dspy.OutputField(desc="Updated notes after processing")


class GraphModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.process = dspy.ChainOfThought(GraphModuleSignature)

    def forward(self, system_context, data, notes):
        return self.process(system_context=system_context, data=data, notes=notes)


class GraphOrchestrator(dspy.Module):
    def __init__(self, num_modules, max_steps):
        super().__init__()
        self.num_modules = num_modules
        self.max_steps = max_steps
        self.modules = [GraphModule() for _ in range(num_modules)]

    def forward(self, initial_data):
        current_module = 0
        current_step = 0
        notes = ""
        data = initial_data

        while current_step < self.max_steps:
            context = (
                f"num_modules={self.num_modules} "
                f"max_steps={self.max_steps} "
                f"current_step={current_step}"
            )

            result = self.modules[current_module](
                system_context=context, data=data, notes=notes
            )

            data = result.updated_data
            notes = result.updated_notes
            try:
                next_module = int(result.next_module) % self.num_modules
            except ValueError:
                next_module = 0

            # Break early if next_module is 0
            if next_module == 0:
                break

            current_module = next_module
            current_step += 1

        return dspy.Prediction(final_data=data, final_notes=notes)
