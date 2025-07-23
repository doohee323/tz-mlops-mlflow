"""
MLflow Model Serving DAG
- Deploy and serve MLflow models via API
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.models import Variable
from docker.types import Mount
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_args = {
    'owner': 'mlops',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'mlflow_serving',
    default_args=default_args,
    description='MLflow Model Serving: Deploy and serve models via API',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['mlflow', 'serving', 'api'],
)

# Get MLflow configuration from Airflow Variables
mlflow_uri = Variable.get("MLFLOW_TRACKING_URI")
mlflow_username = Variable.get("MLFLOW_TRACKING_USERNAME")
mlflow_password = Variable.get("MLFLOW_TRACKING_PASSWORD")

# Task 1: Deploy Model Service
deploy_service = DockerOperator(
    task_id='deploy_model_service',
    image='doohee323/ml_serving:latest',
    container_name='mlflow_api_service',
    api_version='auto',
    auto_remove=True,
    docker_url='unix://var/run/docker.sock',
    network_mode='bridge',
    ports=['8080:8080'],
    environment={
        'MLFLOW_TRACKING_URI': mlflow_uri,
        'MLFLOW_TRACKING_USERNAME': mlflow_username,
        'MLFLOW_TRACKING_PASSWORD': mlflow_password,
        'MODEL_NAME': 'Iris Logistic Regression',
        'MODEL_VERSION': 'latest',
    },
    dag=dag,
)

# Task 2: Wait for Service to be Ready
def wait_for_service(**context):
    """Wait for the API service to be ready"""
    import time
    
    max_retries = 30
    retry_interval = 10
    
    for i in range(max_retries):
        try:
            response = requests.get('http://localhost:8080/health', timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Service is ready: {health_data}")
                return True
        except Exception as e:
            logger.info(f"⏳ Waiting for service... (attempt {i+1}/{max_retries})")
            time.sleep(retry_interval)
    
    logger.error("❌ Service failed to start within timeout")
    return False

wait_service = PythonOperator(
    task_id='wait_for_service',
    python_callable=wait_for_service,
    dag=dag,
)

# Task 3: Test Model Predictions
def test_predictions(**context):
    """Test model predictions with sample data"""
    test_cases = [
        {"features": [5.1, 3.5, 1.4, 0.2], "expected": "setosa"},
        {"features": [6.3, 3.3, 4.7, 1.6], "expected": "versicolor"},
        {"features": [7.0, 3.2, 4.7, 1.4], "expected": "versicolor"},
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        try:
            response = requests.post(
                'http://localhost:8080/predict',
                json={"features": test_case["features"]},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                prediction = result.get('prediction', 'unknown')
                expected = test_case['expected']
                
                success = prediction == expected
                results.append({
                    "test_case": i + 1,
                    "input": test_case["features"],
                    "prediction": prediction,
                    "expected": expected,
                    "success": success
                })
                
                logger.info(f"Test {i+1}: {prediction} (expected: {expected}) - {'✅' if success else '❌'}")
            else:
                logger.error(f"Test {i+1} failed: HTTP {response.status_code}")
                results.append({
                    "test_case": i + 1,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            logger.error(f"Test {i+1} error: {str(e)}")
            results.append({
                "test_case": i + 1,
                "error": str(e)
            })
    
    # Summary
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(test_cases)
    
    logger.info(f"📊 Test Results: {successful_tests}/{total_tests} successful")
    
    return successful_tests == total_tests

test_predictions_task = PythonOperator(
    task_id='test_predictions',
    python_callable=test_predictions,
    dag=dag,
)

# Task 4: Load Testing (Optional)
def load_test(**context):
    """Perform basic load testing"""
    import time
    
    logger.info("🚀 Starting load test...")
    
    # Test batch predictions
    batch_data = {
        "features": [
            [5.1, 3.5, 1.4, 0.2] for _ in range(10)  # 10 predictions
        ]
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            'http://localhost:8080/predict/batch',
            json=batch_data,
            timeout=30
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            predictions_count = len(result.get('predictions', []))
            
            logger.info(f"✅ Load test successful:")
            logger.info(f"   - Predictions: {predictions_count}")
            logger.info(f"   - Duration: {duration:.2f} seconds")
            logger.info(f"   - Throughput: {predictions_count/duration:.2f} predictions/sec")
            
            return True
        else:
            logger.error(f"❌ Load test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Load test error: {str(e)}")
        return False

load_test_task = PythonOperator(
    task_id='load_test',
    python_callable=load_test,
    dag=dag,
)

# Task 5: Service Status Report
def service_status_report(**context):
    """Generate service status report"""
    try:
        # Get health status
        health_response = requests.get('http://localhost:8080/health', timeout=5)
        health_data = health_response.json() if health_response.status_code == 200 else {}
        
        # Get model info
        model_response = requests.get('http://localhost:8080/model/info', timeout=5)
        model_data = model_response.json() if model_response.status_code == 200 else {}
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "service_status": "running" if health_data.get('status') == 'healthy' else 'error',
            "model_loaded": health_data.get('model_loaded', False),
            "model_info": model_data.get('model_info', {}),
            "endpoints": {
                "health": "http://localhost:8080/health",
                "predict": "http://localhost:8080/predict",
                "batch": "http://localhost:8080/predict/batch"
            }
        }
        
        logger.info("📋 Service Status Report:")
        logger.info(f"   - Status: {report['service_status']}")
        logger.info(f"   - Model Loaded: {report['model_loaded']}")
        logger.info(f"   - Model Name: {report['model_info'].get('model_name', 'N/A')}")
        logger.info(f"   - Model Version: {report['model_info'].get('version', 'N/A')}")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Status report error: {str(e)}")
        return {"error": str(e)}

status_report = PythonOperator(
    task_id='service_status_report',
    python_callable=service_status_report,
    dag=dag,
)

# Define task dependencies
deploy_service >> wait_service >> test_predictions_task >> load_test_task >> status_report 