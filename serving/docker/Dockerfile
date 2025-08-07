# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY serving/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ ./shared/

# Copy serving API
COPY serving/api/ ./api/

# Set environment variables
ENV PYTHONPATH=/app
ENV MLFLOW_TRACKING_URI=https://mlflow.drillquiz.com
ENV MLFLOW_EXPERIMENT_NAME=production_experiment
ENV MLFLOW_TRACKING_USERNAME=user
ENV MLFLOW_TRACKING_PASSWORD=xxx

# Create directories for data and models
RUN mkdir -p /data /models

# Expose port for Flask API
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command - run Flask API
CMD ["python", "api/app.py"] 