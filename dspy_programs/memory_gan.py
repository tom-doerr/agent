"""
DSPy program to implement a 'Memory GAN' like system.

- QuestionGenerator: Creates challenging questions from source_text.
- MemoryModule: Answers questions based on 'internalized' knowledge (tries to mimic memory).
- ReferenceModule: Answers questions with full access to source_text (oracle).

SIMBA will optimize these jointly to make the QuestionGenerator good at stumping the MemoryModule
while ensuring questions are valid (answerable by ReferenceModule).
"""

import dotenv
dotenv.load_dotenv()

import dspy
import mlflow
import os
import sys
import firecrawl
from dspy.teleprompt import SIMBA
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
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
    Output only the numerical score without any additional text.
    """
    source_text = dspy.InputField()
    question = dspy.InputField()
    reference_answer = dspy.InputField()
    memory_answer = dspy.InputField()
    assessment_score = dspy.OutputField(desc="A numerical score from 0.0 to 1.0. Output only the number.")

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
        
        # Parse score safely with better error handling
        try:
            # Extract first number from string using split
            num_str = assessment.assessment_score.split()[0]
            score = float(num_str)
            return max(0.0, min(1.0, score))  # Clamp to [0.0, 1.0]
        except (ValueError, TypeError) as e:
            print(f"Failed to parse assessment_score: '{assessment.assessment_score}' - {e}")
            return 0.0
    except Exception as e:
        print(f"Error in gan_metric: {e}")
        # Log the full traceback for debugging
        import traceback
        traceback.print_exc()
        return 0.0

# === Training Data ===
# Each example is just a source text. The 'inputs' for the MemoryGAN module is 'source_text'.
trainset = [
    dspy.Example(source_text="The Eiffel Tower, located in Paris, France, was completed in 1889. It was designed by Gustave Eiffel and is one of the most recognizable landmarks in the world. Initially criticized by some of France's leading artists and intellectuals for its design, it has since become a global cultural icon of France and one of the most recognizable structures in the world. The tower is 330 metres (1,083 ft) tall, about the same height as an 81-storey building, and is the tallest structure in Paris. Its base is square, measuring 125 metres (410 ft) on each side.").with_inputs("source_text"),
    dspy.Example(source_text="Photosynthesis is a process used by plants, algae, and certain bacteria to convert light energy into chemical energy, through a process that uses sunlight, water, and carbon dioxide. This chemical energy is stored in carbohydrate molecules, such as sugars, which are synthesized from carbon dioxide and water. Oxygen is also released as a byproduct. Most plants, most algae, and cyanobacteria perform photosynthesis; such organisms are called photoautotrophs. Photosynthesis is largely responsible for producing and maintaining the oxygen content of the Earth's atmosphere, and supplies most of the energy necessary for life on Earth.").with_inputs("source_text"),
    dspy.Example(source_text="Quantum computing uses quantum-mechanical phenomena like superposition and entanglement to perform computation. Qubits can exist in multiple states simultaneously, enabling quantum computers to solve certain problems much faster than classical computers. However, qubits are fragile and require extremely cold temperatures to maintain their quantum states.").with_inputs("source_text"),
    dspy.Example(source_text="The human brain contains approximately 86 billion neurons, each connected to thousands of other neurons through synapses. This complex network enables processes like learning, memory, and consciousness. Neuroplasticity allows the brain to reorganize itself by forming new neural connections throughout life.").with_inputs("source_text"),
]

def optimize_memory_gan(trainset, max_steps=12, max_demos=4, bsize=2):
    program_to_optimize = MemoryGAN()
    simba_optimizer = SIMBA(
        metric=gan_metric,
        max_steps=max_steps,
        max_demos=max_demos,
        bsize=bsize
    )
    optimized_program = simba_optimizer.compile(program_to_optimize, trainset=trainset)
    return optimized_program

# === Main Optimization Workflow ===
def main():
    print("--- Starting MemoryGAN SIMBA Optimization ---", flush=True)
    
    # --- MLflow Experiment Setup ---
    MLFLOW_EXPERIMENT_NAME = "DSPy_MemoryGAN_Opt"
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    
    # Configure SIMBA with increased steps and demos
    # Detect if running in pytest and reduce steps
    max_steps = 2 if 'pytest' in sys.modules else 12
    
    optimized_program = optimize_memory_gan(
        trainset, 
        max_steps=max_steps,
        max_demos=4,
        bsize=2
    )

    with mlflow.start_run(run_name="SIMBA_MemoryGAN_Run") as _run:
        mlflow.log_params({
            "llm_model_name": LLM_MODEL_NAME,
            "simba_max_steps": max_steps,
            "simba_max_demos": 4,
            "num_train_examples": len(trainset),
            "optimization_type": "SIMBA",
            "target_metric": "GAN_score"
        })

        if optimized_program:
            print("--- SIMBA Compilation Finished ---", flush=True)
            mlflow.set_tag("simba_compilation_status", "Success")
            mlflow.log_metric("optimization_completed", 1)
        else:
            mlflow.set_tag("simba_compilation_status", "Failed")

        # Create harder validation set with Firecrawl only if API key is available
        validation_set = []
        if os.getenv("FIRECRAWL_API_KEY"):
            try:
                print("\nCreating Firecrawl validation set...", flush=True)
                validation_set = [
                    dspy.Example(source_text=get_firecrawl_content("https://en.wikipedia.org/wiki/List_of_unusual_animals")).with_inputs("source_text"),
                    dspy.Example(source_text=get_firecrawl_content("https://en.wikipedia.org/wiki/List_of_emerging_technologies")).with_inputs("source_text"),
                    dspy.Example(source_text=get_firecrawl_content("https://en.wikipedia.org/wiki/List_of_minor_planets")).with_inputs("source_text")
                ]
                print("Firecrawl validation set created.", flush=True)
            except Exception as e:
                print(f"Error creating Firecrawl validation set: {e}", flush=True)
                mlflow.log_param("firecrawl_validation_error", str(e))
        else:
            print("FIRECRAWL_API_KEY not set. Skipping Firecrawl validation set.", flush=True)
            mlflow.log_param("firecrawl_validation_status", "skipped")

        if validation_set and optimized_program:
            print("\n--- Validation Results ---", flush=True)
            total_score = 0
            valid_count = 0
            all_predictions = []  # Store all predictions for later logging
            for i, example in enumerate(validation_set):
                try:
                    if not example.source_text or not example.source_text.strip():
                        print(f"Skipping validation example {i+1}: empty source_text", flush=True)
                        mlflow.log_metric(f"validation_example_{i+1}_skipped", 1)
                        continue
                        
                    prediction = optimized_program(source_text=example.source_text)
                    all_predictions.append(prediction)  # Store prediction
                    score = gan_metric(example, prediction)
                    total_score += score
                    valid_count += 1
            
                    print(f"\nValidation Example {i+1}:", flush=True)
                    print(f"  Source: {example.source_text[:100]}{'...' if len(example.source_text) > 100 else ''}", flush=True)
                    print(f"  Question: {prediction.question[:100]}{'...' if len(prediction.question) > 100 else ''}", flush=True)
                    print(f"  Memory Answer: {prediction.memory_answer[:50]}{'...' if len(prediction.memory_answer) > 50 else ''}", flush=True)
                    print(f"  Reference Answer: {prediction.reference_answer[:50]}{'...' if len(prediction.reference_answer) > 50 else ''}", flush=True)
                    print(f"  Score: {score:.2f}", flush=True)
                    
                    # Log individual validation scores
                    try:
                        mlflow.log_metric(f"validation_example_{i+1}_score", score)
                    except Exception as e:
                        print(f"Failed to log example score to MLflow: {e}")
                except Exception as e:
                    print(f"Validation failed for example {i+1}: {e}", flush=True)
                    # Log the specific error for debugging
                    print(f"  Error details: {str(e)}", flush=True)
                    mlflow.log_metric(f"validation_example_{i+1}_error", 1)
                    all_predictions.append(None)  # Keep list aligned with validation_set
        
            if valid_count > 0:
                avg_score = total_score / valid_count
                print(f"\nAverage Validation Score: {avg_score}", flush=True)
                try:
                    mlflow.log_metric("avg_validation_score", avg_score)
                except Exception as e:
                    print(f"Failed to log metric to MLflow: {e}")
            else:
                print("No valid validation examples completed successfully", flush=True)
                mlflow.log_param("validation_status", "no_valid_examples")
            
            # Log validation set size and example details
            mlflow.log_metric("validation_set_size", len(validation_set))
            mlflow.log_metric("valid_validation_examples", valid_count)
            
            # Log raw validation examples for debugging
            try:
                validation_data = []
                for ex, pred in zip(validation_set, all_predictions):
                    if pred is None:
                        continue  # Skip failed predictions
                    try:
                        validation_data.append({
                            "source": ex.source_text[:500], 
                            "question": pred.question[:500],
                            "memory_answer": pred.memory_answer[:500],
                            "reference_answer": pred.reference_answer[:500],
                            "score": gan_metric(ex, pred)  # Recompute score for logging
                        })
                    except Exception:
                        continue  # Skip problematic entries
                mlflow.log_dict({"validation_data": validation_data}, "validation_data.json")
            except Exception as e:
                print(f"Failed to log validation data: {e}")
        else:
            reason = "optimization failed" if not optimized_program else "no validation set"
            print(f"Skipping validation - {reason}", flush=True)
            
    # Ensure MLflow run is properly closed
    try:
        mlflow.end_run()
    except Exception:
        pass

    print("Script finished.", flush=True)

if __name__ == "__main__":
    main()
