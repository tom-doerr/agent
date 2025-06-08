#!/usr/bin/env python3


import os
from subprocess import run, PIPE, STDOUT, Popen
from typing import Literal
import rich
import dspy
import sys
import termcolor
import argparse
from simpledspy import predict, chain_of_thought, configure

class Agent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.context = ''

    def forward(self, user_input: str) -> None:
        self.context += f'User: {user_input}\n'
        while True:
            action = predict(self.context, description='Please select an action for the agent to take. The options are: run_command, reply_to_user. Output only the action name, no other text. If you are not sure, output "reply_to_user".')
            self.context += f'Agent action: {action}\n'
            if action == 'run_command':
                command = chain_of_thought(self.context, description='Please generate a shell command for the command variable for running with subprocess.run. The command should be a string that can be executed in the shell.')
                self.context += f'Command: {command}\n'
                rich.print(f'[bold blue]Running command:[/bold blue] {command}')

                process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT, text=True, bufsize=1)
                output = ''
                for line in process.stdout:
                    print(line, end='')
                    output += line

                process.wait()
                self.context += f'Process finished with return code: {process.returncode}\n'
                number_additional_chars = 0
                for i in range(3):
                    output_frame = output[-(1000+number_additional_chars):]
                    done_viewing_output, number_additional_chars, text_to_add_to_context = predict(
                        self.context,
                        output_frame,
                        description='Please generate a string that should be added to the context. The string should. The text_to_add_to_context string will be all that we know from the output, so make sure to include all important information but do not fill the context with garbage.  If you are done viewing the output, output "True". If you need to view more output, output "False" and the number of additional characters to view abouve the output you have already seen.',
                    )
                    if bool(done_viewing_output):
                        rich.print(f'[bold green]Done viewing output:[/bold green] {done_viewing_output}')
                        self.context += f'Done viewing output: {done_viewing_output}\n'
                        rich.print(f'[bold green]Text to add to context:[/bold green] {text_to_add_to_context}')
                        self.context += f'Text to add to context: {text_to_add_to_context}\n'
                        self.context += text_to_add_to_context + '\n'
                        break

                    rich.print(f'[bold red]Not done viewing output, need to view more:[/bold red] {done_viewing_output}, additional chars: {number_additional_chars}')

                self.context += f'Process started with PID: {process.pid}\n'
                self.context += f'Command output:\n'

            elif action == 'reply_to_user':
                response = predict(self.context)
                self.context += f'Response: {response}\n'
                rich.print(f'[bold green]Agent response:[/bold green] {response}')
            else:
                print(f'Unknown action: {action}')
                self.context += f'Unknown action: {action}\n'
            options = ['True', 'False']
            done = predict(self.context, options, description='Is the agent done for now or does it need to continue working to finish open tasks? Output True or False. Reply True if we need to wait for the user to reply, False if we can continue working. Only output True if you are sure that the agent is done and no further actions are needed.')
            self.context += f'Done: {done}\n'
            if done == 'True':
                break
            elif done == 'False':
                continue
            else:
                print(f'Unknown option: {done}')
                self.context += f'Unknown option: {done}\n'



MODEL_MAP = {
        'flash': 'openrouter/google/gemini-2.5-flash-preview',
        'r1': 'openrouter/deepseek/deepseek-r1-0528',
        'dv3': 'openrouter/deepseek/deepseek-chat-v3-0324',
}

def parse_args():
    parser = argparse.ArgumentParser(description='Run a simple agent with dspy.')
    parser.add_argument('--lm', type=str, default='dv3',
                        help='The language model to use for the agent.')
    parser.add_argument('--max-tokens', type=int, default=20000,
                        help='The maximum number of tokens to use for the language model.')
    parser.add_argument('--disable-logging', action='store_false', dest='logging',
                        help='Disable logging to the console.')
    return parser.parse_args()


def main():
    args = parse_args()
    dspy.configure(lm=dspy.LM(MODEL_MAP[args.lm], max_tokens=args.max_tokens))
    configure(logging_enabled=args.logging)

    agent = Agent()

    if len(sys.argv) > 1 and '--' in sys.argv:
        # if we have a command line argument, use it as the initial user input
        initial_input = ' '.join(sys.argv[1:]).replace('--', '')
        print(f'Initial input: {initial_input}')
        agent.forward(initial_input)
    while True:
        user_input = input(termcolor.colored('> ', 'green'))  # green prompt
        agent.forward(user_input)

if __name__ == '__main__':
    main()
