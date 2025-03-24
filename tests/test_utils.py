import os
from unittest.mock import patch, mock_open
from src.utils import (
    parse_command, 
    check_api_key_existance, 
    set_openai_api_key_for_session,
    check_if_api_key_has_changed,
    get_user_input
)

def test_add_command():
    user_input = "add -c 'echo hello' -d 'Print hello'"
    parsed_command = parse_command(user_input=user_input)

    assert parsed_command.command == 'add'
    assert parsed_command.description == 'Print hello'
    assert parsed_command.commandrun == 'echo hello'

def test_search_command():
    user_input = "search -d 'find files'"
    parsed_command = parse_command(user_input=user_input)
    
    assert parsed_command.command == 'search'
    assert parsed_command.description == 'find files'

def test_set_api_key_flag_global():
    user_input = "--set-api-key"
    parsed_command = parse_command(user_input=user_input)
    
    assert parsed_command.set_api_key is True
    assert parsed_command.command is None

def test_set_api_key_with_command():
    user_input = "add -c 'ls -la' -d 'List files' --set-api-key sk-1234567890"
    parsed_command = parse_command(user_input=user_input)
    
    assert parsed_command.command == 'add'
    assert parsed_command.description == 'List files'
    assert parsed_command.commandrun == 'ls -la'
    assert parsed_command.set_api_key == 'sk-1234567890'

def test_check_api_key_existance_with_key():
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        with patch('src.utils.fastcmd_print') as mock_print:
            result = check_api_key_existance()
            assert result is True
            mock_print.assert_called_once()

def test_check_api_key_existance_without_key():
    with patch.dict(os.environ, {'OPENAI_API_KEY': ''}, clear=True):
        result = check_api_key_existance()
        assert result is False

def test_check_if_api_key_has_changed():
    from argparse import Namespace
    args = Namespace(set_api_key='new-api-key')
    
    with patch('src.utils.save_api_key') as mock_save:
        with patch.dict(os.environ, {}):
            check_if_api_key_has_changed(args)
            mock_save.assert_called_once_with('new-api-key')
            assert os.environ.get('OPENAI_API_KEY') == 'new-api-key'

def test_set_openai_api_key_for_session_from_config():
    with patch('src.utils.load_api_key', return_value='config-key'):
        with patch.dict(os.environ, {}):
            set_openai_api_key_for_session()
            assert os.environ.get('OPENAI_API_KEY') == 'config-key'

def test_set_openai_api_key_for_session_from_env():
    with patch('src.utils.load_api_key', return_value=None):
        with patch('src.utils.save_api_key') as mock_save:
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-key'}):
                set_openai_api_key_for_session()
                mock_save.assert_called_once_with('env-key')

def test_set_openai_api_key_for_session_from_input():
    with patch('src.utils.load_api_key', return_value=None):
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}, clear=True):
            with patch('src.utils.input', return_value='input-key'):
                with patch('src.utils.fastcmd_print'):
                    set_openai_api_key_for_session()
                    assert os.environ.get('OPENAI_API_KEY') == 'input-key'

def test_get_user_input_regular():
    with patch('src.utils.input', return_value='test command'):
        result = get_user_input()
        assert result == 'test command'

def test_get_user_input_exit():
    with patch('src.utils.input', return_value='exit'):
        result = get_user_input()
        assert result is None

def test_get_user_input_quit():
    with patch('src.utils.input', return_value='quit'):
        result = get_user_input()
        assert result is None