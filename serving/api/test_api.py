#!/usr/bin/env python3
"""
Test client for MLflow Model Serving API
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8080"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_model_info():
    """Test model info endpoint"""
    print("🔍 Testing model info endpoint...")
    response = requests.get(f"{BASE_URL}/model/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_example():
    """Test example endpoint"""
    print("🔍 Testing example endpoint...")
    response = requests.get(f"{BASE_URL}/example")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_single_prediction():
    """Test single prediction endpoint"""
    print("🔍 Testing single prediction...")
    
    # Test data
    test_data = {
        "features": [5.1, 3.5, 1.4, 0.2]  # setosa
    }
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(test_data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_batch_prediction():
    """Test batch prediction endpoint"""
    print("🔍 Testing batch prediction...")
    
    # Test data
    test_data = {
        "features": [
            [5.1, 3.5, 1.4, 0.2],  # setosa
            [6.3, 3.3, 4.7, 1.6],  # versicolor
            [6.7, 3.0, 5.2, 2.3]   # virginica
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/predict/batch",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(test_data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_invalid_input():
    """Test invalid input handling"""
    print("🔍 Testing invalid input handling...")
    
    # Test with wrong number of features
    test_data = {
        "features": [5.1, 3.5, 1.4]  # Missing one feature
    }
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(test_data, indent=2)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_api_documentation():
    """Test API documentation endpoint"""
    print("🔍 Testing API documentation...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Run all tests"""
    print("🚀 Starting MLflow Model API Tests...")
    print("=" * 50)
    
    try:
        # Wait for API to be ready
        print("⏳ Waiting for API to be ready...")
        time.sleep(2)
        
        # Run tests
        test_api_documentation()
        test_health()
        test_model_info()
        test_example()
        test_single_prediction()
        test_batch_prediction()
        test_invalid_input()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Make sure the Flask server is running on http://localhost:8080")
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    main() 