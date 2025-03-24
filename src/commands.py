import os
from cli import fastcmd_print

def handle_add(args, context):
    # handle add command to db --- args.description | args.commandrun
    fastcmd_print(f"✅ Command '{args.description}' added.")

def handle_key(args, context):
    if args.add:
        os.environ["OPENAI_API_KEY"] = args.add
        fastcmd_print("🔑 OpenAI key set successfully.")
    elif args.see:
        key = os.environ.get("OPENAI_API_KEY", None)
        fastcmd_print(f"🔑 Your OpenAI key: {key}" if key else "⚠️ OpenAI key not set.")

def handle_run(args, context):
    # args.description is passed and we need to
    # 1) fetch similiar command from db
    # 2) ask user to run it, or just return it
    # 3) do action
    fastcmd_print(f"✅ Command fetched.")


COMMAND_FACTORY = {
    "add": handle_add,
    "run": handle_run,
    "key": handle_key,
}
