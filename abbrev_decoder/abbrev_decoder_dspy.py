#!/usr/bin/env python3
"""
Abbreviation Decoder using DSPy optimized program
"""

import argparse
import os
import sys
import json
import dspy
from typing import List, Tuple
from abbrev_dspy_program import AbbreviationExpander, AbbreviationValidator

class DSPyAbbrevDecoder:
    def __init__(self, model: str = "openrouter/google/gemini-2.0-flash-001", optimized_path: str = None):
        self.model = model
        
        # Configure DSPy
        lm = dspy.LM(
            model=model,
            api_key_env_var="OPENROUTER_API_KEY",
            max_tokens=300,
            temperature=0.7
        )
        dspy.configure(lm=lm)
        
        # Load optimized program if available
        if optimized_path and os.path.exists(optimized_path):
            print(f"Loading optimized program from {optimized_path}", file=sys.stderr)
            self.expander = AbbreviationExpander()
            self.expander.load(optimized_path)
        else:
            print("Using base program (no optimization loaded)", file=sys.stderr)
            self.expander = AbbreviationExpander()
            
        self.validator = AbbreviationValidator()
    
    def decode(self, abbreviation: str, num_attempts: int = 5) -> List[Tuple[str, float]]:
        """Decode abbreviation and return candidates"""
        results = []
        seen = set()
        
        # Parse abbreviation
        letters = list(abbreviation.replace(".", "").replace(" ", "").lower())
        print(f"Decoding {len(letters)} letters: {' '.join(letters)}", file=sys.stderr)
        
        for i in range(num_attempts):
            try:
                # Get expansion
                result = self.expander(abbreviation=abbreviation)
                expansion = result.expanded
                
                # Validate
                if self.validator(abbreviation=abbreviation, expansion=expansion):
                    if expansion not in seen:
                        seen.add(expansion)
                        # DSPy doesn't provide logprobs easily, so use attempt order as score
                        score = 1.0 / (i + 1)
                        results.append((expansion, score))
                else:
                    print(f"Invalid expansion: {expansion}", file=sys.stderr)
            except Exception as e:
                print(f"Error in attempt {i+1}: {e}", file=sys.stderr)
                
        # Sort by score (higher is better)
        results.sort(key=lambda x: x[1], reverse=True)
        return results

def main():
    parser = argparse.ArgumentParser(
        description="Decode abbreviated sentences using DSPy",
        epilog="Example: abbrev_decoder_dspy 'htmtd' -> 'how to make this decision'"
    )
    parser.add_argument(
        "abbreviation",
        nargs="?",
        help="Abbreviation to decode (e.g., 'htmtd')"
    )
    parser.add_argument(
        "--model", "-m",
        default="openrouter/google/gemini-2.0-flash-001",
        help="LLM model to use (default: openrouter/google/gemini-2.0-flash-001)"
    )
    parser.add_argument(
        "--attempts", "-a",
        type=int,
        default=5,
        help="Number of generation attempts (default: 5)"
    )
    parser.add_argument(
        "--optimized", "-o",
        default="abbrev_expander_optimized.json",
        help="Path to optimized program (default: abbrev_expander_optimized.json)"
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
    
    # Create decoder
    decoder = DSPyAbbrevDecoder(model=args.model, optimized_path=args.optimized)
    
    if args.interactive:
        print("DSPy Abbreviation Decoder - Interactive Mode")
        print("Type abbreviations (e.g., 'htmtd') and press Enter")
        print("Type 'quit' or Ctrl+C to exit\n")
        
        while True:
            try:
                abbrev = input("abbrev> ").strip()
                if abbrev.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if not abbrev:
                    continue
                    
                print("\nDecoding...", file=sys.stderr)
                results = decoder.decode(abbrev, num_attempts=args.attempts)
                
                if not results:
                    print("No valid expansions found.")
                else:
                    print("\nTop expansions:")
                    for i, (text, score) in enumerate(results, 1):
                        print(f"{i}. {text} (confidence: {score:.2f})")
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
            
        results = decoder.decode(args.abbreviation, num_attempts=args.attempts)
        
        if args.json:
            output = {
                "abbreviation": args.abbreviation,
                "expansions": [
                    {"text": text, "confidence": score}
                    for text, score in results
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            if not results:
                print("No valid expansions found.")
            else:
                for i, (text, score) in enumerate(results, 1):
                    print(f"{i}. {text} (confidence: {score:.2f})")

if __name__ == "__main__":
    main()