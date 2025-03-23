

from typing import Optional
import shlex
import argparse
from argparse import Namespace

def get_user_input() -> Optional[str]:
    user_input = input("fastcmd> ")
    if user_input.lower() in ["exit", "quit"]:
        return None
    return user_input


def parse_command(user_input: str) -> Namespace:
    parser = argparse.ArgumentParser(description='FastCmd - Command Line Tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Subparser for 'add' command
    parser_add = subparsers.add_parser('add', help='Add a new command')
    parser_add.add_argument('-d', '--description', required=True, help='Description of the command')
    parser_add.add_argument('-c', '--commandrun', required=True, help='The command to run')

    # Subparser for 'run' command
    parser_run = subparsers.add_parser('run', help='Run a command')
    parser_run.add_argument('-d', '--description', required=True, help='Description of the command')

    # Subparser for 'openaikey' command
    parser_run = subparsers.add_parser('key', help="Add or See OpenAI Key")
    parser_run.add_argument('-a', '--add', required=False, help="ADD YOUR OPENAI KEY")
    parser_run.add_argument('-s', '--see', required=False, help="SEE YOUR OPENAI KEY")

    return parser.parse_args(shlex.split(user_input))

def fastcmd_print(value: str) -> None:
    print(f"fastcmd> {value}")
