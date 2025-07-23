#!/usr/bin/env python3
"""
Flask API for MLflow Model Serving
"""

import sys
import os
import logging
from datetime import datetime

# Add shared utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from flask import Flask, request, jsonify
from utils.mlflow_utils import setup_mlflow_connection, load_model, get_model_info
import mlflow.sklearn
import numpy as np
from sklearn.datasets import load_iris
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global model variable
model = None
model_info = {}

def load_model_for_serving():
    """Load the MLflow model for serving"""
    global model, model_info
    
    try:
        # Setup MLflow connection
        setup_mlflow_connection()
        
        # Model configuration
        model_name = "Iris Logistic Regression"
        
        # Load model
        model = load_model(model_name, "latest")
        
        # Get model info
        model_info = get_model_info(model_name)
        if model_info:
            model_info["loaded_at"] = datetime.now().isoformat()
        
        logger.info(f"Model loaded successfully: {type(model)}")
        logger.info(f"Model info: {model_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/model/info', methods=['GET'])
def model_info_endpoint():
    """Get model information"""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    return jsonify({
        "model_info": model_info,
        "model_type": str(type(model)),
        "features": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
        "target_classes": ["setosa", "versicolor", "virginica"]
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Make predictions"""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        # Get input data
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({
                "error": "Invalid input. Expected JSON with 'features' key containing array of 4 values"
            }), 400
        
        features = data['features']
        
        # Validate input
        if not isinstance(features, list) or len(features) != 4:
            return jsonify({
                "error": "Features must be an array of exactly 4 numeric values"
            }), 400
        
        # Convert to numpy array
        input_data = np.array(features).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(input_data)
        probabilities = model.predict_proba(input_data)
        
        # Map prediction to class names
        iris = load_iris()
        class_names = iris.target_names
        predicted_class = class_names[prediction[0]]
        
        # Format probabilities
        prob_dict = {class_names[i]: float(prob) for i, prob in enumerate(probabilities[0])}
        
        return jsonify({
            "prediction": predicted_class,
            "prediction_id": int(prediction[0]),
            "probabilities": prob_dict,
            "input_features": features,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Make batch predictions"""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        # Get input data
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({
                "error": "Invalid input. Expected JSON with 'features' key containing array of arrays"
            }), 400
        
        features_list = data['features']
        
        # Validate input
        if not isinstance(features_list, list):
            return jsonify({
                "error": "Features must be an array of arrays"
            }), 400
        
        for i, features in enumerate(features_list):
            if not isinstance(features, list) or len(features) != 4:
                return jsonify({
                    "error": f"Features at index {i} must be an array of exactly 4 numeric values"
                }), 400
        
        # Convert to numpy array
        input_data = np.array(features_list)
        
        # Make predictions
        predictions = model.predict(input_data)
        probabilities = model.predict_proba(input_data)
        
        # Map predictions to class names
        iris = load_iris()
        class_names = iris.target_names
        
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            prob_dict = {class_names[j]: float(p) for j, p in enumerate(prob)}
            results.append({
                "index": i,
                "prediction": class_names[pred],
                "prediction_id": int(pred),
                "probabilities": prob_dict,
                "input_features": features_list[i]
            })
        
        return jsonify({
            "predictions": results,
            "total_predictions": len(results),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({"error": f"Batch prediction failed: {str(e)}"}), 500

@app.route('/example', methods=['GET'])
def get_example():
    """Get example input data"""
    iris = load_iris()
    
    return jsonify({
        "example_single": {
            "features": iris.data[0].tolist(),
            "description": "Single prediction example"
        },
        "example_batch": {
            "features": iris.data[:3].tolist(),
            "description": "Batch prediction example (3 samples)"
        },
        "feature_names": iris.feature_names,
        "target_names": iris.target_names.tolist()
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        "message": "MLflow Model Serving API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API documentation",
            "GET /health": "Health check",
            "GET /model/info": "Model information",
            "GET /example": "Example input data",
            "POST /predict": "Single prediction",
            "POST /predict/batch": "Batch prediction"
        },
        "usage": {
            "single_prediction": {
                "url": "/predict",
                "method": "POST",
                "body": {"features": [5.1, 3.5, 1.4, 0.2]}
            },
            "batch_prediction": {
                "url": "/predict/batch",
                "method": "POST",
                "body": {"features": [[5.1, 3.5, 1.4, 0.2], [6.3, 3.3, 4.7, 1.6]]}
            }
        }
    })

if __name__ == '__main__':
    # Load model on startup
    logger.info("Starting MLflow Model Serving API...")
    
    if load_model_for_serving():
        logger.info("Model loaded successfully. Starting Flask server...")
        # Use port 8080 instead of 5000 to avoid conflicts with AirPlay
        app.run(host='0.0.0.0', port=8080, debug=True)
    else:
        logger.error("Failed to load model. Exiting...")
        exit(1) 