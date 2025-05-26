FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy configuration
COPY rxconfig.py .

# Create the app directory structure
RUN mkdir -p mileway

# Copy application code to the correct location
COPY mileway.py mileway/mileway.py

# Create __init__.py to make it a Python package
RUN touch mileway/__init__.py

# Copy other files
COPY manifest.json .
COPY .env* ./

# Create data directory for SQLite database
RUN mkdir -p /app/data && chmod 755 /app/data

# Initialize the Reflex app (this creates the frontend build)
RUN reflex init

# Set default environment variables
ENV BACKEND_PORT=8001
ENV FRONTEND_PORT=3001
ENV API_URL=http://localhost:8001
ENV DEPLOY_URL=http://localhost:3001

# Expose the frontend port (will be overridden by env var)
EXPOSE $FRONTEND_PORT $BACKEND_PORT

# Health check using environment variable
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$FRONTEND_PORT || exit 1

# Simple command - Reflex will read config from environment
CMD ["reflex", "run", "--env", "prod"]