#!/usr/bin/env python3

import dotenv
dotenv.load_dotenv()

import dspy
import time
import os
import mlflow
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import Schema, ColSpec
import uuid # For unique IDs and cache busting
import copy # For implementing __deepcopy__

# === GLOBAL CONFIGURATIONS & DEFINITIONS ===

# --- LLM Configuration ---
LLM_MODEL_NAME = "deepseek/deepseek-chat"
LLM = dspy.LM(
    model=LLM_MODEL_NAME,
    max_tokens=500,
    temperature=0.7,
    cache=False  # Disable DSPy's LM-level caching
)
dspy.settings.configure(lm=LLM)

# --- MLflow Experiment Setup ---
MLFLOW_EXPERIMENT_NAME = "DSPy_SIMBA_Response_Time_Opt"
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

# --- DSPy Signature Definition ---
class TimedQA(dspy.Signature):
    """Answer questions, optimized for response time."""
    question = dspy.InputField(desc="The question to answer.")
    answer = dspy.OutputField(desc="An answer generated quickly.")

# --- Custom Predictor to Track Time ---
class TimedPredict(dspy.Predict):
    def __init__(self, signature, **config):
        super().__init__(signature, **config)
        self._instance_id = str(uuid.uuid4())
        print(f"DEBUG: TimedPredict INSTANCE CREATED: ID={self._instance_id}, Signature={signature}")

    def forward(self, **kwargs):
        # print(f"DEBUG: TimedPredict FORWARD called: ID={self._instance_id}, Actual kwargs keys: {list(kwargs.keys())}")
        start_time = time.perf_counter()
        prediction_result = super().forward(**kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        # print(f"DEBUG: Instance {self._instance_id}: Measured duration for call with keys {list(kwargs.keys())}: {duration:.6f}s")
        
        if isinstance(prediction_result, dspy.Prediction):
            prediction_result._last_prediction_time = duration
        elif isinstance(prediction_result, list) and prediction_result and isinstance(prediction_result[0], dspy.Prediction):
            for p in prediction_result:
                p._last_prediction_time = duration
        return prediction_result

    def __deepcopy__(self, memo):
        new_copy = super().__deepcopy__(memo)
        new_copy._instance_id = str(uuid.uuid4()) 
        print(f"DEBUG: TimedPredict DEEP COPIED INSTANCE CREATED: ID={new_copy._instance_id}, Signature={new_copy._signature if hasattr(new_copy, '_signature') else 'UnknownSignature'}")
        return new_copy

# --- Metric Function for Response Time ---
def response_time_metric(gold, pred, trace=None):
    """Scores predictions based on their generation time, read from the Prediction object."""
    if hasattr(pred, '_last_prediction_time'):
        response_time = pred._last_prediction_time
        return -response_time # SIMBA maximizes, so negative time
    return -float('inf') # Penalize heavily if time not found

# --- Training Data ---
TRAINSET = [
    dspy.Example(question="What is the capital of France?").with_inputs("question"),
    dspy.Example(question="Explain quantum computing in one sentence.").with_inputs("question"),
    dspy.Example(question="Who wrote 'To Kill a Mockingbird'?").with_inputs("question"),
]

# --- SIMBA Optimizer Configuration ---
SIMBA_PARAMS = {
    "max_steps": 3,
    "max_demos": 2,
    "bsize": len(TRAINSET),
    "num_threads": 2
}

# === HELPER FUNCTION FOR PROGRAM EVALUATION ===

def run_and_evaluate_program(program, program_name, question, mlflow_run_id, status_tag):
    """Runs the given DSPy program multiple times for stable timing, prints info, and logs to MLflow."""
    
    num_runs = 3  # Total runs: 1 for warm-up specific to this eval, 2 for timing
    actual_timed_runs = num_runs - 1
    
    answer_for_logging = "Error during prediction."
    llm_time_for_logging = float('inf')
    overall_success = False
    
    accumulated_time = 0.0
    successful_timed_runs = 0
    # Store the last valid prediction object to access its attributes if needed
    last_successful_pred = None 

    print(f"\n--- Evaluating {program_name} ({status_tag}) with {num_runs} runs ({actual_timed_runs} timed) ---")
    print(f"Question: {question}")

    for i in range(num_runs):
        current_answer_text = "Error in this run."
        current_run_time = float('inf')
        run_success = False
        current_pred = None
        try:
            current_pred = program(question=question)
            current_answer_text = current_pred.answer
            # Ensure _last_prediction_time is available, otherwise default to infinity
            current_run_time = getattr(current_pred, '_last_prediction_time', float('inf')) 
            if current_run_time is None: # getattr might return None if attribute exists but is None
                current_run_time = float('inf')

            run_success = True
            if i == 0: # First run is considered a warm-up for this specific evaluation sequence
                print(f"  Run {i+1}/{num_runs} (warm-up): Answer='{str(current_answer_text)[:100].strip()}...', Time={current_run_time:.4f}s")
            else:
                print(f"  Run {i+1}/{num_runs} (timed):   Answer='{str(current_answer_text)[:100].strip()}...', Time={current_run_time:.4f}s")
                if current_run_time != float('inf'): # Only accumulate valid times
                    accumulated_time += current_run_time
                    successful_timed_runs += 1
            
            if run_success:
                answer_for_logging = current_answer_text 
                last_successful_pred = current_pred # Store the prediction object
                overall_success = True 

        except Exception as e:
            print(f"  Run {i+1}/{num_runs}: ERROR running {program_name}: {e}")
            if i == 0:
                overall_success = False 
                break 
    
    if successful_timed_runs > 0:
        avg_llm_time = accumulated_time / successful_timed_runs
        llm_time_for_logging = avg_llm_time
        print(f"Average LLM Call Time ({successful_timed_runs} timed runs): {avg_llm_time:.4f} seconds")
    elif overall_success and last_successful_pred: # Succeeded, but maybe only warm-up or 1 timed run
        # Fallback to the last known successful time if no timed runs completed but overall_success is true
        llm_time_for_logging = getattr(last_successful_pred, '_last_prediction_time', float('inf'))
        if llm_time_for_logging is None: llm_time_for_logging = float('inf')
        print(f"LLM Call Time (based on last successful run): {llm_time_for_logging:.4f} seconds")
    else:
        llm_time_for_logging = float('inf')
        print(f"All runs failed or no valid time recorded for {program_name}. Logging infinite time.")

    with mlflow.start_run(run_id=mlflow_run_id, nested=True) as nested_run:
        mlflow.log_param(f"{program_name}_question_{status_tag}", question)
        mlflow.log_metric(f"{program_name}_time_seconds_{status_tag}", llm_time_for_logging)
        mlflow.log_text(str(answer_for_logging), f"{program_name}_answer_{status_tag}.txt") # Ensure answer is string
        mlflow.set_tag(f"{program_name}_status_{status_tag}", "success" if overall_success else "failed")
        mlflow.set_tag("evaluation_type", status_tag)

    print(f"--- Evaluation for {program_name} ({status_tag}) finished ---")
    # Return the prediction object from the last successful run for potential further inspection
    return last_successful_pred, llm_time_for_logging, overall_success

# === MAIN OPTIMIZATION WORKFLOW ===

def main_optimization_workflow():
    """Orchestrates the DSPy SIMBA optimization and MLflow logging."""
    
    # Define student program and test question
    student_program = TimedPredict(TimedQA)
    test_question_main = "What are the main components of a car engine?"

    # LLM Warm-up call
    print("\n--- Performing a warm-up LLM call ---")
    try:
        # Using a unique prompt for warm-up
        _ = LLM(f"General LLM Warm-up at {time.time()}-{str(uuid.uuid4())}") 
        print("--- Warm-up call complete ---")
    except Exception as e:
        print(f"Warm-up call failed: {e}")

    # Student Program Warm-up call
    print("\n--- Performing a warm-up call with student_program ---")
    try:
        # Using a unique prompt for warm-up
        _ = student_program(question=f"Student program warm-up at {time.time()}-{str(uuid.uuid4())}") 
        print("--- student_program warm-up call complete ---")
    except Exception as e:
        print(f"student_program warm-up call failed: {e}")

    with mlflow.start_run() as run:
        mlflow_run_id = run.info.run_id
        print(f"MLflow Run ID: {mlflow_run_id}")
        mlflow.set_tag("dspy_optimizer", "SIMBA")

        # Log LLM and SIMBA parameters
        mlflow.log_param("llm_model_name", LLM_MODEL_NAME)
        if hasattr(LLM, 'kwargs'): # Check if LLM is configured
            mlflow.log_param("llm_max_tokens", LLM.kwargs.get("max_tokens"))
            mlflow.log_param("llm_temperature", LLM.kwargs.get("temperature"))
        
        simba_params_for_logging = {f"simba_{k}": v for k, v in SIMBA_PARAMS.items()}
        mlflow.log_params(simba_params_for_logging)

        # Evaluate Unoptimized Program
        print("\n--- Testing Unoptimized Program ---")
        unoptimized_pred, unoptimized_time, unoptimized_success = run_and_evaluate_program(
            program=student_program, 
            program_name="student_program_unoptimized", 
            question=test_question_main,
            mlflow_run_id=mlflow_run_id,
            status_tag="unoptimized_evaluation"
        )
        if unoptimized_success:
            # Define the model signature
            input_schema = Schema([ColSpec("string", "question")])
            output_schema = Schema([ColSpec("string", "answer")])
            signature = ModelSignature(inputs=input_schema, outputs=output_schema)

            # Log the unoptimized program model within the main run
            mlflow.dspy.log_model(student_program, artifact_path="unoptimized_dspy_program", signature=signature)
            mlflow.set_tag("unoptimized_program_logged", "true")
        else:
            mlflow.set_tag("unoptimized_program_logged", "false")


        # SIMBA Optimizer Instantiation and Compilation
        print(f"\nInitializing SIMBA optimizer with settings: {SIMBA_PARAMS}")
        simba_optimizer = dspy.SIMBA(
            metric=response_time_metric,
            **SIMBA_PARAMS 
        )
        
        optimized_program = None
        print("\n--- Starting SIMBA Compilation ---")
        try:
            # Create a deepcopy for SIMBA to modify
            program_for_simba = student_program.deepcopy() 
            optimized_program = simba_optimizer.compile(
                student=program_for_simba, 
                trainset=TRAINSET
            )
            print("--- SIMBA Compilation Finished ---")
            mlflow.set_tag("simba_compilation_status", "Success")

        except Exception as e:
            print(f"Error during SIMBA compilation: {e}")
            mlflow.set_tag("simba_compilation_status", "Failed")
            mlflow.log_param("simba_compilation_error", str(e))

        # Evaluate Optimized Program
        optimized_time = float('inf') # Default to inf for comparison robustness
        if optimized_program:
            print("\n--- Testing Optimized Program ---")
            optimized_pred, optimized_time, optimized_success = run_and_evaluate_program(
                program=optimized_program, 
                program_name="optimized_program_final", 
                question=test_question_main,
                mlflow_run_id=mlflow_run_id,
                status_tag="optimized_final_evaluation"
            )
            if optimized_success:
                 # Define the model signature (can reuse if defined scope-appropriately, or redefine for clarity)
                 input_schema = Schema([ColSpec("string", "question")])
                 output_schema = Schema([ColSpec("string", "answer")])
                 signature = ModelSignature(inputs=input_schema, outputs=output_schema)

                 # Log the final optimized program model within the main run
                 mlflow.dspy.log_model(optimized_program, artifact_path="optimized_dspy_program_final", signature=signature)
                 mlflow.set_tag("optimized_program_logged", "true")
            else:
                mlflow.set_tag("optimized_program_logged", "false")


        # Calculate and log time improvement
        if unoptimized_time != float('inf') and optimized_time != float('inf'):
            improvement = unoptimized_time - optimized_time
            print(f"\nUnoptimized Time: {unoptimized_time:.4f}s, Optimized Time: {optimized_time:.4f}s")
            if unoptimized_time > 0: # Avoid division by zero
                improvement_percent = (improvement / unoptimized_time) * 100
                print(f"Time Improvement (LLM call): {improvement:.4f} seconds ({improvement_percent:.2f}%)")
                mlflow.log_metric("time_improvement_seconds", improvement)
                mlflow.log_metric("time_improvement_percent", improvement_percent)
            else: # Unoptimized time was zero or negative (error)
                print(f"Time Improvement (LLM call): {improvement:.4f} seconds (Unoptimized time was zero or invalid, percentage not calculated)")
                mlflow.log_metric("time_improvement_seconds", improvement)
        else:
            print("\nCould not reliably compare unoptimized and optimized times due to errors or missing data.")
            if unoptimized_time == float('inf'):
                print("Unoptimized program evaluation failed or did not produce a valid time.")
            if optimized_time == float('inf'):
                print("Optimized program evaluation failed or did not produce a valid time.")
    
    print("\nScript finished.")

# === SCRIPT ENTRY POINT ===
if __name__ == "__main__":
    main_optimization_workflow()
