#!/usr/bin/env python3

import dspy


dspy.settings.configure(lm=dspy.LM('deepseek/deepseek-chat', max_tokens=100, temperature=1.5))

program = dspy.Predict('input -> output')

dataset = [dspy.Example(input=str(i)).with_inputs('input') for i in range(100)]


def score(example, pred, trace=None):
    # Handle None predictions
    if pred is None:
        return -100  # Very low score for None predictions
    
    # Get the output from the prediction object
    y = pred.output if hasattr(pred, 'output') else str(pred)
    
    # Handle None output
    if y is None:
        return -100
    
    # Ensure y is a string
    y = str(y)
    
    return y.count("a") - 2 * max(0, len(y) - 10)

optimizer = dspy.SIMBA(
        metric=score,
)

best_program = optimizer.compile(program, trainset=dataset)
print('best_program:', best_program)




