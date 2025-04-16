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

    parser_export = subparsers.add_parser(
        "export", help="Export all commands to JSON format"
    )
    parser_export.add_argument(
        "-o",
        "--output",
        help=(
            "Path to save the exported JSON file. "
            "If not specified, saves to Desktop with timestamp."
        ),
    )
    parser_export.add_argument(
        "--set-api-key", type=str, metavar="API_KEY", help=argparse.SUPPRESS
    )

    # Subparser for 'import' command
    parser_import = subparsers.add_parser(
        "import", help="Import commands from a JSON file"
    )
    parser_import.add_argument(
        "-i", "--input", required=True, help="Path to the JSON file to import"
    )
    parser_import.add_argument(
        "--set-api-key", type=str, metavar="API_KEY", help=argparse.SUPPRESS
    )

    return parser.parse_args(shlex.split(user_input))


def check_if_api_key_has_changed(args: Namespace) -> None:
    if args.set_api_key:
        save_api_key(args.set_api_key)
        os.environ["OPENAI_API_KEY"] = args.set_api_key


def fastcmd_print(
    value: str, with_front_text: bool = True, with_front_space: bool = True
) -> None:
    if with_front_text:
        print(f"fastcmd> {value}")
    elif with_front_space:
        print(f"         {value}")
    else:
        print(value)


def print_instructions() -> None:
    fastcmd_print("\nWelcome to FastCmd!", with_front_text=False)
    fastcmd_print("\nAvailable commands:\n", with_front_text=False)

    commands = [
        (
            "add -c <command> -d <description>",
            "Add a new command with a description",
        ),
        ("search -d <description>", "Search saved commands by description"),
        (
            "export [-o <output_path>]",
            "Export all commands to a JSON file (default path if not provided)",
        ),
        ("import -i <input_path>", "Import commands from a JSON file"),
        ("exit / quit", "Exit the FastCmd application"),
    ]

    for cmd, desc in commands:
        fastcmd_print(f"  {cmd:<35} {desc}", with_front_text=False)

    fastcmd_print("\nNotes:", with_front_text=False)
    fastcmd_print(
        "  - Use quotes around <command> and <description> if they contain spaces",
        with_front_text=False,
    )
    fastcmd_print(
        "  - The JSON file used in export/import must follow FastCmd format",
        with_front_text=False,
    )
    fastcmd_print("", with_front_text=False)


def print_command_match(result: dict, distance_percent: int) -> None:
    fastcmd_print(f"\n🎯 [{distance_percent}% match]", with_front_text=False)

    fastcmd_print(
        f"\n🔹 Command: {result['command']}",
        with_front_text=False,
        with_front_space=False,
    )
    fastcmd_print(
        f"📝 Description : {result['description']}\n",
        with_front_text=False,
        with_front_space=False,
    )

    # fastcmd_print(
    #     f"\n▶ You can copy the command and use it\n",
    #     with_front_text=False,
    #     with_front_space=False
    # )
