#!/usr/bin/env python3

import dspy

lm = dspy.LM("deepseek/deepseek-chat")
dspy.settings.configure(lm=lm, max_tokens=1000, temperature=1.0)


qa = dspy.Predict('question -> answer')

answer = qa(question="What is the capital of France?")
print(f"Answer: {answer}")
