import dspy

class ValueNetworkSignature(dspy.Signature):
    """Predict the score and uncertainty for a given data point."""
    data_point = dspy.InputField(desc="A data point to be evaluated.")
    context = dspy.InputField(desc="Context about scoring criteria.")
    score = dspy.OutputField(desc="Predicted score (float between 0.0 and 1.0)")
    uncertainty = dspy.OutputField(desc="Predicted uncertainty (float between 0.0 and 1.0)")

class ValueNetwork(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.ChainOfThought(ValueNetworkSignature)
        self.scoring_context = "Score based on relevance, accuracy, and usefulness"

    def forward(self, data_point):
        prediction = self.predict(
            data_point=data_point, 
            context=self.scoring_context
        )
        try:
            # Try to convert to floats immediately
            score = min(1.0, max(0.0, float(prediction.score)))
            uncertainty = min(1.0, max(0.0, float(prediction.uncertainty)))
        except (TypeError, ValueError):
            # Use safe defaults on conversion failure
            score = 0.5
            uncertainty = 1.0
        
        return dspy.Prediction(
            score=score,
            uncertainty=uncertainty
        )
