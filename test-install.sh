#!/bin/bash

# Create a test directory
TEST_DIR="./test-install"
mkdir -p "$TEST_DIR"

# Create the script that will be installed
cat > "$TEST_DIR/fastcmd" << 'EOL'
#!/bin/bash

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Check if image exists
if ! docker images lukakap/fastcmd:latest --quiet | grep -q .; then
    echo "FastCmd image not found. Pulling from Docker Hub..."
    docker pull lukakap/fastcmd:latest
    if [ $? -ne 0 ]; then
        echo "Error: Failed to pull FastCmd image"
        exit 1
    fi
    echo "FastCmd image pulled successfully"
fi

# Run the container with current directory mounted
docker run -it --rm \
    -v "$PWD":/app \
    -w /app \
    -e PYTHONPATH=/app \
    lukakap/fastcmd:latest "$@"
EOL

# Make the script executable
chmod +x "$TEST_DIR/fastcmd"

echo "FastCmd test installation completed!"
echo "To test it, add the test directory to your PATH:"
echo "export PATH=\"$PWD/$TEST_DIR:\$PATH\""
echo "Then try running: fastcmd" 