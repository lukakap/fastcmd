FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

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