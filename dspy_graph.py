import dspy

class NodeSignature(dspy.Signature):
    """Process data in a graph node and determine next step."""
    system_context = dspy.InputField(desc="Num modules, current step, max steps")
    data = dspy.InputField(desc="Input data for processing")
    notes = dspy.InputField(desc="Additional context notes")
    
    next_module = dspy.OutputField(desc="Index (0-N) of next module to run")
    output_data = dspy.OutputField(desc="Processed output data")
    output_notes = dspy.OutputField(desc="Updated context notes")

class NodeModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.process = dspy.Predict(NodeSignature)
    
    def forward(self, system_context, data, notes):
        return self.process(
            system_context=system_context,
            data=data,
            notes=notes
        )

class GraphModule(dspy.Module):
    def __init__(self, num_modules=3, max_steps=5):
        super().__init__()
        self.num_modules = num_modules
        self.max_steps = max_steps
        self.nodes = [NodeModule() for _ in range(num_modules)]
    
    @staticmethod
    def format_context(num_modules, current_step, max_steps):
        return f"{num_modules} modules, step {current_step}/{max_steps}"
    
    def forward(self, data, notes=""):
        current_step = 0
        current_node = 0
        
        while current_step < self.max_steps:
            context = self.format_context(
                self.num_modules, current_step, self.max_steps
            )
            
            result = self.nodes[current_node](
                system_context=context,
                data=data,
                notes=notes
            )
            
            data = result.output_data
            notes = result.output_notes
            current_node = int(result.next_module)
            current_step += 1
            
            # Validate module index
            if current_node < 0 or current_node >= self.num_modules:
                current_node = 0
        
        return data
