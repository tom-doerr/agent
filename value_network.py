import dspy

class ValueNetworkSignature(dspy.Signature):
    """Predict the score and uncertainty for a given data point."""
    data_point = dspy.InputField(desc="A data point to be evaluated.")
    score = dspy.OutputField(desc="Predicted score (float between 0.0 and 1.0)")
    uncertainty = dspy.OutputField(desc="Predicted uncertainty (float between 0.0 and 1.0)")

class ValueNetwork(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ValueNetworkSignature)

    def forward(self, data_point):
        return self.predict(data_point=data_point)
