# Development Guide

## Prerequisites

- Docker
- Docker Compose
- Make

## Development Setup

### Building the Base Image

The base image contains all development dependencies. To build it:

```bash
make base-build
```

### Updating Dependencies

#### Development Dependencies

To update development dependencies:

```bash
make update-requirements-dev
```

This will:
1. Build the update-deps container
2. Generate a new `requirements-dev.lock` file

#### Main Dependencies

To update main application dependencies:

```bash
make update-requirements
```

This will:
1. Build the update-main-deps container
2. Generate a new `requirements.lock` file

### Running Tests

To run the test suite:

```bash
make tests
```

This will:
1. Use the `fastcmd-base` image
2. Run pytest with the test configuration
3. Display test results

### Linting

To run the linter:

```bash
make lint
```

This will:
1. Run black for code formatting
2. Run isort for import sorting
3. Run flake8 for style checking
4. Run mypy for type checking

### Running the Application

To run the application:

```bash
make run
```

This will:
1. Create necessary configuration directories in your home folder (`~/.fastcmd` and `~/.fastcmd/db`)
2. Set proper permissions for the directories
3. Build the `fastcmd-app` image with all main dependencies installed
4. Run the application in interactive mode (with `stdin_open` and `tty` enabled)
5. Mount your local code directory for development
6. Mount configuration and database directories for persistence
7. Set all required environment variables
8. Allow you to input commands through the terminal

The application runs in interactive mode because it's a command-line tool that needs to:
- Accept user input through STDIN
- Display formatted output through TTY
- Handle terminal-specific features

### Cleaning Configuration

If you need to start fresh or if you're experiencing issues with the configuration:

```bash
make clean-config
```

This will:
1. Remove the `.fastcmd` directory from your home folder
2. Delete all configuration files and database
3. Allow you to start with a clean slate

Note: This will remove your OpenAI API key and any saved commands, so use it carefully.

### Publishing

To publish a new version:

```bash
make publish
```

This will:
1. Build the production image
2. Tag it as `lukakap/fastcmd:latest`
3. Push it to Docker Hub
