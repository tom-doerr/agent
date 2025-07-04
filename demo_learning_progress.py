#!/usr/bin/env python3
"""Demo showing actual learning progress with edit distance"""

import dspy

def edit_distance(s1, s2):
    """Calculate edit distance between strings"""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    return dp[m][n]

# Configure DSPy
dspy.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=30))

# Create transformer
transformer = dspy.ChainOfThought("input_string, target_string -> transformed")

# Track performance over time
performance = []

print("=== Learning to Transform Strings ===")
print("Task: Transform input to match target\n")

# Multiple rounds to show learning
targets = [
    ("hello", "jello"),   # Change h to j
    ("cat", "hat"),       # Change c to h  
    ("dog", "fog"),       # Change d to f
    ("hello", "jello"),   # Repeat to see improvement
    ("cat", "hat"),       # Repeat
    ("dog", "fog"),       # Repeat
]

for round_num, (input_str, target) in enumerate(targets):
    result = transformer(input_string=input_str, target_string=target)
    output = result.transformed
    
    # Calculate performance
    distance = edit_distance(output, target)
    perfect = (distance == 0)
    
    print(f"Round {round_num + 1}: '{input_str}' → '{target}'")
    print(f"  Output: '{output}' | Distance: {distance} {'✓' if perfect else '✗'}")
    
    performance.append(distance)

# Show learning progress
print("\n=== Performance Over Time ===")
print("Edit distances:", performance)
print(f"First 3 attempts: avg distance = {sum(performance[:3])/3:.1f}")
print(f"Last 3 attempts:  avg distance = {sum(performance[3:])/3:.1f}")

if sum(performance[3:])/3 < sum(performance[:3])/3:
    print("\n✓ Model improved with practice!")
else:
    print("\n✗ No clear improvement (would need optimization)")