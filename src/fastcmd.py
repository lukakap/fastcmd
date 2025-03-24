


from utils import get_user_input, parse_command, print_instructions, set_openai_api_key_for_session
from commands import COMMAND_FACTORY


def main():
    print_instructions()
    set_openai_api_key_for_session()

    while True:
        user_input = get_user_input()
        if user_input is None:
            break

        try:
            args = parse_command(user_input)
        except SystemExit:
            continue

        func_command_runner = COMMAND_FACTORY[args.command]
        func_command_runner(args=args, context={})

        
main()