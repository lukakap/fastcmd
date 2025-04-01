import subprocess
from argparse import Namespace

from src.embeddings import calculate_embedding
from src.utils import fastcmd_print, get_user_input
from src.vector_database import add_entry, fetch_similar, init_db


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

        # Find similar commands (default top_k=3)
        results = fetch_similar(query_embedding, top_k=1)

        if not results:
            fastcmd_print("❌ No matching commands found.")
            return False

        fastcmd_print(f"Found {len(results)} matching commands:")
        for i, result in enumerate(results):
            distance_percent = int((1 - result["distance"]) * 100)
            fastcmd_print(
                f"{i+1}. [{distance_percent}% match] {result['description']}"
            )
            fastcmd_print(f"   Command: {result['command']}")

        # Ask user if they want to execute a command
        fastcmd_print(
            "Enter the number of the command to execute, or press Enter to cancel:"
        )
        choice = get_user_input()

        if (
            not choice
            or not choice.isdigit()
            or int(choice) < 1
            or int(choice) > len(results)
        ):
            fastcmd_print("Operation cancelled.")
            return False

        selected_command = results[int(choice) - 1]["command"]
        fastcmd_print(f"Executing: {selected_command}")

        # Execute the selected command
        try:
            result = subprocess.run(
                selected_command, shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                # If command was successful
                fastcmd_print("Command executed successfully")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                # If command failed
                fastcmd_print(f"Command failed with error: {result.stderr}")
                return False
        except Exception as e:
            fastcmd_print(f"Error executing command: {str(e)}")
            return False

    except Exception as e:
        fastcmd_print(f"❌ Error searching for command: {str(e)}")
        return False


COMMAND_FACTORY = {
    "add": handle_add,
    "search": handle_search,
}
