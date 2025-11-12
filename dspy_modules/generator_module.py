import dspy

class GeneratorSignature(dspy.Signature):
    """Generate a data point for evaluation."""
    topic = dspy.InputField(desc="Topic for data point generation.")
    data_point = dspy.OutputField(desc="Generated data point.")

class GeneratorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(GeneratorSignature)

    def forward(self, topic):
        return self.generate(topic=topic)

# Optimization function
def optimize_generator(trainset):
    optimizer = dspy.SIMBA(
        metric=lambda example, pred, trace=None: 1.0 if pred.data_point else 0.0,
        max_steps=12,
        max_demos=10
    )
    return optimizer.compile(GeneratorModule(), trainset=trainset)
