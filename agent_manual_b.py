#!/usr/bin/env python3

import dspy
import sys
from rich import print

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
# TODO
# satisfaction 
# surprise
# plan
# wm update
# wm retrieve

knowledge = ["I'm an AI agent", "I'm based on DSPy"]

class KnowledgeUpdater(dspy.Module):
    """Module for updating the knowledge of the agent."""
    def __init__(self, knowledge):
        self.problem_generator = dspy.Predict('knowledge, observation -> question, solution', description="Generates a question which should only be answerable when having both knowledge and observation or the observation alone. It should not be answerable just with the knowledge. Also give the solution to the question")
        self.knowledge_observation_solver = dspy.Predict('question, knowledge -> reasoning, solution')
        self.knowledge_solver = dspy.Predict('question, knowledge -> reasoning, solution')
        self.knowledge_observation_updater = dspy.Predict('observation, reasoning, solution -> index, search, replace')
        self.knowledge = knowledge

    def forward(self, observation: str) -> None:
        for i in range(10):
            # question, solution = self.problem_generator(knowledge=self.knowledge, observation=observation)
            challenge = self.problem_generator(knowledge=self.knowledge, observation=observation)
            # print(f"[bold yellow]Generated question:[/bold yellow] {question}; [bold yellow]Proposed solution:[/bold yellow] {solution}")
            print(f"[bold yellow]Generated question:[/bold yellow] {challenge.question}; [bold yellow]Proposed solution:[/bold yellow] {challenge.solution}")
            reasoning, solution = self.knowledge_observation_solver(question=question, knowledge=self.knowledge)
            if solution.strip().lower() == "unknown":
                reasoning, solution = self.knowledge_solver(question=question, knowledge=self.knowledge)
            index, search, replace = self.knowledge_observation_updater(observation=observation, reasoning=reasoning, solution=solution)
            if index.strip().lower() == "none":
                break
            index = int(index)
            if index >= len(self.knowledge):
                self.knowledge.append(replace)
            else:
                self.knowledge[index] = replace


print(dspy.inspect_history(n=5))
print(type(dspy.inspect_history(n=5)))

if len(sys.argv) > 1:
    user_message = sys.argv[1]
else:
    user_message = input(">  ")

knowledge_updater = KnowledgeUpdater(knowledge=knowledge)
while True:
    knowledge_updater(observation=user_message)
    agent_reply = reply_module(user_message=user_message)
    print(agent_reply)
    python_code = coding_module(user_message=user_message).python_code
    print(f'Generated code:\n{python_code}')
    is_safe = safety_checker_module(user_message=user_message, python_code=python_code)
    print(f'is_safe: {is_safe}')
    if is_safe:
        print("Executing code:")
        exec(python_code)


    user_message = input(">  ")

