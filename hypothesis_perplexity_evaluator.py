#!/usr/bin/env python3
"""
Hypothesis Perplexity Evaluator

Measures the impact of hypotheses on perplexity by constructing prompts with:
1. Hypothesis (optional)
2. Situation/observation
3. Outcome

Lower perplexity when hypothesis is included indicates good explanatory value.
"""

import argparse
import json
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import dspy
from dspy import OpenAI
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


@dataclass
class EvaluationCase:
    """Single evaluation case with hypothesis, situation, and outcome."""
    hypothesis: str
    situation: str
    outcome: str
    name: Optional[str] = None


class PerplexityEvaluator:
    """Evaluates perplexity of outcomes with and without hypotheses."""
    
    def __init__(self, model_name: str = "gpt2"):
        """Initialize with a model for perplexity calculation."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()
        
        # Set pad token to eos token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def calculate_perplexity(self, text: str) -> float:
        """Calculate perplexity of a text."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
            perplexity = torch.exp(loss).item()
        
        return perplexity
    
    def evaluate_hypothesis(self, case: EvaluationCase) -> Dict[str, float]:
        """Evaluate a single hypothesis case."""
        # Construct prompts with and without hypothesis
        prompt_with_hypothesis = f"""Hypothesis: {case.hypothesis}

Situation: {case.situation}

Outcome: {case.outcome}"""
        
        prompt_without_hypothesis = f"""Situation: {case.situation}

Outcome: {case.outcome}"""
        
        # Calculate perplexities
        perplexity_with = self.calculate_perplexity(prompt_with_hypothesis)
        perplexity_without = self.calculate_perplexity(prompt_without_hypothesis)
        
        # Calculate improvement (lower is better for perplexity)
        improvement = (perplexity_without - perplexity_with) / perplexity_without * 100
        
        return {
            "with_hypothesis": perplexity_with,
            "without_hypothesis": perplexity_without,
            "improvement_percent": improvement,
            "explanatory_value": improvement > 0  # True if hypothesis helps
        }
    
    def evaluate_batch(self, cases: List[EvaluationCase]) -> List[Dict]:
        """Evaluate multiple cases."""
        results = []
        
        for case in cases:
            result = self.evaluate_hypothesis(case)
            result["case_name"] = case.name or f"Case {len(results) + 1}"
            results.append(result)
        
        return results


def load_cases_from_file(filepath: str) -> List[EvaluationCase]:
    """Load evaluation cases from a JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    cases = []
    for item in data:
        case = EvaluationCase(
            hypothesis=item["hypothesis"],
            situation=item["situation"],
            outcome=item["outcome"],
            name=item.get("name")
        )
        cases.append(case)
    
    return cases


def print_results(results: List[Dict]):
    """Pretty print evaluation results."""
    print("\n" + "="*60)
    print("HYPOTHESIS PERPLEXITY EVALUATION RESULTS")
    print("="*60 + "\n")
    
    for result in results:
        print(f"Case: {result['case_name']}")
        print(f"  Perplexity WITH hypothesis:    {result['with_hypothesis']:.2f}")
        print(f"  Perplexity WITHOUT hypothesis: {result['without_hypothesis']:.2f}")
        print(f"  Improvement:                   {result['improvement_percent']:.1f}%")
        print(f"  Has explanatory value:         {'YES' if result['explanatory_value'] else 'NO'}")
        print()
    
    # Summary statistics
    improvements = [r['improvement_percent'] for r in results]
    explanatory_count = sum(1 for r in results if r['explanatory_value'])
    
    print("-"*60)
    print("SUMMARY:")
    print(f"  Total cases evaluated:         {len(results)}")
    print(f"  Cases with explanatory value:  {explanatory_count} ({explanatory_count/len(results)*100:.1f}%)")
    print(f"  Average improvement:           {np.mean(improvements):.1f}%")
    print(f"  Best improvement:              {max(improvements):.1f}%")
    print(f"  Worst improvement:             {min(improvements):.1f}%")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Evaluate hypothesis explanatory value using perplexity")
    parser.add_argument("--model", default="gpt2", help="Model to use for perplexity calculation")
    parser.add_argument("--file", help="JSON file with evaluation cases")
    parser.add_argument("--demo", action="store_true", help="Run with demo examples")
    
    args = parser.parse_args()
    
    # Initialize evaluator
    print(f"Initializing perplexity evaluator with model: {args.model}")
    evaluator = PerplexityEvaluator(model_name=args.model)
    
    # Load or create cases
    if args.file:
        cases = load_cases_from_file(args.file)
    elif args.demo:
        # Demo cases
        cases = [
            EvaluationCase(
                name="Physics - Gravity",
                hypothesis="Objects fall due to gravitational attraction between masses",
                situation="A ball is released from a height of 10 meters",
                outcome="The ball accelerates downward and hits the ground in approximately 1.4 seconds"
            ),
            EvaluationCase(
                name="Biology - Photosynthesis",
                hypothesis="Plants convert sunlight into chemical energy through photosynthesis",
                situation="A plant is placed in direct sunlight with adequate water",
                outcome="The plant grows taller and produces new leaves over several weeks"
            ),
            EvaluationCase(
                name="Economics - Supply/Demand",
                hypothesis="Prices rise when demand exceeds supply",
                situation="A popular toy becomes scarce during the holiday season",
                outcome="The toy's price increases by 50% on secondary markets"
            ),
            EvaluationCase(
                name="Bad Hypothesis Example",
                hypothesis="The moon is made of cheese",
                situation="Scientists analyze moon rock samples brought back by astronauts",
                outcome="The samples consist of basalt and other igneous rocks"
            )
        ]
    else:
        # Interactive mode
        cases = []
        print("\nEnter evaluation cases (press Ctrl+C to finish):")
        try:
            while True:
                print(f"\n--- Case {len(cases) + 1} ---")
                hypothesis = input("Hypothesis: ").strip()
                situation = input("Situation: ").strip()
                outcome = input("Outcome: ").strip()
                name = input("Case name (optional): ").strip() or None
                
                cases.append(EvaluationCase(
                    hypothesis=hypothesis,
                    situation=situation,
                    outcome=outcome,
                    name=name
                ))
        except KeyboardInterrupt:
            print("\n")
    
    if not cases:
        print("No cases to evaluate.")
        return
    
    # Evaluate cases
    print(f"\nEvaluating {len(cases)} cases...")
    results = evaluator.evaluate_batch(cases)
    
    # Print results
    print_results(results)
    
    # Optionally save results
    save = input("\nSave results to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("Filename (default: hypothesis_results.json): ").strip() or "hypothesis_results.json"
        with open(filename, 'w') as f:
            json.dump({
                "model": args.model,
                "cases": [
                    {
                        "name": case.name,
                        "hypothesis": case.hypothesis,
                        "situation": case.situation,
                        "outcome": case.outcome
                    }
                    for case in cases
                ],
                "results": results
            }, f, indent=2)
        print(f"Results saved to {filename}")


if __name__ == "__main__":
    main()