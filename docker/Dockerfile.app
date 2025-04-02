FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up environment variables for configuration
ENV FASTCMD_CONFIG_DIR=/root/.fastcmd
ENV FASTCMD_DB_DIR=/root/.fastcmd/db
ENV FASTCMD_HOME=/root

# Create necessary directories
RUN mkdir -p $FASTCMD_CONFIG_DIR $FASTCMD_DB_DIR && \
    chmod 700 $FASTCMD_CONFIG_DIR && \
    chmod 700 $FASTCMD_DB_DIR

# Copy requirements files
COPY requirements.lock .

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies from lock file
RUN pip install --no-cache-dir -r requirements.lock

# Copy the application
COPY . .

# Add the project root to PYTHONPATH
ENV PYTHONPATH=/app

# Add version label
ARG VERSION
LABEL version=$VERSION

# Set default command
CMD ["python", "src/fastcmd.py"] 