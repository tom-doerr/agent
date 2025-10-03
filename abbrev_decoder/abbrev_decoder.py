#!/usr/bin/env python3
"""
Abbreviation Decoder - Type only first letters of words, get full sentences.
Uses LLMs with logprobs to decode abbreviated input into likely sentences.
"""

import argparse
import os
import sys
from typing import List, Tuple, Optional
import litellm
from litellm import completion
import heapq
from dataclasses import dataclass
import json
import re

@dataclass
class Candidate:
    text: str
    log_prob: float
    abbrev_used: str
    
    def __lt__(self, other):
        # Higher log prob = better, so negate for min heap
        return -self.log_prob < -other.log_prob

class AbbrevDecoder:
    def __init__(self, model: str = "openrouter/google/gemini-2.0-flash-lite-001:free", top_k: int = 5, beam_width: int = 10, num_attempts: int = 10):
        self.model = model
        self.top_k = top_k
        self.beam_width = beam_width
        self.num_attempts = num_attempts
        
    def parse_abbreviation(self, abbrev: str) -> List[str]:
        """Parse abbreviation into list of letters, handling dots as separators."""
        # Remove spaces and split on dots if present
        if '.' in abbrev:
            # Split on dots and take first letter of each part
            parts = abbrev.split('.')
            letters = []
            for part in parts:
                part = part.strip()
                if part:
                    letters.extend(list(part))
            return letters
        else:
            # Just remove spaces and split into individual letters
            return list(abbrev.replace(" ", ""))
        
    def create_prompt(self, abbrev: str, letters: List[str]) -> str:
        """Create a prompt that encourages the model to expand abbreviations."""
        letter_str = ' '.join(letters).upper()
        examples = ""
        
        # Add examples to help the model understand the pattern
        if len(letters) <= 5:
            examples = """
Examples:
- w d y t → what do you think
- h t m t d → how to make this decision
- t i a v g → time is a valuable gift

"""
        
        return f"""Expand this abbreviation where each letter represents the first letter of a word in a sentence. Return ONLY the expanded sentence, nothing else.

{examples}Abbreviation letters: {letter_str}

The sentence must have exactly {len(letters)} words, with each word starting with the corresponding letter in order.

Expanded sentence:"""

    def create_constrained_prompt(self, abbrev: str, letters: List[str], attempt: int) -> str:
        """Create alternative prompts with different contexts to get varied results."""
        letter_str = ' '.join(letters).upper()
        
        contexts = [
            "casual conversation",
            "technical discussion", 
            "business communication",
            "creative writing",
            "everyday speech",
            "formal writing",
            "social media",
            "academic writing"
        ]
        
        context = contexts[attempt % len(contexts)]
        
        return f"""Complete this sentence where each word must start with the given letters in order.
Context: {context}
Letters: {letter_str} ({len(letters)} words total)

Think of a natural sentence that would be used in {context}. Each word MUST start with the corresponding letter.

Sentence:"""

    def get_candidates(self, abbrev: str) -> List[Candidate]:
        """Generate multiple candidate expansions using the LLM."""
        candidates = []
        letters = self.parse_abbreviation(abbrev)
        
        if not letters:
            return []
            
        print(f"Decoding {len(letters)} letters: {' '.join(letters)}", file=sys.stderr)
        
        for i in range(self.num_attempts):
            # Add variation to prompt to get different results
            temp = min(0.7 + (i * 0.05), 2.0)  # Increase temperature for more variety, cap at 2.0
            
            # Use different prompt strategies
            if i < self.num_attempts // 2:
                prompt = self.create_prompt(abbrev, letters)
            else:
                prompt = self.create_constrained_prompt(abbrev, letters, i)
            
            try:
                response = completion(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert at expanding abbreviations into full sentences. Each letter in the input represents the first letter of a word. Always return exactly the number of words specified."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temp,
                    max_tokens=100,
                    logprobs=True,
                    top_logprobs=5
                )
                
                expanded = response.choices[0].message.content.strip()
                # Remove any trailing punctuation for verification
                expanded_clean = expanded.rstrip('.,!?;:')
                
                # Verify the expansion matches the abbreviation
                if self.verify_expansion(letters, expanded_clean):
                    # Calculate total log probability
                    total_logprob = 0
                    if hasattr(response.choices[0], 'logprobs') and response.choices[0].logprobs:
                        for token_data in response.choices[0].logprobs.content:
                            if token_data.logprob:
                                total_logprob += token_data.logprob
                    
                    candidates.append(Candidate(
                        text=expanded,
                        log_prob=total_logprob,
                        abbrev_used=abbrev
                    ))
                else:
                    print(f"Attempt {i+1}: Invalid expansion '{expanded}' for letters {letters}", file=sys.stderr)
                    
            except Exception as e:
                print(f"Error generating candidate {i+1}: {e}", file=sys.stderr)
                continue
        
        # Remove duplicates while preserving best scores
        seen = {}
        for candidate in candidates:
            if candidate.text not in seen or candidate.log_prob > seen[candidate.text].log_prob:
                seen[candidate.text] = candidate
        
        return list(seen.values())
    
    def verify_expansion(self, letters: List[str], expanded: str) -> bool:
        """Verify that the expanded text matches the abbreviation pattern."""
        words = expanded.split()
        
        if len(words) != len(letters):
            return False
            
        for i, word in enumerate(words):
            if not word or word[0].lower() != letters[i].lower():
                return False
                
        return True
    
    def decode(self, abbrev: str) -> List[Tuple[str, float]]:
        """Decode abbreviation and return top candidates with scores."""
        candidates = self.get_candidates(abbrev)
        
        if not candidates:
            # Try with more attempts if initial attempts failed
            print("No valid candidates found, trying with more attempts...", file=sys.stderr)
            self.num_attempts = min(self.num_attempts * 2, 30)
            candidates = self.get_candidates(abbrev)
        
        # Sort by log probability (highest first)
        candidates.sort(reverse=True, key=lambda x: x.log_prob)
        
        # Return top k results
        results = []
        for candidate in candidates[:self.top_k]:
            results.append((candidate.text, candidate.log_prob))
            
        return results

def main():
    parser = argparse.ArgumentParser(
        description="Decode abbreviated sentences using LLMs",
        epilog="Example: abbrev_decoder 'htmtd' -> 'how to make this decision'\n" +
               "Example: abbrev_decoder 'h.a.y.d' -> 'how are you doing'"
    )
    parser.add_argument(
        "abbreviation",
        nargs="?",
        help="Abbreviation to decode (e.g., 'htmtd' or 'h.a.y.d')"
    )
    parser.add_argument(
        "--model", "-m",
        default="openrouter/google/gemini-2.0-flash-lite-001:free",
        help="LLM model to use (default: openrouter/google/gemini-2.0-flash-lite-001:free)"
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=5,
        help="Number of top candidates to show (default: 5)"
    )
    parser.add_argument(
        "--attempts", "-a",
        type=int,
        default=10,
        help="Number of generation attempts (default: 10)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    # Check for API key
    if "openrouter" in args.model and not os.environ.get("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable not set", file=sys.stderr)
        print("Get your API key from https://openrouter.ai/keys", file=sys.stderr)
        sys.exit(1)
    elif "gpt" in args.model and not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    decoder = AbbrevDecoder(model=args.model, top_k=args.top_k, num_attempts=args.attempts)
    
    if args.interactive:
        print("Abbreviation Decoder - Interactive Mode")
        print("Type abbreviations (e.g., 'htmtd') and press Enter")
        print("Use dots to separate letter groups (e.g., 'h.a.y.d')")
        print("Type 'quit' or Ctrl+C to exit\n")
        
        while True:
            try:
                abbrev = input("abbrev> ").strip()
                if abbrev.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if not abbrev:
                    continue
                    
                print("\nDecoding...", file=sys.stderr)
                results = decoder.decode(abbrev)
                
                if not results:
                    print("No valid expansions found.")
                else:
                    print("\nTop expansions:")
                    for i, (text, score) in enumerate(results, 1):
                        print(f"{i}. {text} (score: {score:.2f})")
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
    
    else:
        # Single abbreviation mode
        if not args.abbreviation:
            parser.print_help()
            sys.exit(1)
            
        results = decoder.decode(args.abbreviation)
        
        if args.json:
            output = {
                "abbreviation": args.abbreviation,
                "expansions": [
                    {"text": text, "log_probability": score}
                    for text, score in results
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            if not results:
                print("No valid expansions found.")
                print("Try with more attempts: --attempts 20", file=sys.stderr)
            else:
                for i, (text, score) in enumerate(results, 1):
                    print(f"{i}. {text} (score: {score:.2f})")

if __name__ == "__main__":
    main()