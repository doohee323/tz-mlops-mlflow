# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy ML code
COPY ml_code/ ./ml_code/

# Set environment variables
ENV PYTHONPATH=/app
ENV MLFLOW_TRACKING_URI=http://mlflow-server:5000
ENV MLFLOW_EXPERIMENT_NAME=production_experiment

# Create directories for data and models
RUN mkdir -p /data /models

# Expose port if needed
EXPOSE 8000

# Default command
CMD ["python", "ml_code/main.py"] 