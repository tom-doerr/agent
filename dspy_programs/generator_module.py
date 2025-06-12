import dspy
import random
import numpy as np

class GeneratorSignature(dspy.Signature):
    """Generate a diverse data point for evaluation."""
    topic = dspy.InputField(desc="Topic for data point generation.")
    context = dspy.InputField(desc="Context to ensure diversity.")
    data_point = dspy.OutputField(desc="Generated data point.")

class GeneratorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self._generate_model = None
        self.contexts = []

    @property
    def generate_model(self):
        if self._generate_model is None:
            self._generate_model = dspy.ChainOfThought(GeneratorSignature)
        return self._generate_model

    def forward(self, topic):
        # Create context based on previous generations
        context = self._create_context()
        result = self.generate_model(topic=topic, context=context)
        
        # Update context for next generation
        self.contexts.append(result.data_point)
        if len(self.contexts) > 5:
            self.contexts.pop(0)
            
        return result

    def _create_context(self):
        if not self.contexts:
            return "No previous context"
            
        # Select 2 random previous contexts
        sample = random.sample(self.contexts, min(2, len(self.contexts)))
        return "Avoid similar to: " + ", ".join(sample)
