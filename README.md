# FastCommand

FastCommand is a terminal application designed to simplify the workflow for developers and tech enthusiasts. It translates natural language commands into specific terminal commands, making it easier for users to execute complex tasks without remembering the exact syntax.

## Features

- **Natural Language Processing**: Understands and converts natural language inputs into precise terminal commands.
- **Command Customization and Storage**: Allows users to save, retrieve, and manage custom commands.
- **Cross-platform Compatibility**: Works on various operating systems through Docker.

## Installation

### Quick Install (Recommended)

1. Install Docker
2. Run the installation script:
   ```bash
   curl -s https://raw.githubusercontent.com/lukakap/fastcmd/main/install.sh | sudo bash
   ```
3. Use FastCmd from anywhere:
   ```bash
   fastcmd add -d "description" -c "command"
   fastcmd run -d "description"
   ```

### Development Installation

1. Install Docker and Docker Compose
2. Clone the repository:
   ```bash
   git clone https://github.com/lukakap/fastcmd.git
   cd fastcmd
   ```
3. Run the application:
   ```bash
   make run
   ```

## Development

See [Development Setup](docs/development.md) for instructions on setting up the development environment.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/lukakap/fastcmd/issues) for open problems or discussions.

---

Disclaimer: This tool executes terminal commands and should be used with caution. Always verify commands before execution.

## Stack

### Vector Database

currently we are using sqlite-vec.

## Distribution Strategy

The application is distributed in multiple ways to accommodate different user needs:

1. **Global Command (Recommended)**
   - One-command installation
   - Available as `fastcmd` command globally
   - Automatically pulls and runs Docker container
   - Works from any directory

2. **Development Installation**
   - Clone repository and use Docker Compose
   - Full development environment with all tools
   - Best for contributors and developers

### Publishing Updates

1. **Docker Image**:
   ```bash
   # Build and tag
   docker build -t lukakap/fastcmd:latest -f docker/Dockerfile.app .
   # Push to Docker Hub
   docker push lukakap/fastcmd:latest
   ```