#!/usr/bin/env python3
"""
MLflow Utilities for Model Training and Tracking
"""

import os
import logging
import mlflow
from mlflow.tracking import MlflowClient

# Suppress Git warnings
os.environ['GIT_PYTHON_REFRESH'] = 'quiet'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_mlflow_connection():
    """Setup MLflow connection with authentication"""
    # Set MLflow tracking URI
    print(os.getenv("MLFLOW_TRACKING_URI"))
    print(os.getenv("MLFLOW_TRACKING_USERNAME"))
    print(os.getenv("MLFLOW_TRACKING_PASSWORD"))

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
    
    # Set authentication (if needed)
    # os.environ["MLFLOW_TRACKING_USERNAME"] = "user"
    # os.environ["MLFLOW_TRACKING_PASSWORD"] = "xxx"
    
    logger.info(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")
    return mlflow

def get_or_create_experiment(experiment_name):
    """Safely get or create an experiment"""
    try:
        # Try to get existing experiment
        experiment = mlflow.get_experiment_by_name(experiment_name)
        
        if experiment is None:
            # Create new experiment if it doesn't exist
            experiment_id = mlflow.create_experiment(experiment_name)
            logger.info(f"Created new experiment: {experiment_name} with ID: {experiment_id}")
        else:
            experiment_id = experiment.experiment_id
            logger.info(f"Using existing experiment: {experiment_name} with ID: {experiment_id}")
            
        return experiment_id
        
    except Exception as e:
        logger.warning(f"Error getting/creating experiment: {e}")
        # Fallback: try to use the experiment name directly
        try:
            mlflow.set_experiment(experiment_name)
            logger.info(f"Set experiment to: {experiment_name}")
            return None
        except Exception as e2:
            logger.error(f"Failed to set experiment: {e2}")
            # Last resort: use default experiment
            logger.info("Using default experiment")
            return 0

def get_model_info(model_name):
    """Get information about a specific model"""
    try:
        client = MlflowClient()
        versions = client.search_model_versions(f"name='{model_name}'")
        
        if versions:
            latest_version = max(versions, key=lambda v: v.version)
            return {
                "model_name": model_name,
                "version": latest_version.version,
                "run_id": latest_version.run_id,
                "status": latest_version.status,
                "source": latest_version.source
            }
        else:
            logger.warning(f"No versions found for model: {model_name}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return None

def load_model(model_name, version="latest"):
    """Load a model from MLflow"""
    try:
        model_uri = f"models:/{model_name}/{version}"
        logger.info(f"Loading model from: {model_uri}")
        
        model = mlflow.sklearn.load_model(model_uri)
        logger.info(f"Model loaded successfully: {type(model)}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def list_registered_models():
    """List all registered models"""
    try:
        client = MlflowClient()
        models = client.search_registered_models()
        
        model_list = []
        for model in models:
            model_info = {
                "name": model.name,
                "model_id": model.model_id,
                "creation_timestamp": model.creation_timestamp,
                "last_updated_timestamp": model.last_updated_timestamp,
                "description": model.description
            }
            model_list.append(model_info)
            
        return model_list
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return [] 