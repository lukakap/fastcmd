#!/bin/bash

# Create the script that will be installed
cat > /usr/local/bin/fastcmd << 'EOL'
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
fi

# Run the container with current directory mounted
docker run -it --rm \
    -v "$PWD":/app \
    -w /app \
    lukakap/fastcmd:latest "$@"
EOL

# Make the script executable
chmod +x /usr/local/bin/fastcmd

echo "FastCmd installed successfully! You can now use 'fastcmd' command from anywhere." 