import dspy
import json

class ValueNetworkSignature(dspy.Signature):
    """Predict the score and uncertainty for a given data point. Output a JSON string with 'score' and 'uncertainty' keys."""
    data_point = dspy.InputField(desc="A data point to be evaluated.")
    json_output = dspy.OutputField(desc="JSON string containing 'score' (float) and 'uncertainty' (float)")

class ValueNetwork(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.ChainOfThought(ValueNetworkSignature)

    def forward(self, data_point):
        prediction = self.predict(data_point=data_point)
        try:
            output_dict = json.loads(prediction.json_output)
            return dspy.Prediction(
                score=str(output_dict['score']),
                uncertainty=str(output_dict['uncertainty'])
        except Exception as e:
            print(f"Error parsing JSON output: {e}")
            print(f"Raw output: {prediction.json_output}")
            return dspy.Prediction(score="0.5", uncertainty="0.5")
