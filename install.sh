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

# Function to check and update FastCmd
check_and_update() {
    # Get the current image digest
    local current_digest=$(docker inspect lukakap/fastcmd:latest --format '{{.Id}}' 2>/dev/null || echo "none")
    
    # Pull the latest image without running it
    docker pull lukakap/fastcmd:latest > /dev/null 2>&1
    
    # Get the new image digest
    local new_digest=$(docker inspect lukakap/fastcmd:latest --format '{{.Id}}' 2>/dev/null)
    
    # Compare digests to determine if an update is needed
    if [ "$current_digest" != "$new_digest" ]; then
        echo "A new version of FastCmd is available!"
        echo "Updating to the latest version..."
        if [ $? -eq 0 ]; then
            echo "FastCmd updated successfully!"
        else
            echo "Error: Failed to update FastCmd"
            exit 1
        fi
    fi
}

# Check and update if needed
check_and_update

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

echo "FastCmd installed successfully! You can now use the 'fastcmd' command from anywhere."
echo "FastCmd will automatically update when new versions are available."