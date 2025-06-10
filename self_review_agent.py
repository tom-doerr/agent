#!/usr/bin/env python3

import dspy
from simpledspy import predict, chain_of_thought, configure
from model_map import MODEL_MAP
import sys
from rich.console import Console

console = Console()

class SelfReviewAgent(dspy.Module):
    def __init__(self, max_iterations=3):
        super().__init__()
        self.max_iterations = max_iterations
        self.generate = dspy.Predict("task -> response")
        self.criticize = dspy.Predict("task, response -> feedback")
        self.improve = dspy.Predict("task, response, feedback -> improved_response")
        self.should_continue = dspy.Predict("feedback -> continue: 'yes' or 'no'")

    def forward(self, task):
        history = []
        # Initial generation
        response = self.generate(task=task).response
        history.append(f"Initial response: {response}")
        
        for i in range(self.max_iterations):
            # Get feedback on current response
            feedback = self.criticize(task=task, response=response).feedback
            history.append(f"\n\nIteration {i+1} feedback: {feedback}")
            
            # Decide if we should continue
            decision = self.should_continue(feedback=feedback).should_continue.lower()
            if 'no' in decision:
                history.append("\nStopping: Feedback indicates no further improvements needed")
                break
                
            # Generate improved version
            improved = self.improve(task=task, response=response, feedback=feedback).improved_response
            history.append(f"\nImproved response: {improved}")
            response = improved
        
        return "\n".join(history), response

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Self-Review Agent with Iterative Improvement')
    parser.add_argument('task', type=str, help='The task to complete')
    parser.add_argument('--lm', type=str, default='flash', help='Model to use for predictions')
    parser.add_argument('--iterations', type=int, default=3, help='Max iterations for improvement')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    model_string = MODEL_MAP.get(args.lm, args.lm)
    
    lm = dspy.LM(model_string, max_tokens=4000, temperature=0.7)
    dspy.configure(lm=lm)
    
    agent = SelfReviewAgent(max_iterations=args.iterations)
    history, final_response = agent.forward(args.task)
    
    console.print("\n[bold]Final Response:[/bold]")
    console.print(final_response)
    console.print("\n[bold]Process History:[/bold]")
    console.print(history)
    
    sys.exit(0)
