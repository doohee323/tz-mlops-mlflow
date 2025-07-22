#!/usr/bin/env python3
"""
Main ML execution code with MLflow integration
"""

import os
import sys
import logging
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data():
    """Load or generate sample data"""
    logger.info("Loading data...")
    
    # Generate sample data for demonstration
    np.random.seed(42)
    n_samples = 1000
    
    # Create synthetic features
    X = np.random.randn(n_samples, 10)
    y = 3 * X[:, 0] + 2 * X[:, 1] - 1.5 * X[:, 2] + np.random.randn(n_samples) * 0.1
    
    return X, y

def train_model(X, y, experiment_name="mlflow_experiment"):
    """Train model with MLflow tracking"""
    logger.info(f"Starting MLflow experiment: {experiment_name}")
    
    # Set MLflow tracking URI
    mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    # Set experiment
    mlflow.set_experiment(experiment_name)
    
    with mlflow.start_run():
        # Log parameters
        n_estimators = 100
        max_depth = 10
        random_state = 42
        
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("random_state", random_state)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state
        )
        
        # Train model
        logger.info("Training Random Forest model...")
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state
        )
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Log metrics
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("r2_score", r2)
        mlflow.log_metric("rmse", np.sqrt(mse))
        
        # Log model
        mlflow.sklearn.log_model(model, "random_forest_model")
        
        # Log feature importance
        feature_importance = pd.DataFrame({
            'feature': [f'feature_{i}' for i in range(X.shape[1])],
            'importance': model.feature_importances_
        })
        feature_importance.to_csv("feature_importance.csv", index=False)
        mlflow.log_artifact("feature_importance.csv")
        
        logger.info(f"Training completed. R2 Score: {r2:.4f}, MSE: {mse:.4f}")
        
        return model, mse, r2

def main():
    """Main execution function"""
    try:
        logger.info("Starting ML pipeline...")
        
        # Load data
        X, y = load_data()
        
        # Get experiment name from environment or use default
        experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', 'mlflow_experiment')
        
        # Train model with MLflow tracking
        model, mse, r2 = train_model(X, y, experiment_name)
        
        logger.info("ML pipeline completed successfully!")
        logger.info(f"Final metrics - R2: {r2:.4f}, MSE: {mse:.4f}")
        
    except Exception as e:
        logger.error(f"Error in ML pipeline: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 