import dspy
import random

class GeneratorSignature(dspy.Signature):
    """Generate a data point for evaluation."""
    topic = dspy.InputField(desc="Topic for data point generation.")
    data_point = dspy.OutputField(desc="Generated data point.")

class GeneratorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(GeneratorSignature)

    def forward(self, topic):
        return self.generate(topic=topic)
