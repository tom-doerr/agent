#!/usr/bin/env python3
"""Test with intentionally bad hypotheses to verify the system can distinguish."""

import json

bad_hypotheses = [
    {
        "name": "Bad Physics",
        "hypothesis": "Heavy objects fall faster than light objects in a vacuum",
        "situation": "A feather and a hammer are dropped simultaneously on the moon",
        "outcome": "Both objects hit the ground at exactly the same time"
    },
    {
        "name": "Wrong Biology", 
        "hypothesis": "Plants grow better in complete darkness",
        "situation": "Two identical plants, one in sunlight and one in a dark closet for a month",
        "outcome": "The plant in sunlight thrives while the one in darkness dies"
    },
    {
        "name": "Flawed Economics",
        "hypothesis": "Printing more money always makes everyone richer",
        "situation": "A country doubles its money supply in one year",
        "outcome": "Massive inflation occurs and purchasing power decreases"
    },
    {
        "name": "Good Control",
        "hypothesis": "Water expands when frozen due to its molecular structure",
        "situation": "A sealed water bottle is placed in a freezer overnight", 
        "outcome": "The bottle cracks or bulges due to ice expansion"
    }
]

with open('bad_hypothesis_test.json', 'w') as f:
    json.dump(bad_hypotheses, f, indent=2)

print("Created bad_hypothesis_test.json with intentionally bad hypotheses")