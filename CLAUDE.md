# FastCmd Development Guidelines

## Build/Development Commands
- Install dependencies: `pip install -r requirements.txt`
- Install for development: `pip install -e .`
- Run application: `python fastcmd.py`
- Build executable: `pyinstaller --onefile fastcmd.py`
- Run tests: `pytest`
- Run specific test: `pytest tests/test_file.py::TestClass::test_function`
- Run tests with coverage: `pytest --cov=fastcmd tests/`

## Code Style Guidelines
- **Imports**: Standard library first, third-party packages second, local modules last
- **Formatting**: 4-space indentation, max line length of 100 characters
- **Type Hints**: Not currently used, consider adding for new code
- **Naming Conventions**: 
  - Functions/variables: snake_case
  - Constants: UPPER_SNAKE_CASE
  - Classes: PascalCase
- **Error Handling**: Use try/except blocks with specific exceptions
- **Documentation**: Add docstrings for functions and modules
- **Testing**: Write pytest unit tests for all new functionality

## Project Structure
- Main application logic in `fastcmd.py`
- CLI handling in `cli.py`
- Tests in the `tests/` directory
- Command data stored in `fastcmd-commands.json`
- Cross-platform support via `.py`, `.sh`, and `.bat` files