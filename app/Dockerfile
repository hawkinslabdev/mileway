FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    unzip \
    nodejs \
    npm \
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

# Expose both frontend and backend ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Run the application with both frontend and backend
CMD ["reflex", "run", "--env", "prod", "--frontend-port", "3000", "--backend-port", "8000", "--backend-host", "0.0.0.0"]