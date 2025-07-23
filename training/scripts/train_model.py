#!/usr/bin/env python3
"""
Model Training Script using MLflow
"""

import sys
import os
import logging
from datetime import datetime

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

from utils.mlflow_utils import setup_mlflow_connection, get_or_create_experiment
from utils.data_utils import load_california_housing_robust, create_dataframe_from_housing
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
from urllib.parse import urlparse
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data():
    """Load California Housing dataset using robust loading utility"""
    logger.info("Loading California Housing dataset using robust utility...")
    
    # Use the robust data loading utility
    X, y, feature_names = load_california_housing_robust()
    
    # Create DataFrame
    data = create_dataframe_from_housing(X, y, feature_names)
    
    return data

def hyperparameter_tuning(X_train, y_train, param_grid):
    """Perform hyperparameter tuning using GridSearchCV"""
    logger.info("Starting hyperparameter tuning...")
    
    rf = RandomForestRegressor()
    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=3,
        n_jobs=-1,
        verbose=2,
        scoring="neg_mean_squared_error"
    )
    grid_search.fit(X_train, y_train)
    
    logger.info(f"Best parameters: {grid_search.best_params_}")
    return grid_search

def train_model_with_mlflow(data, experiment_name="house_price_prediction"):
    """Train model with MLflow tracking"""
    logger.info(f"Starting MLflow experiment: {experiment_name}")
    
    # Setup MLflow connection
    setup_mlflow_connection()
    
    # Get or create experiment safely
    experiment_id = get_or_create_experiment(experiment_name)
    
    # Set the experiment
    if experiment_id is not None:
        mlflow.set_experiment(experiment_id=experiment_id)
    else:
        mlflow.set_experiment(experiment_name)
    
    # Prepare data
    X = data.drop(columns=["Price"])
    y = data["Price"]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    
    # Define hyperparameter grid
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [5, 10, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    
    with mlflow.start_run():
        # Perform hyperparameter tuning
        grid_search = hyperparameter_tuning(X_train, y_train, param_grid)
        
        # Get the best model
        best_model = grid_search.best_estimator_
        
        # Optimize model size for MLflow upload to prevent 413 error
        logger.info("Optimizing model size for MLflow upload...")
        
        # Reduce model complexity if needed
        if hasattr(best_model, 'n_estimators') and best_model.n_estimators > 50:
            logger.info(f"Reducing n_estimators from {best_model.n_estimators} to 50 for size optimization")
            best_model.n_estimators = 50
        
        # Limit max_depth if it's too large
        if hasattr(best_model, 'max_depth') and best_model.max_depth and best_model.max_depth > 10:
            logger.info(f"Reducing max_depth from {best_model.max_depth} to 10 for size optimization")
            best_model.max_depth = 10
        
        # Retrain with optimized parameters if changes were made
        if (hasattr(best_model, 'n_estimators') and best_model.n_estimators == 50) or \
           (hasattr(best_model, 'max_depth') and best_model.max_depth == 10):
            logger.info("Retraining model with optimized parameters...")
            best_model.fit(X_train, y_train)
        
        # Evaluate the best model
        y_pred = best_model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        
        # Log best parameters and metrics
        mlflow.log_param("best_n_estimators", grid_search.best_params_['n_estimators'])
        mlflow.log_param("best_max_depth", grid_search.best_params_['max_depth'])
        mlflow.log_param("best_min_samples_split", grid_search.best_params_['min_samples_split'])
        mlflow.log_param("best_min_samples_leaf", grid_search.best_params_['min_samples_leaf'])
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("rmse", np.sqrt(mse))
        
        # Log model
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
        
        if tracking_url_type_store != 'file':
            try:
                # Try to log model with compression
                mlflow.sklearn.log_model(
                    best_model, 
                    "model", 
                    registered_model_name="Best Randomforest Model",
                    code_paths=None  # Don't include code to reduce size
                )
                logger.info("Model logged successfully with compression")
            except Exception as upload_error:
                logger.warning(f"Model upload failed with compression: {upload_error}")
                logger.info("Trying with further size reduction...")
                
                # Create a smaller model for upload
                small_model = RandomForestRegressor(
                    n_estimators=25,  # Much smaller
                    max_depth=5,      # Limited depth
                    min_samples_split=best_model.min_samples_split,
                    min_samples_leaf=best_model.min_samples_leaf,
                    random_state=42
                )
                small_model.fit(X_train, y_train)
                
                # Log the smaller model
                mlflow.sklearn.log_model(
                    small_model, 
                    "model", 
                    registered_model_name="Best Randomforest Model (Compressed)",
                    code_paths=None
                )
                logger.info("Smaller model logged successfully")
        else:
            from mlflow.models import infer_signature
            signature = infer_signature(X_train, y_train)
            mlflow.sklearn.log_model(best_model, "model", signature=signature)
        
        logger.info(f"Best Hyperparameters: {grid_search.best_params_}")
        logger.info(f"Mean Squared Error: {mse:.4f}")
        logger.info(f"Root Mean Squared Error: {np.sqrt(mse):.4f}")
        
        return best_model, mse, grid_search.best_params_

def main():
    """Main execution function"""
    try:
        logger.info("Starting House Price Prediction ML pipeline...")
        
        # Load data
        data = load_data()
        
        # Get experiment name from environment or use default
        experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', 'house_price_prediction')
        
        # Train model with MLflow tracking
        model, mse, best_params = train_model_with_mlflow(data, experiment_name)
        
        logger.info("ML pipeline completed successfully!")
        logger.info(f"Final metrics - MSE: {mse:.4f}, RMSE: {np.sqrt(mse):.4f}")
        
    except Exception as e:
        logger.error(f"Error in ML pipeline: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 