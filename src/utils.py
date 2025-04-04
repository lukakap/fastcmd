import argparse
import os
import shlex
from argparse import Namespace
from typing import Optional

from src.config import load_api_key, save_api_key


def get_user_input() -> Optional[str]:
    user_input = input("fastcmd> ")
    if user_input.lower() in ["exit", "quit"]:
        return None
    return user_input


def check_api_key_existance() -> bool:
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        fastcmd_print("🔑 OpenAI key is added")
        return True
    else:
        return False


def set_openai_api_key_for_session() -> None:
    """
    Retrieves the OpenAI API key from the environment variable OPENAI_API_KEY.
    If not set, prompts the user to input it via CLI and then sets it for the
    current session.

    Returns:
        str: The OpenAI API key.
    """
    config_api_key = load_api_key()
    if config_api_key:
        os.environ["OPENAI_API_KEY"] = config_api_key
        return

    env_api_key = os.getenv("OPENAI_API_KEY")
    if env_api_key:
        save_api_key(env_api_key)
        return

    fastcmd_print("Please enter your OPENAI_API_KEY:")
    api_key = input("fastcmd> OPENAI_API_KEY: ").strip()
    if not api_key:
        raise ValueError("API key cannot be empty.")
    os.environ["OPENAI_API_KEY"] = api_key
    save_api_key(api_key)
    fastcmd_print("OPENAI_API_KEY has been set to the config")


def parse_command(user_input: str) -> Namespace:
    parser = argparse.ArgumentParser(description="FastCmd - Command Line Tool")
    parser.add_argument(
        "--set-api-key",
        action="store_true",
        help="Set or update your OpenAI API key.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Subparser for 'add' command
    parser_add = subparsers.add_parser("add", help="Add a new command")
    parser_add.add_argument(
        "-d", "--description", required=True, help="Description of the command"
    )
    parser_add.add_argument(
        "-c", "--commandrun", required=True, help="The command to run"
    )
    parser_add.add_argument(
        "--set-api-key", type=str, metavar="API_KEY", help=argparse.SUPPRESS
    )

    # Subparser for 'search' command
    parser_search = subparsers.add_parser("search", help="search a command")
    parser_search.add_argument(
        "-d", "--description", required=True, help="Description of the command"
    )
    parser_search.add_argument(
        "--set-api-key", type=str, metavar="API_KEY", help=argparse.SUPPRESS
    )

    return parser.parse_args(shlex.split(user_input))


def check_if_api_key_has_changed(args: Namespace) -> None:
    if args.set_api_key:
        save_api_key(args.set_api_key)
        os.environ["OPENAI_API_KEY"] = args.set_api_key


def fastcmd_print(value: str, with_front_text: bool = True) -> None:
    if with_front_text:
        print(f"fastcmd> {value}")
    else:
        print(f"         {value}")


def print_instructions() -> None:
    fastcmd_print("Welcome to FastCmd! Available commands:")
    fastcmd_print(
        "  add -c '<command>' -d '<description>'  : Add a new command with description",
        with_front_text=False,
    )
    fastcmd_print(
        "  search -d '<description>'             : Search for a command by description",
        with_front_text=False,
    )
    fastcmd_print(
        "  exit/quit                             : Exit the application",
        with_front_text=False,
    )
    fastcmd_print("", with_front_text=False)
