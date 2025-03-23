from src.cli import parse_command

def test_add_command():
    user_input = "add -c 'echo hello' -d 'Print hello'"
    parsed_command = parse_command(user_input=user_input)

    assert parsed_command.command == 'add'
    assert parsed_command.description == 'Print hello'
    assert parsed_command.commandrun == 'echo hello'

