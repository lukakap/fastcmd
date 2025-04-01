# Development Setup

This document describes how to set up and maintain the development environment for FastCmd.

## Development Environment

The project uses Docker for development to ensure consistency across different development machines. The development environment is containerized and includes all necessary tools and dependencies.

## Development Dependencies

The project uses a set of development dependencies defined in `requirements-dev.list` and locked in `requirements-dev.lock`. These include:

- `openai`: For OpenAI API integration
- `sqlite-vec`: For vector database operations
- `black`: Code formatter
- `isort`: Import sorter
- `flake8`: Code linter
- `mypy`: Type checker

### Updating Dependencies

To add or update a dependency:

1. Edit `requirements-dev.list` to add/update the package
2. Run:
   ```bash
   make update-requirements-dev
   ```

This will generate a new `requirements-dev.lock` with exact versions.

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
