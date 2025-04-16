import json
import os
import subprocess
from argparse import Namespace
from pathlib import Path

from src.embeddings import calculate_embedding
from src.utils import fastcmd_print, get_user_input
from src.vector_database import (
    add_entry,
    fetch_all_commands,
    fetch_similar,
    init_db,
)


def handle_add(args: Namespace) -> bool:
    """
    Handle adding a new command to the database.

    Args:
        args: Command line arguments containing description and command to run
    """
    try:
        # Initialize database if it doesn't exist
        # We don't use a custom db_path here, as it should be patched in tests
        init_db()

        # Calculate embedding for the description
        embedding = calculate_embedding(args.description)

        # Add command to database
        add_entry(
            embedding=embedding,
            command=args.commandrun,
            description=args.description,
        )

        fastcmd_print(f"✅ Command '{args.description}' added successfully.")
        return True
    except Exception as e:
        fastcmd_print(f"❌ Error adding command: {str(e)}")
        return False


def handle_search(args: Namespace) -> bool:
    """
    Handle searching for commands by description.

    Args:
        args: Command line arguments containing description to search for

    Returns:
        bool: True if command found and processed, False otherwise
    """
    try:
        query_embedding = calculate_embedding(args.description)

        # Fetch only the most similar command (top_k=1)
        results = fetch_similar(query_embedding, top_k=1)

        if not results:
            fastcmd_print("❌ No matching commands found.")
            return False

        # Only show the most similar command
        result = results[0]
        distance_percent = int((1 - result["distance"]) * 100)
        fastcmd_print(
            f"[{distance_percent}% match] {result['description']}"
        )
        print(f"\tCommand: {result['command']}")

        # Ask user if they want to execute the command
        print(
            "\tPress 'y' to execute this command, or any other key to cancel:"
        )
        choice = get_user_input()

        if not choice or choice.lower() != 'y':
            fastcmd_print("Operation cancelled.")
            return False

        selected_command = result["command"]
        fastcmd_print(f"Executing: {selected_command}")

        # Execute the selected command
        try:
            result = subprocess.run(
                selected_command, shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                fastcmd_print("Command executed successfully")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                fastcmd_print(f"Command failed with error: {result.stderr}")
                return False
        except Exception as e:
            fastcmd_print(f"Error executing command: {str(e)}")
            return False

    except Exception as e:
        fastcmd_print(f"❌ Error searching for command: {str(e)}")
        return False


def handle_export(args: Namespace) -> bool:
    """
    Handle exporting all commands to a JSON file.

    Args:
        args: Command line arguments containing optional output path

    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        # Initialize database if it doesn't exist
        init_db()

        # Fetch all commands
        commands = fetch_all_commands()

        if not commands:
            fastcmd_print("❌ No commands found in the database.")
            return False

        # Create the export data structure
        export_data = {"commands": commands}

        # Convert to JSON with pretty printing
        json_data = json.dumps(export_data, indent=2)

        # Print to console
        fastcmd_print("Exported commands:")
        print(json_data)

        if args.output:
            output_path = Path(args.output)
        else:
            # Use host's home directory from environment variable
            host_home = os.getenv("HOST_HOME")
            if not host_home:
                raise ValueError("Could not determine host home directory")
            output_path = Path(host_home) / "fastcmd_commands.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(json_data)

        user_home = os.getenv("USER_HOME")
        if not user_home:
            user_home = os.getenv("HOME")
        display_path = f"{user_home}/fastcmd_commands.json"
        fastcmd_print(f"✅ Commands exported to: {display_path}")
        return True
    except Exception as e:
        fastcmd_print(f"❌ Error exporting commands: {str(e)}")
        return False


def handle_import(args: Namespace) -> bool:
    """
    Handle importing commands from a JSON file and adding them to the database.

    Args:
        args: Command line arguments containing the path to the JSON file

    Returns:
        bool: True if import was successful, False otherwise
    """
    try:
        if not args.input:
            fastcmd_print(
                "❌ Please provide the path to the JSON file with --input"
            )
            return False

        host_home = os.getenv("HOST_HOME")
        user_home = os.getenv("USER_HOME")
        input_path_str = args.input

        if user_home and host_home and input_path_str.startswith(user_home):
            container_input_path = input_path_str.replace(
                user_home, host_home, 1
            )
        else:
            container_input_path = input_path_str

        input_path = Path(container_input_path)
        if not input_path.exists():
            fastcmd_print(f"❌ File not found: {input_path}")
            return False

        with open(input_path, "r") as f:
            data = json.load(f)

        commands = data.get("commands", [])
        if not commands:
            fastcmd_print("❌ No commands found in the import file.")
            return False

        init_db()

        imported_count = 0
        for cmd in commands:
            if "description" in cmd and "command" in cmd:
                embedding = calculate_embedding(cmd["description"])
                add_entry(
                    embedding=embedding,
                    command=cmd["command"],
                    description=cmd["description"],
                )
                imported_count += 1
            else:
                fastcmd_print(f"⚠️ Skipping invalid entry: {cmd}")

        fastcmd_print(
            f"✅ Imported {imported_count} commands from {input_path}"
        )
        return True
    except Exception as e:
        fastcmd_print(f"❌ Error importing commands: {str(e)}")
        return False


COMMAND_FACTORY = {
    "add": handle_add,
    "search": handle_search,
    "export": handle_export,
    "import": handle_import,
}
