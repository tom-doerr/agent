import dspy
import mlflow
import os
import sys
import firecrawl
from dspy.teleprompt import SIMBA
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import Schema, ColSpec
import time

def get_firecrawl_content(url):
    """Scrape a URL using Firecrawl and return the content."""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set")
    app = firecrawl.FirecrawlApp(api_key=api_key)
    try:
        result = app.scrape_url(url, options={'pageOptions': {'onlyMainContent': True}})
        return result.get('content', '') if isinstance(result, dict) else str(result)
    except Exception as e:
        print(f"Firecrawl error: {e}")
        return ""

# === GLOBAL CONFIGURATIONS & DEFINITIONS ===

# --- LLM Configuration ---
LLM_MODEL_NAME = "deepseek/deepseek-chat" # Or your preferred model
LLM = dspy.LM(
    model=LLM_MODEL_NAME,
    max_tokens=1000, # Increased max_tokens for potentially complex generation/answers
    temperature=0.7,
    cache=False # Start with cache off for more realistic optimization
)
dspy.settings.configure(lm=LLM)


# === DSPy Signatures ===

class GenerateChallengingQuestion(dspy.Signature):
    """Given a source text, generate a challenging question that is answerable from the text but might be difficult for a system relying solely on its memory or a general understanding, rather than direct access to the text for answering this specific question."""
    source_text = dspy.InputField(desc="The source text to generate a question from.")
    challenging_question = dspy.OutputField(desc="A question designed to be hard for a memory-based system but answerable from the source text.")

class AnswerFromMemory(dspy.Signature):
    """Answer the given question based *only* on your general knowledge and information you have 'memorized' or internalized previously. Do NOT use any specific provided source text to answer this current question, even if it seems relevant. Act as if you are recalling information.
    If you do not know the answer from your memory, indicate that clearly."""
    question = dspy.InputField(desc="The question to answer from memory.")
    answer = dspy.OutputField(desc="The answer based on 'memorized' information.")

class AnswerFromSource(dspy.Signature):
    """Answer the given question based *directly* on the provided source text."""
    source_text = dspy.InputField(desc="The source text containing the answer.")
    question = dspy.InputField(desc="The question to answer.")
    answer = dspy.OutputField(desc="The answer derived directly from the source text.")

# === DSPy Modules ===

class QuestionGenerator(dspy.Predict):
    def __init__(self):
        super().__init__(GenerateChallengingQuestion)

class MemoryModule(dspy.Predict):
    def __init__(self):
        super().__init__(AnswerFromMemory)

class ReferenceModule(dspy.Predict):
    def __init__(self):
        super().__init__(AnswerFromSource)

# === Main MemoryGAN Module ===

class MemoryGAN(dspy.Module):
    def __init__(self):
        super().__init__()
        self.question_generator = QuestionGenerator()
        self.memory_module = MemoryModule()
        self.reference_module = ReferenceModule()

    def forward(self, source_text):
        # 1. Generate a challenging question
        pred_question = self.question_generator(source_text=source_text)
        question = pred_question.challenging_question

        # 2. Memory module attempts to answer
        pred_memory_answer = self.memory_module(question=question)
        memory_answer = pred_memory_answer.answer

        # 3. Reference module provides the gold answer
        pred_reference_answer = self.reference_module(source_text=source_text, question=question)
        reference_answer = pred_reference_answer.answer

        # Attach all parts to the prediction for the metric function
        # Also, include the original source_text in the prediction for the metric if needed
        return dspy.Prediction(
            source_text=source_text, # Pass along for metric evaluation
            question=question,
            memory_answer=memory_answer,
            reference_answer=reference_answer
        )

# === SIMBA Metric Function (Placeholder - Needs Implementation) ===

# This will likely require an LLM as a judge
class AssessAnswers(dspy.Signature):
    """Given a source text, a question, a reference answer (derived from source text), 
    and a memory-based answer, provide a numerical score (0.0 to 1.0) based on:
    1. Validity: Is the reference answer correct and derived from the source text? (0.5 if yes, 0.0 if no)
    2. Stumping: Is the memory answer incorrect or significantly different from the reference? (0.5 if yes, 0.0 if no)
    Total score = Validity + Stumping.
    Only output the numerical score.
    """
    source_text = dspy.InputField()
    question = dspy.InputField()
    reference_answer = dspy.InputField()
    memory_answer = dspy.InputField()
    assessment_score = dspy.OutputField(desc="A numerical score from 0.0 to 1.0")

def gan_metric(example, pred, trace=None):
    try:
        # Extract components from prediction
        source_text = pred.source_text
        question = pred.question
        reference_answer = pred.reference_answer
        memory_answer = pred.memory_answer

        # Skip if any component is missing
        if not all([source_text, question, reference_answer, memory_answer]):
            return 0.0

        # Get assessment from judge
        assessment = dspy.Predict(AssessAnswers)(
            source_text=source_text,
            question=question,
            reference_answer=reference_answer,
            memory_answer=memory_answer
        )
        
        # Parse score safely
        score = float(assessment.assessment_score)
        return max(0.0, min(1.0, score))  # Clamp to [0.0, 1.0]
    except Exception as e:
        print(f"Error in gan_metric: {e}")
        return 0.0

# Optimization function
def optimize_memory_gan(trainset):
    # Configure SIMBA with increased steps and demos
    # Detect if running in pytest and reduce steps
    max_steps = 2 if 'pytest' in sys.modules else 12
    
    simba_optimizer = SIMBA(
        metric=gan_metric,
        max_steps=max_steps,
        max_demos=4,
        bsize=2
    )
    return simba_optimizer.compile(MemoryGAN(), trainset=trainset)

# Main function for testing
def main():
    """Main function for testing MemoryGAN"""
    print("MemoryGAN module loaded successfully")
