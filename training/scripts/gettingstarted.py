#!/usr/bin/env python
# coding: utf-8

"""
Getting Started With ML Project With MLFLOW

- Installing MLflow.
- Starting a local MLflow Tracking Server.
- Logging and registering a model with MLflow.
- Loading a logged model for inference using MLflow's pyfunc flavor.
- Viewing the experiment results in the MLflow UI.
"""

import pandas as pd
from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import mlflow
from mlflow.models import infer_signature
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set MLflow authentication
# os.environ["MLFLOW_TRACKING_USERNAME"] = "user"
# os.environ["MLFLOW_TRACKING_PASSWORD"] = "xxx"

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

def main():
    """Main function for MLflow quickstart"""
    try:
        logger.info("Starting MLflow Quickstart...")
        
        # Set the tracking URI
        mlflow.set_tracking_uri("https://mlflow.new-nation.church")
        logger.info(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")
        
        # Load the dataset
        X, y = datasets.load_iris(return_X_y=True)
        logger.info(f"Dataset loaded: {X.shape[0]} samples, {X.shape[1]} features")
        
        # Split the data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
        logger.info(f"Training set: {X_train.shape[0]} samples, Test set: {X_test.shape[0]} samples")
        
        # Define the model hyperparameters
        params = {
            "penalty": "l2",
            "solver": "lbfgs", 
            "max_iter": 1000, 
            "multi_class": "auto", 
            "random_state": 8888
        }
        
        # Train the model
        logger.info("Training Logistic Regression model...")
        lr = LogisticRegression(**params)
        lr.fit(X_train, y_train)
        
        # Prediction on the test set
        y_pred = lr.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Model accuracy: {accuracy:.4f}")
        
        # MLFLOW Tracking
        experiment_name = "MLFLOW Quickstart"
        
        # Safely get or create experiment
        experiment_id = get_or_create_experiment(experiment_name)
        
        # Set experiment
        if experiment_id is not None:
            mlflow.set_experiment(experiment_id=experiment_id)
        else:
            mlflow.set_experiment(experiment_name)
        
        # Start an MLFLOW run
        with mlflow.start_run():
            # Log the hyperparameters
            mlflow.log_params(params)
            
            # Log the accuracy metrics
            mlflow.log_metric("accuracy", accuracy)
            
            # Set a tag that we can use to remind ourselves what this run was for
            mlflow.set_tag("Training Info", "Basic LR model for iris data")
            
            # Log the model
            mlflow.sklearn.log_model(
                lr, 
                "model", 
                registered_model_name="Iris Logistic Regression"
            )
            
            # Get run info
            run = mlflow.active_run()
            logger.info(f"MLflow Run ID: {run.info.run_id}")
            logger.info(f"Experiment ID: {run.info.experiment_id}")
            
        logger.info("MLflow Quickstart completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in MLflow Quickstart: {str(e)}")
        raise

if __name__ == "__main__":
    main()


