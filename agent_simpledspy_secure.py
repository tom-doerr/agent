#!/usr/bin/env python3
"""Secure version of agent_simpledspy with command validation and resource limits."""

import os
import sys
import argparse
from typing import Literal
from pathlib import Path
import rich
import dspy
import termcolor
from simpledspy import predict, chain_of_thought, configure
from model_map import MODEL_MAP

# Import security components
from safe_command_agent import SafeCommandAgent
from utils.command_executor import CommandResult


class SecureSimpleDSPyAgent(SafeCommandAgent):
    """SimpleDSPy agent with secure command execution."""
    
    def __init__(self, lm_config=None, **kwargs):
        # Initialize parent with security features
        super().__init__(
            name="secure_simpledspy",
            command_whitelist_mode=True,
            max_command_memory_mb=512,
            max_command_cpu_seconds=30,
            max_context_tokens=8000,  # Larger for DSPy agent
            **kwargs
        )
        
        # Configure DSPy if needed
        if lm_config:
            dspy.configure(lm=lm_config)
        
        # Add commonly needed commands to whitelist
        safe_commands = [
            'ls', 'cat', 'grep', 'find', 'echo', 'pwd', 'cd',
            'git', 'python', 'pip', 'npm', 'node', 'curl', 'wget',
            'mkdir', 'touch', 'cp', 'mv', 'head', 'tail', 'wc',
            'sort', 'uniq', 'diff', 'sed', 'awk', 'cut', 'tr',
            'date', 'whoami', 'which', 'env', 'ps', 'kill',
            'tar', 'gzip', 'gunzip', 'zip', 'unzip',
        ]
        for cmd in safe_commands:
            self.add_allowed_command(cmd)
    
    def _decide_action(self) -> str:
        """Use DSPy to decide next action."""
        context_messages = self.get_context_messages()
        context_str = self._messages_to_string(context_messages)
        
        action = predict(
            context_str,
            description='Please select an action for the agent to take. '
                       'The options are: run_command, reply_to_user. '
                       'Output only the action name, no other text. '
                       'If you are not sure, output "reply_to_user".'
        )
        
        # Log decision
        self.context_manager.add('system', f'Agent action: {action}')
        return action
    
    def _generate_command(self) -> str:
        """Use DSPy to generate a shell command."""
        context_messages = self.get_context_messages()
        context_str = self._messages_to_string(context_messages)
        
        command = chain_of_thought(
            context_str,
            description='Please generate a shell command for running with subprocess. '
                       'The command should be a string that can be executed in the shell. '
                       'IMPORTANT: Only use basic, safe commands. Avoid rm, sudo, or system modifications.'
        )
        
        # Log generated command
        self.context_manager.add('system', f'Generated command: {command}')
        return command
    
    def _process_output(self, output: str) -> str:
        """Use DSPy to process command output."""
        context_messages = self.get_context_messages()
        context_str = self._messages_to_string(context_messages)
        
        # Process output in chunks if too large
        max_output_size = 2000
        if len(output) > max_output_size:
            # Take beginning and end
            output_preview = output[:1000] + "\n...[truncated]...\n" + output[-1000:]
        else:
            output_preview = output
        
        summary = predict(
            context_str,
            output_preview,
            description='Please generate a summary of the command output. '
                       'Include all important information but keep it concise. '
                       'Focus on results, errors, or key findings.'
        )
        
        return summary
    
    def _generate_response(self) -> str:
        """Use DSPy to generate response to user."""
        context_messages = self.get_context_messages()
        context_str = self._messages_to_string(context_messages)
        
        response = predict(
            context_str,
            description='Generate a helpful response to the user based on the conversation context.'
        )
        
        return response
    
    def _should_continue(self) -> bool:
        """Use DSPy to decide if agent should continue."""
        context_messages = self.get_context_messages()
        context_str = self._messages_to_string(context_messages)
        
        done = predict(
            context_str,
            ['True', 'False'],
            description='Is the agent done for now or does it need to continue working? '
                       'Output True if done (waiting for user), False if should continue. '
                       'Only output True if you are sure no further actions are needed.'
        )
        
        self.context_manager.add('system', f'Continue decision: {done}')
        return done == 'False'
    
    def _messages_to_string(self, messages):
        """Convert messages to string format for DSPy."""
        parts = []
        for msg in messages:
            role = msg['role'].capitalize()
            content = msg['content']
            parts.append(f"{role}: {content}")
        return '\n'.join(parts)
    
    def process_user_input(self, user_input: str):
        """Process user input with secure command execution."""
        # Add to context
        self.context_manager.add('user', user_input)
        
        while True:
            # Decide action
            action = self._decide_action()
            rich.print(f'[bold blue]Action:[/bold blue] {action}')
            
            if action == 'run_command':
                # Generate command
                command = self._generate_command()
                rich.print(f'[bold blue]Running command:[/bold blue] {command}')
                
                # Execute securely
                result = self.execute_command(command, timeout=30)
                
                # Display result
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    rich.print(f'[bold red]Error:[/bold red] {result.stderr}')
                
                # Process output for context
                output_summary = self._process_output(
                    result.stdout if result.stdout else result.stderr
                )
                
                # Add to context
                status = "successful" if result.return_code == 0 else "failed"
                self.context_manager.add(
                    'assistant',
                    f"Executed command '{command}' ({status}). {output_summary}"
                )
                
            elif action == 'reply_to_user':
                # Generate response
                response = self._generate_response()
                rich.print(f'[bold green]Agent response:[/bold green] {response}')
                
                # Add to context
                self.context_manager.add('assistant', response)
                
            else:
                rich.print(f'[bold red]Unknown action:[/bold red] {action}')
                self.context_manager.add('system', f'Unknown action: {action}')
            
            # Check if should continue
            if not self._should_continue():
                break
    
    def run_interactive(self):
        """Run agent in interactive mode."""
        print(f"\n{self.name} started (secure mode)")
        print("Type /help for commands or /quit to exit\n")
        
        while self.running:
            try:
                user_input = input(termcolor.colored('> ', 'green')).strip()
                
                if user_input.startswith('/'):
                    # Handle special commands
                    output = self.handle_command(user_input)
                    if output:
                        print(output)
                else:
                    # Process with DSPy
                    self.process_user_input(user_input)
                    
                    # Check context usage
                    stats = self.get_context_stats()
                    if stats['usage_percentage'] > 80:
                        rich.print(
                            f"[yellow]Context {stats['usage_percentage']:.1f}% full "
                            f"({stats['total_tokens']}/{stats['max_tokens']} tokens)[/yellow]"
                        )
                        
            except KeyboardInterrupt:
                print("\nUse /quit to exit")
            except Exception as e:
                rich.print(f"[bold red]Error:[/bold red] {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run a secure SimpleDSPy agent with command validation.'
    )
    parser.add_argument(
        '--lm', type=str, default='dv3',
        help='The language model to use for the agent.'
    )
    parser.add_argument(
        '--max-tokens', type=int, default=20000,
        help='The maximum number of tokens for the language model.'
    )
    parser.add_argument(
        '--disable-logging', action='store_false', dest='logging',
        help='Disable logging to the console.'
    )
    parser.add_argument(
        '--disable-whitelist', action='store_true',
        help='Disable command whitelist (DANGEROUS - for testing only)'
    )
    parser.add_argument(
        '--max-memory', type=int, default=512,
        help='Maximum memory in MB for command execution'
    )
    parser.add_argument(
        '--max-cpu', type=int, default=30,
        help='Maximum CPU seconds for command execution'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Configure DSPy
    lm_config = dspy.LM(
        MODEL_MAP[args.lm],
        max_tokens=args.max_tokens,
        cache=False
    )
    dspy.configure(lm=lm_config)
    configure(logging_enabled=args.logging)
    
    # Create secure agent
    agent = SecureSimpleDSPyAgent(
        lm_config=lm_config,
        command_whitelist_mode=not args.disable_whitelist,
        max_command_memory_mb=args.max_memory,
        max_command_cpu_seconds=args.max_cpu,
    )
    
    # Process initial input if provided
    if len(sys.argv) > 1 and '--' in sys.argv:
        initial_input = ' '.join(sys.argv[1:]).replace('--', '').strip()
        if initial_input:
            print(f'Processing: {initial_input}')
            agent.process_user_input(initial_input)
    
    # Run interactive mode
    agent.run_interactive()


if __name__ == '__main__':
    main()