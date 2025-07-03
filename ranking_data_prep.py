#!/usr/bin/env python3
"""
Utility for preparing and managing ranking datasets.

This script helps:
1. Generate predictions from a model
2. Create/edit ground truth rankings
3. Convert between formats
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
import sys
sys.path.append(str(Path(__file__).parent))

from dspy_ranking_optimizer import PairwiseRanker, load_latest_ranker
from utils.io import load_ndjson, save_ndjson


def create_editable_ranking_file(items: List[Dict[str, Any]], output_path: Path):
    """Create a human-editable NDJSON file with items in random order.
    
    Human can reorder lines in their text editor to create ground truth ranking.
    """
    import random
    shuffled = items.copy()
    random.shuffle(shuffled)
    
    # Save as NDJSON with comments showing the title
    with open(output_path, 'w') as f:
        for item in shuffled:
            # Add a comment field with the title for easy identification
            item_copy = item.copy()
            text = item_copy.get('text', '')
            item_copy['_title'] = text.split('\n')[0][:100]
            f.write(json.dumps(item_copy) + '\n')


def parse_ranking_file(ranking_path: Path) -> List[Dict[str, Any]]:
    """Parse a human-edited NDJSON ranking file.
    
    Simply loads the NDJSON in order - the human has already reordered the lines.
    Removes the temporary _title field if present.
    """
    items = load_ndjson(ranking_path)
    
    # Remove the _title helper field
    for item in items:
        if '_title' in item:
            del item['_title']
    
    return items


def rank_items_with_model(items: List[Dict[str, Any]], ranker: PairwiseRanker) -> List[Dict[str, Any]]:
    """Rank items using pairwise comparisons with the model.
    
    Uses a simple bubble sort with model comparisons.
    """
    # Create a copy to sort
    ranked_items = items.copy()
    n = len(ranked_items)
    
    print(f"Ranking {n} items using model...")
    comparisons = 0
    
    # Bubble sort with model comparisons
    for i in range(n):
        for j in range(0, n - i - 1):
            # Compare adjacent items
            result = ranker(
                item_a=ranked_items[j]['text'],
                item_b=ranked_items[j + 1]['text']
            )
            comparisons += 1
            
            # Swap if B is better than A
            if result.better_item == 'B':
                ranked_items[j], ranked_items[j + 1] = ranked_items[j + 1], ranked_items[j]
        
        print(f"Pass {i+1}/{n} complete ({comparisons} comparisons so far)")
    
    print(f"Ranking complete! Total comparisons: {comparisons}")
    return ranked_items


def main():
    parser = argparse.ArgumentParser(description="Ranking data preparation utility")
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Create editable ranking file
    create_parser = subparsers.add_parser('create', help='Create editable ranking file')
    create_parser.add_argument('input', help='Input NDJSON file')
    create_parser.add_argument('output', help='Output editable ranking file')
    
    # Parse ranking file back to NDJSON
    parse_parser = subparsers.add_parser('parse', help='Parse edited ranking file')
    parse_parser.add_argument('ranking_file', help='Edited NDJSON ranking file')
    parse_parser.add_argument('output', help='Output ordered NDJSON file')
    
    # Generate model predictions
    predict_parser = subparsers.add_parser('predict', help='Generate model predictions')
    predict_parser.add_argument('input', help='Input NDJSON file to rank')
    predict_parser.add_argument('output', help='Output ranked NDJSON file')
    predict_parser.add_argument('--model', help='Model path (default: latest)', default=None)
    
    args = parser.parse_args()
    
    if args.command == 'create':
        # Create editable ranking file
        items = load_ndjson(Path(args.input))
        create_editable_ranking_file(items, Path(args.output))
        print(f"Created editable ranking file: {args.output}")
        print(f"Edit this file to reorder items (best first), then use 'parse' command")
        
    elif args.command == 'parse':
        # Parse edited ranking back to NDJSON
        ordered_items = parse_ranking_file(Path(args.ranking_file))
        save_ndjson(ordered_items, Path(args.output))
        print(f"Parsed ranking file and saved {len(ordered_items)} ordered items to: {args.output}")
        
    elif args.command == 'predict':
        # Generate predictions using model
        print("Loading model...")
        if args.model:
            ranker = PairwiseRanker()
            ranker.load(args.model)
        else:
            ranker = load_latest_ranker()
        
        items = load_ndjson(Path(args.input))
        ranked_items = rank_items_with_model(items, ranker)
        save_ndjson(ranked_items, Path(args.output))
        print(f"Saved model-ranked items to: {args.output}")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()