#!/usr/bin/env python3


from simpledspy import predict, chain_of_thought
import os
from subprocess import run, PIPE, STDOUT, Popen
from typing import Literal
import rich
import dspy
import sys

# dspy.configure(lm=dspy.LM('openrouter/google/gemini-2.5-flash-preview'))
dspy.configure(lm=dspy.LM('deepseek/deepseek-reasoner', max_tokens=20000))

#dspy.configure(lm=dspy.LM('openrouter/deepseek/deepseek-r1-0528'))



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
                #command = predict(self.context, description='Please generate a shell command for the command variable for running with subprocess.run. The command should be a string that can be executed in the shell.')
                command = chain_of_thought(self.context, description='Please generate a shell command for the command variable for running with subprocess.run. The command should be a string that can be executed in the shell.')
                self.context += f'Command: {command}\n'
                print(f'Running command: {command}')
                # result = run(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
                process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT, text=True, bufsize=1)
                self.context += f'Process started with PID: {process.pid}\n'
                self.context += f'Command output:\n'
                for line in process.stdout:
                    print(line, end='')
                    self.context += f'{line}'

                process.wait()
                self.context += f'Process finished with return code: {process.returncode}\n'
#                if result.returncode == 0:
#                    print(f'Command output: {result.stdout}')
#                    self.context += f'Command output: {result.stdout}\n'
#                else:
#                    print(f'Command error: {result.stderr}')
#                    self.context += f'Command error: {result.stderr}\n'
            elif action == 'reply_to_user':
                response = predict(self.context)
                self.context += f'Response: {response}\n'
                # fancy and colored
                rich.print(f'[bold green]Agent response:[/bold green] {response}')
            else:
                print(f'Unknown action: {action}')
                self.context += f'Unknown action: {action}\n'
            options = ['True', 'False']
            done = predict(self.context, options, description='Is the agent done for now or does it need to continue working to finish open tasks? Output True or False. Reply True if we need to wait for the user to reply, False if we can continue working. Only output True if you are sure that the agent is done and no further actions are needed.')
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

if len(sys.argv) > 1 and '--' in sys.argv:
    # if we have a command line argument, use it as the initial user input
    initial_input = ' '.join(sys.argv[1:]).replace('--', '')
    print(f'Initial input: {initial_input}')
    agent.forward(initial_input)
while True:
    user_input = input('> ')
    agent.forward(user_input)


