#!/usr/bin/env python3


from simpledspy import predict
import os
from subprocess import run, PIPE
from typing import Literal
import rich
import dspy
dspy.configure(lm=dspy.LM('openrouter/google/gemini-2.5-flash-preview'))



class ActionSelector(dspy.Signature):
    context: str = dspy.InputField(description='The current context of the conversation, including user input and previous actions.')
    selected_action: Literal['run_command', 'reply_to_user'] = dspy.OutputField()


class Agent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.select_action = dspy.Predict(ActionSelector)
        #self.done = dspy.Predict('context, options -> done')
        self.context = ''

    def print_context(self):
        # use rich
        rich.print(self.context)


    def forward(self, user_input: str) -> None:
        self.context += f'User: {user_input}\n'
        while True:
            action = self.select_action(context=self.context).selected_action
            self.context += f'Agent action: {action}\n'
            #print(f'Context: {self.context}')
            if action == 'run_command':
                command = predict(self.context, description='Please generate a shell command for the command variable for running with subprocess.run. The command should be a string that can be executed in the shell.')
                self.context += f'Command: {command}\n'
                print(f'Running command: {command}')
                result = run(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
                if result.returncode == 0:
                    print(f'Command output: {result.stdout}')
                    self.context += f'Command output: {result.stdout}\n'
                else:
                    print(f'Command error: {result.stderr}')
                    self.context += f'Command error: {result.stderr}\n'
            elif action == 'reply_to_user':
                response = predict(self.context)
                self.context += f'Response: {response}\n'
                # fancy and colored
                rich.print(f'[bold green]Agent response:[/bold green] {response}')
            else:
                print(f'Unknown action: {action}')
                self.context += f'Unknown action: {action}\n'
            options = ['True', 'False']
            done = predict(self.context, options, description='Is the agent done for now or does it need to continue working to finish open tasks? Output True or False. Reply True if we need to wait for the user to reply, False if we can continue working.')
            self.context += f'Done: {done}\n'
            #self.print_context()
            if done == 'True':
                break
            elif done == 'False':
                continue
            else:
                print(f'Unknown option: {done}')
                self.context += f'Unknown option: {done}\n'


agent = Agent()
while True:
    user_input = input('> ')
    agent.forward(user_input)


input()
context = ''
while True:
    user_input = input('> ')
    context += f'\nUser: {user_input}\n'
#    response = predict(user_input)
#    print(response)
    available_actions = ['run_command', 'reply_to_user']
    while True:
        #action = predict(context, available_actions, description='Choose an action for the agent to perform') 
        context += f'\nAgent action: {action}\n'
        if action == 'run_command':
            command = predict(context)
            context += f'\nCommand: {command}\n'
            print(f'Running command: {command}')
            result = run(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
            if result.returncode == 0:
                print(f'Command output: {result.stdout}')
                context += f'\nCommand output: {result.stdout}\n'
            else:
                print(f'Command error: {result.stderr}')
                context += f'\nCommand error: {result.stderr}\n'
        elif action == 'reply_to_user':
            response = predict(context)
            context += f'\nResponse: {response}\n'
            print(f'Agent response: {response}')
        else:
            print(f'Unknown action: {action}')
            context += f'\nUnknown action: {action}\n'


        options = ['True', 'False']
        done = predict(context, options)
        context += f'\nDone: {done}\n'
        if done == 'True':
            break
        elif done == 'False':
            continue
        else:
            print(f'Unknown option: {done}')
            context += f'\nUnknown option: {done}\n'





