#!/usr/bin/env python3
"""
DSPy program for abbreviation decoding
"""

import dspy
from typing import List, Tuple
import json
from dataclasses import dataclass

@dataclass
class AbbreviationExample:
    abbreviation: str
    expanded: str
    
class AbbreviationSignature(dspy.Signature):
    """Expand abbreviation where each letter represents the first letter of a word."""
    
    abbreviation = dspy.InputField(desc="Letters representing first letter of each word (e.g., 'wdyt')")
    expanded = dspy.OutputField(desc="Full sentence with words starting with those letters (e.g., 'what do you think')")

class AbbreviationExpander(dspy.Module):
    def __init__(self):
        super().__init__()
        self.expand = dspy.ChainOfThought(AbbreviationSignature)
    
    def forward(self, abbreviation: str) -> dspy.Prediction:
        # Parse abbreviation to get letter count
        letters = list(abbreviation.replace(".", "").replace(" ", ""))
        
        # Add context about the number of words needed
        enhanced_abbrev = f"{abbreviation} ({len(letters)} words)"
        
        result = self.expand(abbreviation=enhanced_abbrev)
        return result

class AbbreviationValidator(dspy.Module):
    """Validates that expansion matches abbreviation pattern"""
    
    def forward(self, abbreviation: str, expansion: str) -> bool:
        letters = list(abbreviation.replace(".", "").replace(" ", "").lower())
        words = expansion.strip().rstrip('.,!?;:').split()
        
        if len(words) != len(letters):
            return False
            
        for i, word in enumerate(words):
            if not word or word[0].lower() != letters[i]:
                return False
                
        return True

class MultiAttemptExpander(dspy.Module):
    """Makes multiple attempts to find valid expansions"""
    
    def __init__(self, num_attempts=5):
        super().__init__()
        self.num_attempts = num_attempts
        self.expander = AbbreviationExpander()
        self.validator = AbbreviationValidator()
        
    def forward(self, abbreviation: str) -> List[str]:
        valid_expansions = []
        
        for _ in range(self.num_attempts):
            try:
                expansion = self.expander(abbreviation=abbreviation).expanded
                if self.validator(abbreviation=abbreviation, expansion=expansion):
                    valid_expansions.append(expansion)
            except:
                continue
                
        return valid_expansions

def create_training_data():
    """Create training examples for the abbreviation expander"""
    
    examples = [
        # Common conversational
        ("wdyt", "what do you think"),
        ("htmtd", "how to make this decision"),
        ("hayd", "how are you doing"),
        ("tiavg", "time is a valuable gift"),
        ("wdyw", "what do you want"),
        ("hdyk", "how do you know"),
        ("idk", "i don't know"),
        ("ttyl", "talk to you later"),
        
        # Business/professional
        ("pfa", "please find attached"),
        ("eod", "end of day"),
        ("cob", "close of business"),
        ("fyi", "for your information"),
        ("asap", "as soon as possible"),
        
        # Technical
        ("api", "application programming interface"),
        ("cpu", "central processing unit"),
        ("ram", "random access memory"),
        ("sql", "structured query language"),
        
        # Longer examples
        ("tiwagt", "time is what a gift takes"),
        ("hdywmt", "how do you want me to"),
        ("icbwtt", "i can't believe what they think"),
        ("wdywtdt", "what do you want to do today"),
        
        # Creative/varied
        ("tmr", "the morning rain"),
        ("bsd", "beautiful sunny day"),
        ("lmg", "let me go"),
        ("syat", "see you around tomorrow"),
        ("hmb", "hit me back"),
        ("gmab", "give me a break"),
        
        # More complex
        ("plmkwtd", "please let me know what to do"),
        ("idkwyttm", "i don't know what you're talking to me"),
        ("hdywmth", "how do you want me to help"),
        ("tqftc", "thank you for the call"),
        ("wywttm", "when you want to talk more"),
        
        # Very long examples  
        ("hdywmthtywtwtt", "how do you want me to help that you will think was the test"),
        ("icttmiabttd", "i can take the meeting if anyone brings the technical documentation"),
        ("wwtdanbtgf", "we want to discuss a new business that generates funds"),
    ]
    
    return [AbbreviationExample(abbr, exp) for abbr, exp in examples]

def save_dataset(examples: List[AbbreviationExample], filename: str):
    """Save dataset to JSON file"""
    with open(filename, 'w') as f:
        for example in examples:
            json.dump({"abbreviation": example.abbreviation, "expanded": example.expanded}, f)
            f.write('\n')

def load_dataset(filename: str) -> List[AbbreviationExample]:
    """Load dataset from JSON file"""
    examples = []
    with open(filename, 'r') as f:
        for line in f:
            data = json.loads(line)
            examples.append(AbbreviationExample(data['abbreviation'], data['expanded']))
    return examples

if __name__ == "__main__":
    # Create and save training data
    training_data = create_training_data()
    save_dataset(training_data, "abbrev_train.jsonl")
    print(f"Created {len(training_data)} training examples")
    
    # Test the basic expander
    lm = dspy.LM(model="openrouter/google/gemini-2.0-flash-001", api_key_env_var="OPENROUTER_API_KEY", max_tokens=300)
    dspy.configure(lm=lm)
    
    expander = AbbreviationExpander()
    
    # Test a few examples
    test_abbrevs = ["wdyt", "htmtd", "hayd"]
    
    print("\nTesting basic expander:")
    for abbrev in test_abbrevs:
        try:
            result = expander(abbreviation=abbrev)
            print(f"{abbrev} -> {result.expanded}")
        except Exception as e:
            print(f"{abbrev} -> Error: {e}")