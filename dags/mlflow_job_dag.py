from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

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
    'mlflow_job_dag',
    default_args=default_args,
    description='MLflow ML job orchestration DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['mlflow', 'mlops'],
)

def mlflow_experiment_task():
    """Execute MLflow experiment"""
    import subprocess
    import sys
    
    # Run the ML code
    result = subprocess.run([
        sys.executable, 
        '/app/ml_code/main.py'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"ML job failed: {result.stderr}")
    
    print("MLflow experiment completed successfully")

# Docker task to run ML code
ml_job = DockerOperator(
    task_id='ml_job',
    image='mlflow-ml:latest',
    container_name='mlflow_ml_job',
    api_version='auto',
    auto_remove=True,
    docker_url='unix://var/run/docker.sock',
    network_mode='bridge',
    mounts=[
        Mount(source='/path/to/data', target='/data', type='bind'),
        Mount(source='/path/to/models', target='/models', type='bind'),
    ],
    environment={
        'MLFLOW_TRACKING_URI': 'http://mlflow-server:5000',
        'MLFLOW_EXPERIMENT_NAME': 'production_experiment',
    },
    dag=dag,
)

# Python task for post-processing
post_process = PythonOperator(
    task_id='post_process',
    python_callable=lambda: print("Post-processing completed"),
    dag=dag,
)

# Define task dependencies
ml_job >> post_process 