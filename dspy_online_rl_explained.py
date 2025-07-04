#!/usr/bin/env python3
"""How collected feedback improves the model"""

import dspy

# The key insight: DSPy optimizers use examples to find better prompts/demonstrations

def show_how_feedback_helps():
    """Demonstrate how collected data improves predictions"""
    
    # 1. Collect feedback data (inputs, outputs, rewards)
    feedback_data = [
        # Good examples (high reward)
        {"inputs": {"request": "Give me coffee"}, 
         "output": "Could you please give me some coffee?", 
         "reward": 10.0},
        
        # Bad examples (low reward)  
        {"inputs": {"request": "Send report"},
         "output": "Send report now",
         "reward": 0.0},
    ]
    
    # 2. Convert to DSPy training format
    trainset = []
    for item in feedback_data:
        if item["reward"] > 5:  # Only use good examples
            example = dspy.Example(
                request=item["inputs"]["request"],
                polite_request=item["output"]  # This becomes the "label"
            ).with_inputs("request")
            trainset.append(example)
    
    # 3. DSPy optimizer uses these examples to:
    #    - Add them as demonstrations in the prompt
    #    - Learn what patterns work well
    #    - Generate better instructions
    
    print("Good examples become demonstrations:")
    for ex in trainset:
        print(f"  Input: {ex.request}")
        print(f"  Output: {ex.polite_request}\n")
    
    # 4. After optimization, the predictor has learned:
    #    "When I see 'Give me X', I should output 'Could you please...'"
    #    because those examples had high rewards
    
    return trainset


# The magic: DSPy optimizers improve prompts using your feedback
"""
Before optimization:
  Prompt: "request -> polite_request"
  
After optimization with your feedback:
  Prompt: "request -> polite_request
          
          Examples:
          Input: Give me coffee
          Output: Could you please give me some coffee?
          
          Input: Send the files
          Output: Could you please send the files?"
"""

if __name__ == "__main__":
    print("=== How Feedback Improves the Model ===\n")
    trainset = show_how_feedback_helps()
    
    print("The optimizer adds these as few-shot examples!")
    print("Next predictions will follow the learned pattern.")