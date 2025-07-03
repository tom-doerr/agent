#!/usr/bin/env python3


import dspy
import sys
from rich import print as rp
import asyncio
import mlflow
import pydantic
import random
import os

mlflow.set_tracking_uri('http://localhost:5002')
mlflow.set_experiment('iter_improvement')
mlflow.dspy.autolog()

# lm = dspy.LM('ollama_chat/deepseek-r1:7b', api_base='http://localhost:11434',api_key='')
lm = dspy.LM('openrouter/deepseek/deepseek-r1-0528', max_tokens=40000)
# lm = dspy.LM('openrouter/google/gemini-2.5-flash-lite-preview-06-17')
dspy.configure(lm=lm)

critic = dspy.Predict('artifact, aspect -> critique', instructions="Critique the artifact based on the aspect. The critique should be in depth, constructive")
refiner = dspy.Predict('artifact, critique -> refined_artifact', instructions="Refine the artifact based on the critique.")
aspect_generator = dspy.Predict('user_request -> aspects: list[str]', instructions="Generate a list of aspects to critique the artifact. Include a wide range of aspects and generate many. Include aspects such as: correctness, completeness, clarity, conciseness, relevance, originality, creativity, depth, and specificity, as well as any other aspects that are relevant to the user request. They should be dimensions in which we measure the quality of the artifact.")
initial_artifact_generator = dspy.Predict('user_request -> artifact', instructions="Generate an initial artifact based on the user request. The initial artifact should be in depth, constructive and specific to the user request.")

if len(sys.argv) > 1:
    # user_request = ''.join(sys.argv[1:]) if len(sys.argv) > 1 else ''
    user_request = ' '.join(sys.argv[1:])
else:
    user_request = sys.stdin.read().strip()

# artifact = ''
critique = ''

aspects = aspect_generator(user_request=user_request).aspects
ARTIFACT_FILE_LOCATION = 'artifact.txt'
if os.path.exists(ARTIFACT_FILE_LOCATION):
    with open(ARTIFACT_FILE_LOCATION, 'r') as f:
        artifact = f.read()
else:
    artifact = initial_artifact_generator(user_request=user_request).artifact
rp(f'[cyan]aspects:[/] {aspects}')

for i in range(100):
    artifact = refiner(artifact=artifact, critique=critique).refined_artifact
    rp(f'[cyan]artifact:[/] {artifact}')
    with open(ARTIFACT_FILE_LOCATION, 'w') as f:
        f.write(artifact)
    aspect = random.choice(aspects)
    rp(f'[cyan]aspect:[/] {aspect}')
    critique = critic(artifact=artifact, aspect=aspect).critique
    rp(f'[cyan]critique:[/] {critique}')










# system_state_info = ''
#return_value = ''
#python_code_run_history = []
#command_run_history = []


# command = command_generator(user_request=user_request, system_state_info=system_state_info).command
#while True:
    # python_code_to_run = python_code_generator(user_request=user_request, system_state_info=system_state_info, python_code_run_history=python_code_run_history, return_value=return_value).python_code_to_run
    #command = command_generator(user_request=user_request, system_state_info=system_state_info, command_run_history=command_run_history, return_value=return_value).command
    ## print('python_code_to_run: ', python_code_to_run)
    #rp(f'[cyan]command[/]: {command}')
    #result = safety_checker(command=command, command_run_history=command_run_history, user_request=user_request)
    #command_is_safe_to_execute, reasoning = result.command_is_safe_to_execute, result.reasoning
    #color = 'green' if command_is_safe_to_execute else 'red'
    #rp(f'[cyan]command_is_safe_to_execute:[/] [{color}] {command_is_safe_to_execute} [/]')
    #print('reasoning: ', reasoning)
    #if command_is_safe_to_execute:
    #    try:
    #        #return_value = exec(python_code_to_run)
    #        result = subprocess.run(command, shell=True, capture_output=True, text=True)
    #        return_value = str(result)
    #        print('return_value: ', return_value)
    #    except Exception as e:
    #        return_value = str(e)
    #else:
    #    return_value = f"Command wasn't executed because it was determined to be unsafe. Reasoning: {reasoning}"

    ## python_code_run_history.append({'code': python_code_to_run, 'return_value': return_value})
    #command_run_history.append({'command': command, 'return_value': return_value})
    #is_finished_result = is_finished_checker(user_request=user_request, system_state_info=system_state_info, command_run_history=command_run_history, return_value=return_value)
    #rp(f'[cyan]is_finished:[/] {is_finished_result.is_finished}')
    #print('is_finished_result.reasoning: ', is_finished_result.reasoning)
    #if is_finished_result.is_finished:
    #    rp(f'[green]Finished![/]')
        # break
        # user_request = sys.stdin.read().strip()
        # colored






#
#


















