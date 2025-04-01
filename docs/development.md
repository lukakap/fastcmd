# Development Setup

This document describes how to set up and maintain the development environment for FastCmd.

## Development Environment

The project uses Docker for development to ensure consistency across different development machines. The development environment is containerized and includes all necessary tools and dependencies.

## Docker Images

The project uses several Docker images:

- `fastcmd-base`: Base image for development tools (pytest, lint)
- `fastcmd-app`: Application image for running the command-line tool
- `fastcmd-update-deps`: Image for updating development dependencies
- `fastcmd-update-main-deps`: Image for updating main dependencies

Images are automatically built on first use and cached for subsequent runs. They are only rebuilt when their dependencies change.

## Dependencies

The project uses two sets of dependencies:

### Development Dependencies
Defined in `requirements-dev.list` and locked in `requirements-dev.lock`. These include:

- `openai`: For OpenAI API integration
- `sqlite-vec`: For vector database operations
- `black`: Code formatter
- `isort`: Import sorter
- `flake8`: Code linter
- `mypy`: Type checker

### Main Dependencies
Defined in `requirements.list` and locked in `requirements.lock`. These are the core dependencies needed to run the application.

### Updating Dependencies

To add or update dependencies:

1. For development dependencies:
   - Edit `requirements-dev.list`
   - Run:
     ```bash
     make update-requirements-dev
     ```

2. For main dependencies:
   - Edit `requirements.list`
   - Run:
     ```bash
     make update-requirements
     ```

This will generate new lock files with exact versions.

## Development Commands

### Running Tests

1. Build the base image:
   ```bash
   make base-build
   ```
2. Run tests:
   ```bash
   make tests
   ```

### Running Lint

1. Build the base image:
   ```bash
   make base-build
   ```
2. Run linting:
   ```bash
   make lint
   ```

This will run black, isort, flake8, and mypy checks.

### Running the Application

To run the application:

```bash
make run
```

This will:
1. Build the `fastcmd-app` image with all main dependencies installed
2. Run the application in interactive mode (with `stdin_open` and `tty` enabled)
3. Allow you to input commands through the terminal

The application runs in interactive mode because it's a command-line tool that needs to:
- Accept user input through STDIN
- Display formatted output through TTY
- Handle terminal-specific features
