import os
import re
import io
import mlflow
import dspy
from functools import partial
from contextlib import redirect_stdout

# Centralized DSPy configuration
def configure_dspy(model_name):
    ll极 = dspy.LM(
        model=model_name,
        max_tokens=4000
    )
    dspy.settings.configure(lm=llm)
    return llm

# --- LLM Configuration ---
llm_model_name = "deepseek/deepseek-reasoner"
deepseek_lm = configure_dspy(llm_model_name)

# --- MLflow Parameters ---
mlflow_params = {
    "llm_model": llm_model_name,
    "target_answer_length": 100,
    "simba_max_steps": 12,
    "simba_max_demos": 10,
    "simba_bsize": 0, # Will be updated with len(trainset) later
    "simba_num_threads": 20, # Current desired value
    "simba_seed": 6793115,
    "script_version": "1.1" # Added version for tracking
}

# --- DSPy Signature Definition ---
class BasicQA(dspy.Signature):
    """Answer questions with answers of an optimized length."""
    question = dspy.InputField(desc="The question to answer.")
    answer = dspy.OutputField(desc="An answer that is ideally around 100 characters long.")

# --- Metric Function ---
def length_metric(gold, pred, trace=None, target_length=100):
    """Scores predictions based on proximity of answer length to target_length characters."""
    if not hasattr(pred, 'answer') or pred.answer is None:
        return -1000
    answer_length = len(pred.answer)
    score = -abs(answer_length - target_length)
    return score

# --- Training Data ---
trainset = [
    dspy.Example(question="What are the main advantages of using renewable energy sources?").with_inputs("question"),
    dspy.Example(question="Explain the concept of black holes in simple terms.").with_inputs("question"),
    dspy.Example(question="Summarize the plot of the movie Inception.").with_inputs("question"),
    dspy.Example(question="What were the key causes of World War I?").with_inputs("question"),
    dspy.Example(question="Describe the process of photosynthesis.").with_inputs("question"),
    dspy.Example(question="Who was Albert Einstein and what were his major contributions to science?").with_inputs("question"),
    dspy.Example(question="What is the significance of the Great Wall of China?").with_inputs("question")
]
mlflow_params["simba_bsize"] = len(trainset) # Update bsize param

# --- Student Program ---
unoptimized_program = dspy.Predict(BasicQA)

# --- Test Unoptimized Program ---
print("\n--- Testing Original (Unoptimized) Program ---")
question_to_test = "What is the capital of France and its main attractions?"
try:
    unoptimized_pred = unoptimized_program(question=question_to_test)
    print(f"Question: {question_to_test}")
    print(f"Unoptimized Answer: {unoptimized_pred.answer}")
    print(f"Unoptimized Answer Length: {len(unoptimized_pred.answer)}\n")
except Exception as e:
    print(f"Error running unoptimized program: {e}\n")

# --- MLflow Run for SIMBA Optimization ---
with mlflow.start_run() as run:
    print(f"MLflow Run ID: {run.info.run_id}")
    mlflow.set_tag("mlflow.runName", f"SIMBA Opt - {mlflow_params['llm_model']} - threads {mlflow_params['simba_num_threads']}")
    mlflow.log_params(mlflow_params)

    print(f"\nInitializing SIMBA optimizer with model '{mlflow_params['llm_model']}'...")
    # Note: SIMBA's verbose and track_metric are essential for parsing scores from stdout
    simba_optimizer = dspy.SIMBA(
        metric=partial(length_metric, target_length=mlflow_params['target_answer_length']),
        max_steps=mlflow_params['simba_max_steps'],
        max_demos=mlflow_params['simba_max_demos'],
        bsize=mlflow_params['simba_bsize'],
        num_threads=mlflow_params['simba_num_threads'],
        verbose=True, 
        track_metric=True, 
        seed=mlflow_params['simba_seed']
    )

    # Capture stdout to parse SIMBA's progress for metrics
    stdout_capture = io.StringIO()
    optimized_program = None # Initialize to ensure it's defined
    print("\n--- Starting SIMBA Compilation (stdout captured for metrics) ---")
    try:
        with redirect_stdout(stdout_capture):
            # Pass a copy of the student program to avoid in-place modification issues if not desired
            optimized_program = simba_optimizer.compile(
                student=unoptimized_program.deepcopy(), 
                trainset=trainset
            )
        print("--- SIMBA Compilation Finished ---\n")
    except Exception as e:
        print(f"Error during SIMBA compilation: {e}\n")
        mlflow.set_tag("simba_compilation_error", str(e))
        # Still try to parse any output captured so far, as some batches might have completed
    finally:
        captured_output = stdout_capture.getvalue()
        # For debugging the captured output:
        # print("\n--- Captured STDOUT from SIMBA ---")
        # print(captured_output)
        # print("--- End of Captured STDOUT ---")

        # Parse captured stdout for metrics
        # Regex to find "Batch X: Current best score is Y after this batch."
        batch_score_pattern = re.compile(r"Batch\s+(\d+):\s+Current best score is\s+([-+]?\d*\.?\d+)\s+after this batch\.")
        
        parsed_batch_scores = False
        for line in captured_output.splitlines():
            match = batch_score_pattern.search(line)
            if match:
                batch_num = int(match.group(1))
                score = float(match.group(2))
                mlflow.log_metric("simba_batch_best_score", score, step=batch_num)
                print(f"Logged to MLflow: Batch {batch_num}, Score: {score}")
                parsed_batch_scores = True
        
        if not parsed_batch_scores:
            print("Could not parse any 'Batch X: Current best score is Y' lines from SIMBA output. Check verbose/track_metric settings or regex.")

    if optimized_program:
        print("\nLogging optimized program to MLflow...")
        try:
            mlflow.dspy.log_model(
                optimized_program,
                artifact_path="optimized_dspy_program",
                # Using a more dynamic registered model name
                registered_model_name=f"simba_{mlflow_params['llm_model'].replace('/', '_')}_len_opt"
            )
            print("Optimized program logged to MLflow.")
            
            # Save locally as well, and log as artifact
            local_save_path = f"simba_optimized_{mlflow_params['llm_model'].replace('/', '_')}.json"
            optimized_program.save(local_save_path)
            print(f"Optimized program saved locally to {local_save_path}")
            mlflow.log_artifact(local_save_path, "optimized_program_local_save")

            # --- Testing SIMBA-Optimized Program (inside MLflow run) ---
            print("\n--- Testing SIMBA-Optimized Program (inside MLflow run) ---")
            try:
                optimized_pred = optimized_program(question=question_to_test)
                print(f"Question: {question_to_test}")
                print(f"Optimized Answer: {optimized_pred.answer}")
                opt_answer_len = len(optimized_pred.answer)
                print(f"Optimized Answer Length: {opt_answer_len}")
                mlflow.log_metric("optimized_test_answer_length_france", opt_answer_len)

                another_question = "Explain the theory of relativity in a concise manner."
                optimized_pred_another = optimized_program(question=another_question)
                print(f"\nQuestion: {another_question}")
                print(f"Optimized Answer: {optimized_pred_another.answer}")
                opt_another_len = len(optimized_pred_another.answer)
                print(f"Optimized Answer Length: {opt_another_len}")
                mlflow.log_metric("optimized_test_answer_length_relativity", opt_another_len)

            except Exception as e:
                print(f"Error running optimized program tests: {e}")
                mlflow.set_tag("optimized_program_test_error", str(e))
        except Exception as e:
            print(f"Error logging or saving optimized model: {e}")
            mlflow.set_tag("model_logging_error", str(e))
    else:
        print("SIMBA optimization did not produce an optimized program (likely due to an error during compile). Logging this status.")
        mlflow.set_tag("simba_status", "failed_to_compile_or_no_program_returned")

print("\nScript finished.")
