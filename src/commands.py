import os
from utils import fastcmd_print

def handle_add(args, context):
    # handle add command to db --- args.description | args.commandrun
    fastcmd_print(f"✅ Command '{args.description}' added.")

def handle_search(args, context):
    # args.description is passed and we need to
    # 1) fetch similiar command from db
    # 2) ask user to run it, or just return it
    # 3) do action
    fastcmd_print(f"✅ Command fetched.")


COMMAND_FACTORY = {
    "add": handle_add,
    "search": handle_search,
}
