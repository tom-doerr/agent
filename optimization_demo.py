#!/usr/bin/env python3

import dspy, reasoning_gym, sys
import mlflow
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

dspy_version_installed = dspy.__version__
print(f"DSPy version: {dspy_version_installed}")

mlflow.set_tracking_uri("http://localhost:5002")
mlflow.set_experiment("dspy-optimization-demo")
mlflow.autolog()

# Token logging setup
TOKEN_LOG_FILE = Path("token_usage.ndjson")
OPTIMIZATION_START_TIME = datetime.now()

# Load pricing config
with open("pricing_config.json", "r") as f:
    PRICING_CONFIG = json.load(f)

def get_current_pricing():
    """Get current pricing based on UTC time."""
    now_utc = datetime.now(timezone.utc)
    current_hour = now_utc.hour + now_utc.minute / 60.0
    
    pricing = PRICING_CONFIG["deepseek_reasoner"]["pricing_schedule"]
    
    # Check if we're in discount period (16:30 - 00:30 UTC)
    if current_hour >= 16.5 or current_hour < 0.5:
        return pricing["discount"], "discount"
    else:
        return pricing["standard"], "standard"

def calculate_cost(input_tokens: int, output_tokens: int, cache_hit_rate: float = 0.0):
    """Calculate cost in USD for the given token counts."""
    pricing, period = get_current_pricing()
    
    # Calculate input cost (mix of cache hit and miss)
    input_cost_hit = (input_tokens * cache_hit_rate) * pricing["input_cache_hit"] / 1_000_000
    input_cost_miss = (input_tokens * (1 - cache_hit_rate)) * pricing["input_cache_miss"] / 1_000_000
    output_cost = output_tokens * pricing["output"] / 1_000_000
    
    total_cost = input_cost_hit + input_cost_miss + output_cost
    
    return {
        "total_cost_usd": total_cost,
        "input_cost_usd": input_cost_hit + input_cost_miss,
        "output_cost_usd": output_cost,
        "pricing_period": period,
        "cache_hit_rate": cache_hit_rate
    }

def wait_for_discount_period():
    """Check if we should wait for discount period."""
    now_utc = datetime.now(timezone.utc)
    current_hour = now_utc.hour + now_utc.minute / 60.0
    
    # If we're in standard period, calculate wait time to discount
    if 0.5 <= current_hour < 16.5:
        hours_until_discount = 16.5 - current_hour
        print(f"\n⚠️  Currently in STANDARD pricing period (4x more expensive)")
        print(f"⏰ Discount period starts in {hours_until_discount:.1f} hours (16:30 UTC)")
        print(f"💡 Consider waiting or run with --force-expensive flag")
        return True, hours_until_discount
    else:
        print(f"\n✅ Currently in DISCOUNT pricing period (75% cheaper!)")
        if current_hour >= 16.5:
            hours_remaining = 24 - current_hour + 0.5
        else:
            hours_remaining = 0.5 - current_hour
        print(f"⏰ Discount period ends in {hours_remaining:.1f} hours")
        return False, hours_remaining

def log_token_usage(phase: str, optimizer: str, step: int = 0, **kwargs):
    """Log token usage with comprehensive metadata and cost calculation."""
    # Calculate cost if we have token counts
    cost_info = {}
    if "input_tokens" in kwargs and "output_tokens" in kwargs:
        cost_info = calculate_cost(
            kwargs.get("input_tokens", 0),
            kwargs.get("output_tokens", 0),
            kwargs.get("cache_hit_rate", 0.0)
        )
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "unix_time": time.time(),
        "utc_hour": datetime.now(timezone.utc).hour + datetime.now(timezone.utc).minute / 60.0,
        "phase": phase,  # e.g., "training", "validation", "inference"
        "optimizer": optimizer,  # e.g., "SIMBA", "MIPROv2"
        "step": step,
        "elapsed_seconds": (datetime.now() - OPTIMIZATION_START_TIME).total_seconds(),
        **kwargs,
        **cost_info
    }
    
    # Append to NDJSON file
    with open(TOKEN_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    # Also print summary
    if "total_tokens" in kwargs:
        cost_str = f" (${cost_info.get('total_cost_usd', 0):.4f})" if cost_info else ""
        print(f"[{phase}] Step {step}: {kwargs.get('total_tokens', 0)} tokens{cost_str} "
              f"(in: {kwargs.get('input_tokens', 0)}, "
              f"out: {kwargs.get('output_tokens', 0)}, "
              f"reasoning: {kwargs.get('reasoning_tokens', 0)})")

# 1️⃣  Wire DeepSeek-R1 7B served by Ollama
# lm = dspy.LM( 'ollama/deepseek-r1:7b', api_base='http://localhost:11434', api_key='')
# lm = dspy.LM('openrouter/google/gemini-2.5-flash-lite-preview-06-17')
# lm = dspy.LM('openrouter/deepseek/deepseek-r1-0528-qwen3-8b', max_tokens=20000)
# lm = dspy.LM('openrouter/deepseek/dnereek-r1-0528', max_tokens=20000, temperature=1.5)

# Create a wrapper to capture token usage
class TokenLoggingLM:
    def __init__(self, lm, optimizer_name="unknown"):
        self.lm = lm
        self.optimizer_name = optimizer_name
        self.call_count = 0
        
    def __call__(self, *args, **kwargs):
        self.call_count += 1
        start_time = time.time()
        
        # Call the actual LM
        result = self.lm(*args, **kwargs)
        
        # Extract token usage from the result
        if hasattr(self.lm, 'history') and self.lm.history:
            last_call = self.lm.history[-1]
            usage = last_call.get('usage', {})
            
            # Log comprehensive information
            log_token_usage(
                phase="optimization" if "bootstrap" in str(args) else "inference",
                optimizer=self.optimizer_name,
                step=self.call_count,
                model=str(self.lm),
                input_tokens=usage.get('prompt_tokens', 0),
                output_tokens=usage.get('completion_tokens', 0),
                reasoning_tokens=usage.get('reasoning_tokens', 0),
                total_tokens=usage.get('total_tokens', 0),
                cached_tokens=usage.get('cached_tokens', 0),
                duration_ms=int((time.time() - start_time) * 1000),
                temperature=kwargs.get('temperature', self.lm.kwargs.get('temperature', 1.0)),
                max_tokens=kwargs.get('max_tokens', self.lm.kwargs.get('max_tokens', 0)),
                prompt_length=len(str(args[0])) if args else 0,
                response_length=len(str(result)) if result else 0,
                # Additional metadata
                parallel=dspy.settings.parallel,
                batch_size=kwargs.get('batch_size', 1),
                raw_usage=usage  # Store complete usage dict
            )
            
            # Also log to MLflow
            mlflow.log_metrics({
                f"tokens_{self.optimizer_name}_input": usage.get('prompt_tokens', 0),
                f"tokens_{self.optimizer_name}_output": usage.get('completion_tokens', 0),
                f"tokens_{self.optimizer_name}_reasoning": usage.get('reasoning_tokens', 0),
                f"tokens_{self.optimizer_name}_total": usage.get('total_tokens', 0),
            }, step=self.call_count)
        
        return result
    
    def __getattr__(self, name):
        return getattr(self.lm, name)

# Create base LM and wrapper
# Use DeepSeek API directly with tight token limits
import os
deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
base_lm = dspy.LM('deepseek/deepseek-chat', 
                  api_key=deepseek_api_key,
                  api_base='https://api.deepseek.com',
                  max_tokens=500,  # Tight max token limit
                  temperature=0.7)
lm = TokenLoggingLM(base_lm, optimizer_name="initial")

# dspy.configure(lm=lm, parallel=False)   # single-thread to avoid OOM on CPU
dspy.configure(lm=lm, parallel=True)   # single-thread to avoid OOM on CPU

# 2️⃣  Tiny training batch from Reasoning Gym (“leg_counting” task)
# 2️⃣  Select task for optimization - these are "coin-flip" tasks where DeepSeek R1 hovers around 50%
# Task options and their typical accuracy on 100-sample test sets:
TASK_OPTIONS = {
    'fraction_simplification': 'Arithmetic - 51% - Multi-step ops with sign handling',
    'base_conversion': 'Algorithms - 48% - Decimal to base-n conversion (n ∈ [2,36])',
    'figlet_font': 'Cognition/ARC - 49% - ASCII-art word recognition',
    'number_sequence': 'Induction - 52% - Find next term in sequence',
    'shortest_path': 'Graphs - 46% - Grid maze pathfinding (≤12×12)',
    'n_queens': 'Games - 47% - Generate valid n-queens boards (size 8)'
}

# Default task selection
SELECTED_TASK = 'shortest_path'  # Routinely finds a path but ~40% are not minimal length

print(f"\n📊 Selected task: {SELECTED_TASK}")
print(f"   Description: {TASK_OPTIONS[SELECTED_TASK]}")
print(f"   (Change with SELECTED_TASK variable)\n")

train_ds = reasoning_gym.create_dataset(SELECTED_TASK, size=40, seed=0)
trainset = [
    dspy.Example(question=e["question"], answer=str(e["answer"]))
        .with_inputs("question")
    for e in train_ds
]

qa = dspy.Predict("question -> answer")
# qa = dspy.ChainOfThought('question -> answer')

# 4️⃣  Exact-match metric
def em(ex, pred, trace=None):
    return float(pred.answer.strip() == ex.answer.strip())

# Check pricing period before starting expensive optimization
in_expensive_period, time_info = wait_for_discount_period()

# Add command line parsing for override
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--force-expensive', action='store_true', help='Run even during expensive period')
parser.add_argument('--use-mipro', action='store_true', help='Use MIPROv2 instead of SIMBA')
args, unknown = parser.parse_known_args()

if in_expensive_period and not args.force_expensive:
    print("\n❌ Aborting to save costs. Use --force-expensive to override.")
    print(f"💰 Running now would cost ~4x more than waiting {time_info:.1f} hours")
    sys.exit(1)

# 5️⃣  Prompt-optimize with SIMBA (stochastic mini-batch ascent)
# simba = dspy.SIMBA(metric=em, bsize=6, max_steps=4, max_demos=3)
if not args.use_mipro:
    OPTIMIZER_NAME = "SIMBA"
    print(f"\n{'='*60}")
    print(f"Starting optimization with {OPTIMIZER_NAME}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # Update the wrapper's optimizer name
    lm.optimizer_name = OPTIMIZER_NAME
    
    # Log optimization start
    log_token_usage(
        phase="optimization_start",
        optimizer=OPTIMIZER_NAME,
        step=0,
        trainset_size=len(trainset),
        model_config={
            "model": str(base_lm),
            "max_tokens": base_lm.kwargs.get('max_tokens', 0),
            "temperature": base_lm.kwargs.get('temperature', 1.0),
            "parallel": dspy.settings.parallel
        }
    )
    
    simba = dspy.SIMBA(metric=em, num_threads=100)
    better_qa = simba.compile(qa, trainset=trainset, seed=42)
    
    # Log optimization complete
    log_token_usage(
        phase="optimization_complete",
        optimizer=OPTIMIZER_NAME,
        step=lm.call_count,
        total_calls=lm.call_count
    )
else:
    OPTIMIZER_NAME = "MIPROv2"
    print(f"\n{'='*60}")
    print(f"Starting optimization with {OPTIMIZER_NAME}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # Update the wrapper's optimizer name
    lm.optimizer_name = OPTIMIZER_NAME
    
    # Log optimization start
    log_token_usage(
        phase="optimization_start",
        optimizer=OPTIMIZER_NAME,
        step=0,
        trainset_size=len(trainset),
        model_config={
            "model": str(base_lm),
            "max_tokens": base_lm.kwargs.get('max_tokens', 0),
            "temperature": base_lm.kwargs.get('temperature', 1.0),
            "parallel": dspy.settings.parallel
        }
    )
    
    mipro = dspy.MIPROv2(metric=em, auto='medium')
    better_qa = mipro.compile(qa, trainset=trainset, seed=42, requires_permission_to_run=False)
    
    # Log optimization complete
    log_token_usage(
        phase="optimization_complete",
        optimizer=OPTIMIZER_NAME,
        step=lm.call_count,
        total_calls=lm.call_count
    )

# 6️⃣  Quick smoke-test
print(f"\n{'='*60}")
print("Running test inference")
print(f"{'='*60}\n")

lm.optimizer_name = f"{OPTIMIZER_NAME}_test"

test = reasoning_gym.create_dataset('leg_counting', size=1, seed=1337)[0]
print("Q:", test["question"])

# Log test start
test_start_count = lm.call_count
answer = better_qa(question=test["question"]).answer
print("A:", answer)

# Log test inference
log_token_usage(
    phase="test_inference",
    optimizer=OPTIMIZER_NAME,
    step=lm.call_count,
    test_question_length=len(test["question"]),
    test_answer_length=len(answer)
)

# Generate summary report
print(f"\n{'='*60}")
print("TOKEN USAGE SUMMARY")
print(f"{'='*60}")
print(f"Total LM calls: {lm.call_count}")
print(f"Optimization phase calls: {test_start_count}")
print(f"Test inference calls: {lm.call_count - test_start_count}")

# Read and summarize token log
total_tokens = 0
total_reasoning = 0
total_input = 0
total_output = 0
total_cost = 0.0
call_costs = []

with open(TOKEN_LOG_FILE, 'r') as f:
    for line in f:
        entry = json.loads(line)
        if entry.get('optimizer') == OPTIMIZER_NAME or entry.get('optimizer') == f"{OPTIMIZER_NAME}_test":
            total_tokens += entry.get('total_tokens', 0)
            total_reasoning += entry.get('reasoning_tokens', 0)
            total_input += entry.get('input_tokens', 0)
            total_output += entry.get('output_tokens', 0)
            if 'total_cost_usd' in entry:
                total_cost += entry['total_cost_usd']
                call_costs.append(entry['total_cost_usd'])

print(f"\nTotal tokens used: {total_tokens:,}")
print(f"  - Input tokens: {total_input:,}")
print(f"  - Output tokens: {total_output:,}")
print(f"  - Reasoning tokens: {total_reasoning:,}")

print(f"\n💰 COST ANALYSIS:")
print(f"Total cost: ${total_cost:.4f}")
if call_costs:
    print(f"Average cost per call: ${sum(call_costs)/len(call_costs):.4f}")
    print(f"Most expensive call: ${max(call_costs):.4f}")
    print(f"Cheapest call: ${min(call_costs):.4f}")

# Calculate what it would have cost in the other pricing period
pricing = PRICING_CONFIG["deepseek_reasoner"]["pricing_schedule"]
current_pricing, current_period = get_current_pricing()
other_period = "standard" if current_period == "discount" else "discount"
other_pricing = pricing[other_period]

# Rough estimate assuming no cache hits
other_cost = (total_input * other_pricing["input_cache_miss"] / 1_000_000 + 
              total_output * other_pricing["output"] / 1_000_000)

if current_period == "discount":
    print(f"\n✅ You saved ${other_cost - total_cost:.4f} by running during discount period!")
else:
    print(f"\n⚠️  You could have saved ${total_cost - other_cost:.4f} by running during discount period!")

print(f"\nToken log saved to: {TOKEN_LOG_FILE}")
print(f"Use 'python plot_token_usage.py' to visualize token usage and costs over time")

# Also save a summary
summary = {
    "optimizer": OPTIMIZER_NAME,
    "timestamp": datetime.now().isoformat(),
    "total_calls": lm.call_count,
    "total_tokens": total_tokens,
    "input_tokens": total_input,
    "output_tokens": total_output,
    "reasoning_tokens": total_reasoning,
    "trainset_size": len(trainset),
    "duration_seconds": (datetime.now() - OPTIMIZATION_START_TIME).total_seconds()
}

with open(f"optimization_summary_{OPTIMIZER_NAME}_{int(time.time())}.json", 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\nSummary saved to: optimization_summary_{OPTIMIZER_NAME}_{int(time.time())}.json")




























































