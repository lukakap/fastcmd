#!/bin/bash

# Ensure script is run with root permissions
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root or using sudo."
  exit 1
fi

# Define the installation path
INSTALL_PATH="/usr/local/bin/fastcmd"

# Create the fastcmd script
cat > "$INSTALL_PATH" << 'EOL'
#!/bin/bash

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Check if image exists, if not pull it
if ! docker image inspect lukakap/fastcmd:latest > /dev/null 2>&1; then
    echo "Pulling FastCmd image..."
    docker pull lukakap/fastcmd:latest
    if [ $? -ne 0 ]; then
        echo "Error: Failed to pull FastCmd image"
        exit 1
    fi
fi

# Run the container
docker run -it --rm lukakap/fastcmd:latest "$@"
EOL

# Make the script executable
chmod +x "$INSTALL_PATH"

echo "FastCmd installed successfully! You can now use the 'fastcmd' command from anywhere..."