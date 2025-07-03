#!/usr/bin/env python3
"""Explore reasoning_gym tasks to find those with short outputs."""

import reasoning_gym

# Task categories that typically have short outputs
SHORT_OUTPUT_TASKS = [
    # Arithmetic and numeric tasks
    ('arithmetic.addition_2digit', 'Two-digit addition'),
    ('arithmetic.subtraction_2digit', 'Two-digit subtraction'),
    ('arithmetic.multiplication_single', 'Single digit multiplication'),
    ('arithmetic.division_quotient', 'Division quotient only'),
    
    # Logic tasks
    ('logic.yes_no', 'Yes/No logical questions'),
    ('logic.true_false', 'True/False statements'),
    
    # Simple classification
    ('composite.parity', 'Even/Odd classification'),
    ('composite.prime_check', 'Prime number check'),
    
    # Other short answer tasks
    ('algebra.linear_1var', 'Simple linear equations (x value only)'),
    ('geometry.angle_calculation', 'Angle calculations'),
    ('arithmetic.percentage', 'Percentage calculations'),
]

def check_task_outputs():
    """Check various tasks and their typical output lengths."""
    print("Exploring reasoning_gym tasks with typically short outputs...\n")
    
    # First, try to find what tasks are actually available
    available_tasks = []
    
    # Common task names to try
    common_tasks = [
        'shortest_path', 'leg_counting', 'fraction_simplification',
        'base_conversion', 'figlet_font', 'number_sequence', 'n_queens',
        'arithmetic', 'algebra', 'logic', 'geometry'
    ]
    
    for task in common_tasks:
        try:
            ds = reasoning_gym.create_dataset(task, size=1)
            available_tasks.append(task)
        except:
            pass
    
    print(f"Found {len(available_tasks)} available tasks: {available_tasks}\n")
    
    # Now examine each available task
    for task_name in available_tasks:
        try:
            print(f"\n{'='*60}")
            print(f"TASK: {task_name}")
            print('='*60)
            
            # Get a few examples
            ds = reasoning_gym.create_dataset(task_name, size=5, seed=42)
            
            answer_lengths = []
            # Convert to list if needed
            examples = list(ds) if hasattr(ds, '__iter__') else [ds]
            for i, example in enumerate(examples[:5]):
                if isinstance(example, dict):
                    question = example.get('question', example.get('problem', 'N/A'))
                    answer = example.get('answer', example.get('solution', 'N/A'))
                else:
                    question = getattr(example, 'question', 'N/A')
                    answer = getattr(example, 'answer', 'N/A')
                
                answer_str = str(answer)
                answer_lengths.append(len(answer_str))
                
                if i < 3:  # Show first 3 examples
                    print(f"\nExample {i+1}:")
                    print(f"  Q: {question[:100]}...")
                    print(f"  A: {answer_str}")
                    print(f"  Answer length: {len(answer_str)} characters")
            
            avg_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
            print(f"\nAverage answer length: {avg_length:.1f} characters")
            
            if avg_length < 10:
                print("✓ SHORT OUTPUT TASK - Good for minimal token usage!")
            
        except Exception as e:
            print(f"Error with task {task_name}: {e}")
    
    # Summary of short output tasks
    print("\n" + "="*60)
    print("SUMMARY: Tasks with shortest outputs")
    print("="*60)
    
    short_tasks = []
    for task_name in available_tasks:
        try:
            ds = reasoning_gym.create_dataset(task_name, size=10, seed=42)
            total_length = 0
            count = 0
            
            examples = list(ds) if hasattr(ds, '__iter__') else [ds]
            for example in examples[:10]:
                if isinstance(example, dict):
                    answer = example.get('answer', example.get('solution', 'N/A'))
                else:
                    answer = getattr(example, 'answer', 'N/A')
                
                total_length += len(str(answer))
                count += 1
            
            avg_length = total_length / count if count > 0 else 0
            if avg_length < 20:  # Consider "short" if average is under 20 chars
                short_tasks.append((task_name, avg_length))
        except:
            pass
    
    # Sort by average length
    short_tasks.sort(key=lambda x: x[1])
    
    print("\nTasks with shortest average answer lengths:")
    for task, avg_len in short_tasks[:10]:
        print(f"  - {task}: {avg_len:.1f} characters average")

if __name__ == "__main__":
    check_task_outputs()