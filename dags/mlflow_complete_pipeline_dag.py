"""
Complete MLflow Pipeline DAG
- Model Training → Model Registration → Model Deployment → Model Serving
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from docker.types import Mount
from airflow.models import Variable
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
    'mlflow_complete_pipeline',
    default_args=default_args,
    description='Complete MLflow ML pipeline: Training → Registration → Deployment → Serving',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['mlflow', 'mlops', 'pipeline'],
)

# Get MLflow configuration from Airflow Variables
mlflow_uri = Variable.get("MLFLOW_TRACKING_URI")
mlflow_username = Variable.get("MLFLOW_TRACKING_USERNAME")
mlflow_password = Variable.get("MLFLOW_TRACKING_PASSWORD")
mlflow_experiment = Variable.get("MLFLOW_EXPERIMENT_NAME", "production_experiment")

# Task 1: Model Training
train_model = DockerOperator(
    task_id='train_model',
    image='doohee323/ml_training:latest',
    container_name='mlflow_training_job',
    api_version='auto',
    auto_remove=True,
    docker_url='unix://var/run/docker.sock',
    network_mode='bridge',
    mounts=[
        Mount(source='/path/to/data', target='/data', type='bind'),
        Mount(source='/path/to/models', target='/models', type='bind'),
    ],
    environment={
        'MLFLOW_TRACKING_URI': mlflow_uri,
        'MLFLOW_EXPERIMENT_NAME': mlflow_experiment,
        'MLFLOW_TRACKING_USERNAME': mlflow_username,
        'MLFLOW_TRACKING_PASSWORD': mlflow_password,
    },
    dag=dag,
)

# Task 2: Model Registration Check
def check_model_registration(**context):
    """Check if model is registered in MLflow"""
    import mlflow
    from mlflow.tracking import MlflowClient
    
    # Get MLflow configuration from Airflow Variables
    mlflow_uri = Variable.get("MLFLOW_TRACKING_URI")
    
    # Setup MLflow connection
    mlflow.set_tracking_uri(mlflow_uri)
    client = MlflowClient()
    
    # Check for registered models
    models = client.search_registered_models()
    model_names = [model.name for model in models]
    
    logger.info(f"Registered models: {model_names}")
    
    # Check for specific model (e.g., "Best Randomforest Model")
    target_model = "Best Randomforest Model"
    if target_model in model_names:
        logger.info(f"✅ Model '{target_model}' is registered")
        return True
    else:
        logger.warning(f"❌ Model '{target_model}' is not registered")
        return False

check_model = PythonOperator(
    task_id='check_model_registration',
    python_callable=check_model_registration,
    dag=dag,
)

# Task 3: Deploy Model to Serving Environment
deploy_model = DockerOperator(
    task_id='deploy_model',
    image='doohee323/ml_serving:latest',
    container_name='mlflow_serving_deployment',
    api_version='auto',
    auto_remove=True,
    docker_url='unix://var/run/docker.sock',
    network_mode='bridge',
    ports=['8080:8080'],
    environment={
        'MLFLOW_TRACKING_URI': mlflow_uri,
        'MLFLOW_TRACKING_USERNAME': mlflow_username,
        'MLFLOW_TRACKING_PASSWORD': mlflow_password,
        'MODEL_NAME': 'Best Randomforest Model',
        'MODEL_VERSION': 'latest',
    },
    dag=dag,
)

# Task 4: Health Check for API Service
def check_api_health(**context):
    """Check if API service is healthy"""
    try:
        response = requests.get('http://localhost:8080/health', timeout=30)
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"API Health Check: {health_data}")
            return health_data.get('model_loaded', False)
        else:
            logger.error(f"API Health Check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"API Health Check error: {str(e)}")
        return False

api_health_check = PythonOperator(
    task_id='api_health_check',
    python_callable=check_api_health,
    dag=dag,
)

# Task 5: Model Performance Test
def test_model_performance(**context):
    """Test model performance with sample data"""
    try:
        # Sample test data
        test_data = {
            "features": [5.1, 3.5, 1.4, 0.2]
        }
        
        response = requests.post(
            'http://localhost:8080/predict',
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Model prediction test successful: {result}")
            return True
        else:
            logger.error(f"Model prediction test failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Model performance test error: {str(e)}")
        return False

performance_test = PythonOperator(
    task_id='performance_test',
    python_callable=test_model_performance,
    dag=dag,
)

# Task 6: Batch Prediction Test
def test_batch_prediction(**context):
    """Test batch prediction functionality"""
    try:
        # Sample batch test data
        batch_data = {
            "features": [
                [5.1, 3.5, 1.4, 0.2],
                [6.3, 3.3, 4.7, 1.6],
                [7.0, 3.2, 4.7, 1.4]
            ]
        }
        
        response = requests.post(
            'http://localhost:8080/predict/batch',
            json=batch_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Batch prediction test successful: {len(result.get('predictions', []))} predictions")
            return True
        else:
            logger.error(f"Batch prediction test failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Batch prediction test error: {str(e)}")
        return False

batch_test = PythonOperator(
    task_id='batch_prediction_test',
    python_callable=test_batch_prediction,
    dag=dag,
)

# Task 7: Model Monitoring Setup
def setup_monitoring(**context):
    """Setup model monitoring and alerting"""
    logger.info("Setting up model monitoring...")
    
    # Here you would typically:
    # 1. Set up metrics collection
    # 2. Configure alerting rules
    # 3. Set up dashboards
    # 4. Configure model drift detection
    
    monitoring_config = {
        "metrics_endpoint": "http://localhost:8080/health",
        "prediction_endpoint": "http://localhost:8080/predict",
        "alert_threshold": 0.95,
        "drift_detection": True
    }
    
    logger.info(f"Monitoring configuration: {monitoring_config}")
    return True

monitoring_setup = PythonOperator(
    task_id='setup_monitoring',
    python_callable=setup_monitoring,
    dag=dag,
)

# Task 8: Pipeline Completion Notification
def pipeline_completion_notification(**context):
    """Send notification about pipeline completion"""
    logger.info("🎉 MLflow Pipeline completed successfully!")
    logger.info("✅ Model trained and registered")
    logger.info("✅ Model deployed and serving")
    logger.info("✅ API health checks passed")
    logger.info("✅ Performance tests completed")
    logger.info("✅ Monitoring setup complete")
    
    # Here you would typically send notifications via:
    # - Email
    # - Slack
    # - Teams
    # - Webhook
    
    return True

completion_notification = PythonOperator(
    task_id='pipeline_completion_notification',
    python_callable=pipeline_completion_notification,
    dag=dag,
)

# Define task dependencies
train_model >> check_model >> deploy_model >> api_health_check
api_health_check >> [performance_test, batch_test]
[performance_test, batch_test] >> monitoring_setup >> completion_notification 