#!/usr/bin/env python3
"""
Data Preparation Script for Docker Build
This script pre-downloads datasets during Docker build to avoid runtime download issues
"""

import os
import sys
import logging

# Suppress Git warnings
os.environ['GIT_PYTHON_REFRESH'] = 'quiet'

# Add shared utils to path - handle both local development and Docker
current_dir = os.path.dirname(os.path.abspath(__file__))
# Try multiple possible paths for shared utils
possible_paths = [
    os.path.join(current_dir, '../../shared'),  # From training/scripts/
    os.path.join(current_dir, '../shared'),     # From scripts/ (if in Docker)
    '/app/shared',                              # Absolute path in Docker
    os.path.join(os.getcwd(), 'shared')         # From current working directory
]

for path in possible_paths:
    if os.path.exists(path):
        sys.path.append(path)
        break
else:
    # If no path found, try to find shared directory relative to current file
    logger = logging.getLogger(__name__)
    logger.warning("Could not find shared directory, trying to locate it...")
    
    # Walk up the directory tree to find shared
    current = current_dir
    while current != os.path.dirname(current):  # Stop at root
        shared_path = os.path.join(current, 'shared')
        if os.path.exists(shared_path):
            sys.path.append(shared_path)
            logger.info(f"Found shared directory at: {shared_path}")
            break
        current = os.path.dirname(current)

from utils.data_utils import load_california_housing_robust

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Pre-download and prepare datasets"""
    logger.info("Starting data preparation for Docker build...")
    
    # Create data directories
    data_dirs = [
        "/app/scikit_learn_data",
        "/tmp/scikit_learn_data",
        os.path.expanduser("~/.cache/scikit_learn_data")
    ]
    
    for data_dir in data_dirs:
        try:
            os.makedirs(data_dir, exist_ok=True)
            logger.info(f"Created/verified directory: {data_dir}")
        except Exception as e:
            logger.warning(f"Could not create directory {data_dir}: {e}")
    
    # Try to pre-download California Housing dataset
    try:
        logger.info("Pre-downloading California Housing dataset...")
        X, y, feature_names = load_california_housing_robust()
        logger.info(f"✅ Successfully pre-downloaded dataset: {X.shape[0]} samples, {X.shape[1]} features")
        
        # Verify the data
        logger.info(f"Feature names: {feature_names}")
        logger.info(f"Target range: {y.min():.2f} to {y.max():.2f}")
        logger.info(f"Features range: {X.min(axis=0)} to {X.max(axis=0)}")
        
    except Exception as e:
        logger.error(f"Failed to pre-download dataset: {e}")
        logger.info("Dataset will be downloaded at runtime or synthetic data will be used")
    
    # List downloaded files
    for data_dir in data_dirs:
        if os.path.exists(data_dir):
            try:
                contents = os.listdir(data_dir)
                logger.info(f"Contents of {data_dir}: {contents}")
            except Exception as e:
                logger.warning(f"Could not list contents of {data_dir}: {e}")
    
    logger.info("Data preparation completed!")

if __name__ == "__main__":
    main() 