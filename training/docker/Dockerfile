# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Git
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY training/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities first
COPY shared/ ./shared/

# Copy training scripts
COPY training/scripts/ ./scripts/

# Create directories for data and models
RUN mkdir -p /data /models /app/scikit_learn_data /tmp/scikit_learn_data

# Pre-download datasets during build
RUN python scripts/prepare_data.py

# Set environment variables
ENV PYTHONPATH=/app
ENV MLFLOW_TRACKING_URI=https://mlflow.new-nation.church
ENV MLFLOW_EXPERIMENT_NAME=production_experiment
ENV MLFLOW_TRACKING_USERNAME=user
ENV MLFLOW_TRACKING_PASSWORD=xxx
# Suppress Git warnings in MLflow
ENV GIT_PYTHON_REFRESH=quiet

# Default command - run training script
CMD ["python", "scripts/train_model.py"] 