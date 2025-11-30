"""DSPy modules for hill climb learning."""
import dspy


class ModifyText(dspy.Signature):
    """Improve the given text while preserving its core meaning."""
    original: str = dspy.InputField(desc="The original text to improve")
    modified: str = dspy.OutputField(desc="An improved version of the text")


class EvaluateText(dspy.Signature):
    """Determine if the modified text is better than the original."""
    original: str = dspy.InputField(desc="The original text")
    modified: str = dspy.InputField(desc="The modified text")
    is_better: bool = dspy.OutputField(desc="True if modified is better")


class TextModifier(dspy.Module):
    """Generates improved versions of text."""

    def __init__(self):
        super().__init__()
        self.modify = dspy.Predict(ModifyText)

    def forward(self, original: str) -> dspy.Prediction:
        return self.modify(original=original)


class TextEvaluator(dspy.Module):
    """Evaluates if a modification is an improvement."""

    def __init__(self):
        super().__init__()
        self.evaluate = dspy.Predict(EvaluateText)

    def forward(self, original: str, modified: str) -> dspy.Prediction:
        return self.evaluate(original=original, modified=modified)
