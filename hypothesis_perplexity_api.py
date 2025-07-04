#!/usr/bin/env python3
"""
Hypothesis Perplexity Evaluator - API Version

Uses language model APIs to evaluate how well hypotheses explain outcomes.
This version uses log probabilities from API responses for perplexity calculation.
"""

import argparse
import json
import sys
from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import dspy

load_dotenv()


@dataclass
class EvaluationCase:
    """Single evaluation case with hypothesis, situation, and outcome."""
    hypothesis: str
    situation: str
    outcome: str
    name: Optional[str] = None


class APIPerplexityEvaluator:
    """Evaluates hypothesis explanatory power using LLM completion probabilities."""
    
    def __init__(self, model: str = "openrouter/google/gemini-2.5-flash-preview"):
        """Initialize with a language model."""
        self.lm = dspy.LM(
            model=model,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            api_base="https://openrouter.ai/api/v1"
        )
        dspy.configure(lm=self.lm)
    
    def evaluate_completion_likelihood(self, prompt: str, completion: str) -> float:
        """
        Evaluate how likely a completion is given a prompt.
        Returns a score where higher is better (more likely).
        """
        # Create a few-shot prompt to get probability assessment
        assessment_prompt = f"""Rate how naturally the following text flows from 0-100, where 100 means the outcome is extremely natural and expected given the context, and 0 means it's completely unexpected:

Context: {prompt}

Continuation: {completion}

Provide only a number between 0-100."""
        
        response = self.lm(assessment_prompt, temperature=0)
        
        # Handle different response formats
        if isinstance(response, list):
            response = response[0] if response else "50"
        
        try:
            score = float(str(response).strip())
            return max(0, min(100, score))  # Ensure in range
        except:
            return 50.0  # Default middle score if parsing fails
    
    def evaluate_hypothesis(self, case: EvaluationCase) -> Dict[str, float]:
        """Evaluate a single hypothesis case."""
        # Construct contexts with and without hypothesis
        context_with_hypothesis = f"Hypothesis: {case.hypothesis}\n\nSituation: {case.situation}"
        context_without_hypothesis = f"Situation: {case.situation}"
        
        # Evaluate likelihood of outcome given each context
        likelihood_with = self.evaluate_completion_likelihood(
            context_with_hypothesis, 
            f"Outcome: {case.outcome}"
        )
        likelihood_without = self.evaluate_completion_likelihood(
            context_without_hypothesis,
            f"Outcome: {case.outcome}"
        )
        
        # Calculate improvement
        improvement = likelihood_with - likelihood_without
        improvement_percent = (improvement / likelihood_without * 100) if likelihood_without > 0 else 0
        
        return {
            "likelihood_with_hypothesis": likelihood_with,
            "likelihood_without_hypothesis": likelihood_without,
            "improvement": improvement,
            "improvement_percent": improvement_percent,
            "explanatory_value": improvement > 5  # Threshold for meaningful improvement
        }
    
    def evaluate_batch(self, cases: List[EvaluationCase]) -> List[Dict]:
        """Evaluate multiple cases."""
        results = []
        
        for i, case in enumerate(cases):
            print(f"Evaluating case {i+1}/{len(cases)}: {case.name or 'Unnamed'}...")
            result = self.evaluate_hypothesis(case)
            result["case_name"] = case.name or f"Case {i + 1}"
            result["hypothesis"] = case.hypothesis
            result["situation"] = case.situation
            result["outcome"] = case.outcome
            results.append(result)
        
        return results


def create_comparative_prompt(case: EvaluationCase) -> str:
    """Create a prompt that asks the model to compare explanatory power directly."""
    return f"""Compare these two explanations for the same outcome:

VERSION A (with hypothesis):
Hypothesis: {case.hypothesis}
Situation: {case.situation}
Outcome: {case.outcome}

VERSION B (without hypothesis):
Situation: {case.situation}
Outcome: {case.outcome}

Which version makes the outcome more understandable and expected?
Answer with: A (hypothesis helps), B (hypothesis doesn't help), or SAME (no difference)
Then rate the improvement from -100 to +100, where positive means the hypothesis helps."""


class ComparativeEvaluator:
    """Alternative evaluator using direct comparison."""
    
    def __init__(self, model: str = "openrouter/google/gemini-2.5-flash-preview"):
        """Initialize with a language model."""
        self.lm = dspy.LM(
            model=model,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            api_base="https://openrouter.ai/api/v1"
        )
        dspy.configure(lm=self.lm)
    
    def evaluate_hypothesis(self, case: EvaluationCase) -> Dict[str, any]:
        """Evaluate using comparative assessment."""
        prompt = create_comparative_prompt(case)
        response = self.lm(prompt, temperature=0)
        
        # Handle different response formats
        if isinstance(response, list):
            response = response[0] if response else ""
        
        # Parse response
        lines = str(response).strip().split('\n')
        choice = "SAME"
        improvement = 0
        
        for line in lines:
            if line.startswith(('A', 'B', 'SAME')):
                choice = line.split()[0]
            elif any(char.isdigit() or char == '-' for char in line):
                try:
                    # Extract number from line
                    import re
                    numbers = re.findall(r'-?\d+', line)
                    if numbers:
                        improvement = int(numbers[0])
                except:
                    pass
        
        return {
            "comparison_result": choice,
            "improvement_score": improvement,
            "explanatory_value": choice == "A" and improvement > 10,
            "hypothesis": case.hypothesis
        }
    
    def evaluate_batch(self, cases: List[EvaluationCase]) -> List[Dict]:
        """Evaluate multiple cases."""
        results = []
        
        for i, case in enumerate(cases):
            print(f"Evaluating case {i+1}/{len(cases)}: {case.name or 'Unnamed'}...")
            result = self.evaluate_hypothesis(case)
            result["case_name"] = case.name or f"Case {i + 1}"
            result["situation"] = case.situation
            result["outcome"] = case.outcome
            results.append(result)
        
        return results


def print_results(results: List[Dict]):
    """Pretty print evaluation results."""
    print("\n" + "="*80)
    print("HYPOTHESIS EXPLANATORY VALUE EVALUATION")
    print("="*80 + "\n")
    
    for result in results:
        print(f"Case: {result['case_name']}")
        print(f"  Hypothesis: {result.get('hypothesis', 'N/A')[:60]}...")
        
        if 'likelihood_with_hypothesis' in result:
            print(f"  Likelihood WITH hypothesis:    {result['likelihood_with_hypothesis']:.1f}/100")
            print(f"  Likelihood WITHOUT hypothesis: {result['likelihood_without_hypothesis']:.1f}/100")
            print(f"  Improvement:                   {result['improvement']:.1f} points ({result['improvement_percent']:.1f}%)")
        elif 'comparison_result' in result:
            print(f"  Comparison result:             {result['comparison_result']}")
            print(f"  Improvement score:             {result['improvement_score']}")
        
        print(f"  Has explanatory value:         {'YES' if result['explanatory_value'] else 'NO'}")
        print()
    
    # Summary
    explanatory_count = sum(1 for r in results if r['explanatory_value'])
    print("-"*80)
    print(f"SUMMARY: {explanatory_count}/{len(results)} hypotheses have significant explanatory value")
    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Evaluate hypothesis explanatory value using LLM APIs")
    parser.add_argument("--model", default="openrouter/google/gemini-2.5-flash-preview", help="Model to use")
    parser.add_argument("--method", choices=["likelihood", "comparative"], default="likelihood")
    parser.add_argument("--file", help="JSON file with evaluation cases")
    parser.add_argument("--demo", action="store_true", help="Run with demo examples")
    
    args = parser.parse_args()
    
    # Load cases
    if args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
        cases = [
            EvaluationCase(
                hypothesis=item["hypothesis"],
                situation=item["situation"], 
                outcome=item["outcome"],
                name=item.get("name")
            )
            for item in data
        ]
    else:
        # Demo case
        cases = [
            EvaluationCase(
                name="Thermodynamics Demo",
                hypothesis="Heat flows from hot objects to cold objects until thermal equilibrium is reached",
                situation="A hot cup of coffee is left on a table in a room temperature environment",
                outcome="After 30 minutes, the coffee has cooled to nearly room temperature"
            )
        ]
    
    # Evaluate
    print(f"Using {args.method} method with model: {args.model}")
    
    if args.method == "likelihood":
        evaluator = APIPerplexityEvaluator(model=args.model)
    else:
        evaluator = ComparativeEvaluator(model=args.model)
    
    results = evaluator.evaluate_batch(cases)
    print_results(results)
    
    # Save results
    if sys.stdin.isatty():
        save = input("\nSave results? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"hypothesis_results_{args.method}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Saved to {filename}")


if __name__ == "__main__":
    main()