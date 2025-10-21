#!/usr/bin/env python3

import os
import dspy
import sys

# Configure DeepSeek v3.2 with reasoning enabled
lm = dspy.LM(
    model="openrouter/deepseek/deepseek-v3.2-exp",
    temperature=1.0,
    max_tokens=16000,
    cache=True,
    extra_body={
        "reasoning": {
            # "effort": "high",  # high = ~80% tokens for reasoning
            "effort": "low", 
            "exclude": False   # Include reasoning in response
        }
    }
)

dspy.configure(lm=lm)

reply_module = dspy.Predict('user_message -> agent_reply', system_prompt="You are a helpful assistant.")
coding_module = dspy.Predict('user_message -> python_code')
safety_checker_module = dspy.Predict('user_message, python_code -> is_safe: bool')

while True:
    user_message = input(">  ")
    agent_reply = reply_module(user_message=user_message)
    print(agent_reply)
    python_code = coding_module(user_message=user_message).python_code
    print(f'Generated code:\n{python_code}')
    is_safe = safety_checker_module(user_message=user_message, python_code=python_code)
    if is_safe:
        print("Executing code:")
        exec(python_code)



