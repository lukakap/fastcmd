import json
import subprocess
import os
from argparse import Namespace
from pathlib import Path

from src.embeddings import calculate_embedding
from src.utils import fastcmd_print, get_user_input
from src.vector_database import add_entry, fetch_similar, init_db, fetch_all_commands


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
        export_data = {
            "commands": commands
        }
        
        # Convert to JSON with pretty printing
        json_data = json.dumps(export_data, indent=2)
        
        # Print to console
        fastcmd_print("Exported commands:")
        print(json_data)
        
        if args.output:
            output_path = Path(args.output)
        else:
            # Use host's home directory from environment variable
            host_home = os.getenv('HOST_HOME')
            if not host_home:
                raise ValueError("Could not determine host home directory")
            output_path = Path(host_home) / "fastcmd_commands.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            f.write(json_data)
            
        user_home = os.getenv('USER_HOME')
        if not user_home:
            user_home = os.getenv('HOME')
        display_path = f"{user_home}/fastcmd_commands.json"
        fastcmd_print(f"✅ Commands exported to: {display_path}")
        return True
    except Exception as e:
        fastcmd_print(f"❌ Error exporting commands: {str(e)}")
        return False


COMMAND_FACTORY = {
    "add": handle_add,
    "search": handle_search,
    "export": handle_export,
}
