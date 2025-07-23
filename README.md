# tz-mlops-mlflow

MLflow and Airflow based Machine Learning Operations (MLOps) pipeline project.

## 📋 Project Overview

This project is a pipeline that automates and manages ML experiments using existing external MLflow and Airflow servers.

### Workflow

```
[ML experiment code (Jupyter)]
     ↓ (nbconvert)
[Python code conversion and if __name__ addition]
     ↓
[Docker Image build and Push]            => CI
     ↓
[Airflow DAG creation and GitOps deployment]       => CI
     ↓
[Airflow UI Trigger and Monitoring]     => CI
```

## 📁 Project Structure

```
tz-mlops-mlflow/
├── training/                    # Model development/training
│   ├── scripts/                 # Training scripts
│   │   ├── train_model.py       # Main training script
│   │   ├── gettingstarted.py    # Existing training script
│   │   └── get-started.py       # Existing training script
│   ├── notebooks/               # Experiment notebooks
│   │   └── get-started.ipynb    # MLflow experiment Jupyter notebook
│   └── docker/                  # Training Docker
│       └── Dockerfile           # Training environment
├── serving/                     # Model serving
│   ├── api/                     # API server
│   │   ├── app.py               # Flask API server
│   │   └── test_api.py          # API test client
│   └── docker/                  # Serving Docker
│       └── Dockerfile           # Serving environment
├── shared/                      # Shared utilities
│   └── utils/                   # Common functions
│       └── mlflow_utils.py      # MLflow utilities
├── dags/                        # Airflow DAG
│   ├── mlflow_job_dag.py        # Existing training-only DAG
│   ├── mlflow_complete_pipeline_dag.py  # Complete pipeline DAG
│   └── mlflow_serving_dag.py    # Serving-only DAG
├── k8s/                         # k8s airflow, mlflow installation reference
├── requirements.txt             # Python package dependencies
└── README.md                    # Project documentation
```

## 🚀 Key Features

- **External MLflow Server Integration**: Send experiment results to existing MLflow server
- **External Airflow Server Integration**: Execute DAGs on existing Airflow server
- **Docker Containerization**: Reproducible ML environment setup
- **Flask API Service**: Serve MLflow models via REST API
- **Jupyter Notebook**: Experiment and development environment
- **Modular Structure**: Separation of training and serving
- **Complete MLOps Pipeline**: Training → Registration → Deployment → Serving

## 🛠️ Technology Stack

- **ML Framework**: MLflow, scikit-learn, pandas, numpy
- **Orchestration**: Apache Airflow (external server)
- **Containerization**: Docker
- **Web Framework**: Flask
- **Language**: Python 3.10+

## 🔧 Environment Setup

### 1. Create Working Environment

```bash
cd tz-mlops-mlflow
rm -Rf venv
pyenv install 3.10.13
pyenv local 3.10.13
python -m venv env
source env/bin/activate
python3 -V  # Python 3.10.x

pip3 install -r requirements.txt
pip3 install papermill
```

### 2. Jupyter Kernel Setup (Optional)

```bash
# Force Python3 version setting
pip install ipykernel
python -m ipykernel install --user --name=python3 --display-name "Python 3 (venv)"
jupyter kernelspec list
```

### 3. Environment Variables Setup

```bash
# External MLflow server configuration
export MLFLOW_TRACKING_URI=https://mlflow.new-nation.church
export MLFLOW_EXPERIMENT_NAME=production_experiment
export MLFLOW_TRACKING_USERNAME=user
export MLFLOW_TRACKING_PASSWORD=xxx

# External Airflow server configuration
export AIRFLOW_API_URL=https://airflow-admin.new-nation.church
```

### 3. **Build and Push Docker Images**

#### Option A: Using the build script (Recommended)
```bash
# Build and push in one command
./training/ml_training.sh --push

# Or build only
./training/ml_training.sh
```

#### Option B: Manual build from project root
```bash
# Build from project root directory
docker build -f training/docker/Dockerfile -t doohee323/ml_training:latest .
docker push doohee323/ml_training:latest
```

#### Option C: Build from training directory (Legacy - may have path issues)
```bash
cd training
docker build -f docker/Dockerfile -t doohee323/ml_training:latest .
docker push doohee323/ml_training:latest
```

## 🏃‍♂️ Usage

## 📋 **Scenario 1: New Model Development - Detailed Step-by-Step Guide**

### **Step 1: Environment Setup and Preparation**

#### 1.1 Current Environment Check
```bash
# Check current directory and project structure
pwd
ls -la

# Check Python version
python3 --version

# Activate virtual environment (if exists)
source env/bin/activate  # or source venv/bin/activate
```

#### 1.2 Install Required Packages
```bash
# Install requirements.txt
pip install -r requirements.txt

# Install additional packages
pip install papermill requests
```

#### 1.3 Environment Variables Setup
```bash
# MLflow server configuration
export MLFLOW_TRACKING_URI=https://mlflow.new-nation.church
export MLFLOW_EXPERIMENT_NAME=production_experiment
export MLFLOW_TRACKING_USERNAME=user
export MLFLOW_TRACKING_PASSWORD=xxx
```

### **Step 2: Model Development (Jupyter Notebook)**

#### 2.1 Run Notebook
```bash
# Run experiment notebook
jupyter-notebook training/notebooks/get-started.ipynb
```

#### 2.2 Tasks to Perform in Notebook
- Data loading and preprocessing
- Model training and experimentation
- Save experiment results to MLflow
- Model performance verification and hyperparameter tuning
- Select optimal model

### **Step 3: Training Script Development**

#### 3.1 Run Training Script
```bash
cd training/scripts
python train_model.py
```

#### 3.2 Training Completion Verification
When training is completed, the following messages will appear:
```
INFO:__main__:Best Hyperparameters: {...}
INFO:__main__:Mean Squared Error: X.XXXX
INFO:__main__:Root Mean Squared Error: X.XXXX
INFO:__main__:ML pipeline completed successfully!
```

#### 3.3 MLflow Registration Verification
- Access MLflow UI (https://mlflow.new-nation.church)
- Check experiment results and model
- Verify that model is properly registered

### **Step 4: Docker Image Build**

#### 4.1 Build Training Image
```bash
cd training
docker build -f docker/Dockerfile -t doohee323/ml_training:latest .
```

#### 4.2 Build Serving Image
```bash
cd serving
docker build -f docker/Dockerfile -t doohee323/ml_serving:latest .
```

#### 4.3 Verify Image Build
```bash
# Check built images
docker images | grep doohee323

# Check image details
docker inspect doohee323/ml_training:latest
docker inspect doohee323/ml_serving:latest
```

### **Step 5: Docker Image Push**

#### 5.1 Docker Hub Login
```bash
docker login
# Username: doohee323
# Password: [Docker Hub password]
```

#### 5.2 Push Images
```bash
# Push training image
docker push doohee323/ml_training:latest

# Push serving image
docker push doohee323/ml_serving:latest

## 🌐 Kubernetes Networking

### **Network Architecture in Kubernetes**

In Kubernetes, each pod has its own network namespace, which means:

1. **Same Pod Communication**: `localhost` works only within the same pod
2. **Cross-Pod Communication**: Use service names (e.g., `http://serving-service:8080`)
3. **External Access**: Use Ingress or LoadBalancer

### **Service Discovery in Kubernetes**

```yaml
# Example Kubernetes Service for MLflow Serving
apiVersion: v1
kind: Service
metadata:
  name: mlflow-serving-service
spec:
  selector:
    app: mlflow-serving
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

### **Access Patterns**

| Environment | Access Method | Example |
|-------------|---------------|---------|
| **Local Development** | `localhost` | `http://localhost:8080/health` |
| **Same Pod** | `localhost` | `http://localhost:8080/health` |
| **Different Pod** | Service Name | `http://serving-service:8080/health` |
| **External** | Ingress/LoadBalancer | `https://your-domain.com/health` |

### **DAG Configuration for Kubernetes**

When using Airflow DAGs in Kubernetes:

1. **Use KubernetesPodOperator** for pod-based tasks
2. **Configure service names** for inter-service communication
3. **Set up proper networking** for external access
4. **Use environment variables** for dynamic endpoint configuration
```

#### 5.3 Verify Push
```bash
# Check images on Docker Hub
curl https://hub.docker.com/v2/repositories/doohee323/ml_training/tags/
curl https://hub.docker.com/v2/repositories/doohee323/ml_serving/tags/
```

### **Step 6: Airflow Variable Setup**

#### 6.1 Access Airflow UI
- URL: https://airflow-admin.new-nation.church/
- Navigate to Admin → Variables menu

#### 6.2 Variable Configuration
Add the following Variables:

| Key | Value |
|-----|-------|
| `MLFLOW_TRACKING_URI` | `https://mlflow.new-nation.church` |
| `MLFLOW_TRACKING_USERNAME` | `user` |
| `MLFLOW_TRACKING_PASSWORD` | `xxx` |
| `MLFLOW_EXPERIMENT_NAME` | `production_experiment` |

### **Step 7: Airflow DAG Deployment**

#### 7.1 Select DAG File
```bash
# Use complete pipeline DAG (recommended)
cp dags/mlflow_complete_pipeline_dag.py tz-airflow-dags/airflow-dags/

# Or training-only DAG
cp dags/mlflow_job_dag.py tz-airflow-dags/airflow-dags/

# Or serving-only DAG
cp dags/mlflow_serving_dag.py tz-airflow-dags/airflow-dags/
```

#### 7.2 GitOps Deployment
```bash
# Clone Airflow DAG repository (skip if already exists)
git clone https://github.com/doohee323/tz-airflow-dags.git

# Copy DAG file
cp dags/mlflow_complete_pipeline_dag.py tz-airflow-dags/airflow-dags/

# GitOps deployment
cd tz-airflow-dags
git add airflow-dags/mlflow_complete_pipeline_dag.py
git commit -m 'Add complete MLflow pipeline DAG'
git push
```

### **Step 8: Execute in Airflow**

#### 8.1 Verify DAG in Airflow UI
- URL: https://airflow-admin.new-nation.church/
- Check `mlflow_complete_pipeline` in DAG list
- Verify DAG is activated (On/Off toggle)

#### 8.2 Execute DAG
- Click "Trigger DAG" button on DAG page
- Set execution parameters (if needed)
- Click "Trigger" button

#### 8.3 Monitor Execution Status
- Check task execution status in Graph View
- Check detailed logs in Log View
- Monitor success/failure status of each task

### **Step 9: Result Verification and Validation**

#### 9.1 Verify Results in MLflow UI
- URL: https://mlflow.new-nation.church
- Check experiment results and model
- Verify model version and performance metrics

#### 9.2 Verify API Service
```bash
# Check if API service is running
# Local Development Testing
curl http://localhost:8080/health

# Prediction test (Local Development)
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'

# Batch prediction test (Local Development)
curl -X POST http://localhost:8080/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"features": [[5.1, 3.5, 1.4, 0.2], [6.3, 3.3, 4.7, 1.6]]}'

# Kubernetes Environment Testing
# Note: In Kubernetes, use service names or external endpoints
# curl http://serving-service:8080/health
# curl http://your-ingress-domain/health
```

#### 9.3 Performance Test
```bash
# Run API test script
cd serving/api
python test_api.py
```

### **Step 10: Monitoring and Alert Setup**

#### 10.1 Airflow Alert Setup
- Configure email alerts on failure
- Setup Slack/Teams webhook
- Configure success/failure notifications

#### 10.2 Model Monitoring
- Track model performance metrics
- Detect data drift
- Monitor API response time

---

## 🔄 MLflow Model Usage

#### 1. **Full Pipeline (mlflow_complete_pipeline_dag.py)**
```
[Model Training] → [MLflow Registration] → [Model Deployment] → [API Serving] → [Testing] → [Monitoring]
```

#### 2. **Serving Only (mlflow_serving_dag.py)**
```
[Load Existing Model] → [API Serving] → [Testing] → [Performance Measurement]
```

### **Airflow DAG Roles**

| DAG | Role | Description |
|-----|------|-------------|
| `mlflow_job_dag` | Training Only | Registers model to MLflow after training |
| `mlflow_complete_pipeline` | Full Pipeline | Training → Registration → Deployment → Serving → Testing |
| `mlflow_serving_dag` | Serving Only | Serves existing model via API |

### **Actual Usage Examples**

#### 1. **Automated Model Deployment**
```python
# Run in Airflow DAG
deploy_model = DockerOperator(
    task_id='deploy_model',
    image='doohee323/ml_serving:latest',
    environment={
        'MODEL_NAME': 'Best Randomforest Model',
        'MODEL_VERSION': 'latest',
    }
)
```

#### 2. **Model Performance Testing**
```python
# Automatic testing in Airflow DAG
def test_model_performance(**context):
    response = requests.post(
        'http://localhost:8080/predict',  # Local development only
        json={"features": [5.1, 3.5, 1.4, 0.2]}
    )
    return response.status_code == 200
```

#### 3. **Model Monitoring**
```python
# Setting up monitoring in Airflow DAG
def setup_monitoring(**context):
    monitoring_config = {
        "metrics_endpoint": "http://localhost:8080/health",  # Local development only
        "prediction_endpoint": "http://localhost:8080/predict",  # Local development only
        "alert_threshold": 0.95
    }
    return True
```

## 🚀 Flask API Service

### API Server Execution

```bash
# Run locally
cd serving/api
python app.py

# Or run with Docker
cd serving
docker build -f docker/Dockerfile -t mlflow-api:latest .
docker run -p 8080:8080 mlflow-api:latest
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation |
| `/health` | GET | Health check |
| `/model/info` | GET | Model information |
| `/example` | GET | Example data |
| `/predict` | POST | Single prediction |
| `/predict/batch` | POST | Batch prediction |

### API Usage Examples

#### Single Prediction
```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

#### Batch Prediction
```bash
curl -X POST http://localhost:8080/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"features": [[5.1, 3.5, 1.4, 0.2], [6.3, 3.3, 4.7, 1.6]]}'
```

### API Testing

```bash
# Run API test script
cd serving/api
python test_api.py
```

## 🔍 External Server Connection Information

### MLflow Server
- **URL**: https://mlflow.new-nation.church
- **Function**: Experiment tracking, model management, artifact storage

### Airflow Server
- **URL**: https://airflow-admin.new-nation.church/
- **Function**: Workflow orchestration, DAG execution monitoring

## 📊 Monitoring

### MLflow Monitoring
- Experiment parameter and metric tracking
- Model performance comparison
- Artifact version management

### Airflow Monitoring
- DAG execution status check
- Task success/failure logs
- Workflow performance metrics

### API Monitoring
- Health check endpoint
- Prediction request logs
- Model loading status check

## 🏗️ Project Structure Advantages

### 1. **Separation of Concerns (SoC)**
- **Training**: Model development, experimentation, hyperparameter tuning
- **Serving**: Model deployment, API service, prediction
- **Common**: Reusable utilities

### 2. **Independent Deployment**
- Training and serving can be deployed independently
- Use different Docker images
- Different resource requirements

### 3. **Scalability**
- Add new models by modifying only training
- API service works without model changes
- Reuse common utilities

### 4. **Maintainability**
- Minimize code duplication
- Clear responsibility separation
- Easier testing

### 5. **Complete MLOps Pipeline**
- **Training**: Model development and experimentation
- **Registration**: Save model to MLflow
- **Deployment**: Deploy with Docker container
- **Serving**: Predict via REST API
- **Monitoring**: Performance and status tracking

## 🚨 Troubleshooting Guide

### **Common Issues**

#### 1. **MLflow Connection Error**
```bash
# Check environment variables
echo $MLFLOW_TRACKING_URI
echo $MLFLOW_TRACKING_USERNAME
echo $MLFLOW_TRACKING_PASSWORD

# Network connection check
curl -I https://mlflow.new-nation.church
```

#### 2. **Docker Build Error**
```bash
# Check Docker daemon status
docker info

# Check image build logs
docker build -f docker/Dockerfile -t test-image . --progress=plain
```

#### 3. **Airflow DAG Execution Error**
```bash
# Check DAG syntax errors
python -c "import dags.mlflow_complete_pipeline_dag"

# Check Airflow Variables
airflow variables get MLFLOW_TRACKING_URI
```

#### 4. **API Service Error**
```bash
# Check port usage
lsof -i :8080

# Check container logs
docker logs mlflow_api_service
```

#### 5. **California Housing Dataset Download Error**
```bash
# Check if dataset is pre-downloaded in container
docker exec -it <container_name> ls -la /app/scikit_learn_data/

# Check if synthetic data is being used
docker logs <container_name> | grep "synthetic"

# Verify data loading methods
docker exec -it <container_name> python -c "
from sklearn.datasets import fetch_california_housing
try:
    housing = fetch_california_housing()
    print(f'Dataset loaded: {housing.data.shape}')
except Exception as e:
    print(f'Error: {e}')
"
```

**Solution**: The training script now includes robust fallback options:
1. **Local file loading**: Tries to load from `/app/scikit_learn_data`
2. **Default cache**: Uses scikit-learn's default cache location
3. **Alternative location**: Tries downloading to `/tmp/scikit_learn_data`
4. **Synthetic data**: Creates realistic synthetic data for testing

The Docker build process also pre-downloads the dataset when possible.

#### 6. **Git Warnings in MLflow**
```bash
# Check if Git is installed in container
docker exec -it <container_name> git --version

# Check environment variable
docker exec -it <container_name> echo $GIT_PYTHON_REFRESH
```

**Solution**: Git warnings are now suppressed by:
1. **Installing Git**: Added `git` to Docker dependencies
2. **Environment variable**: Set `GIT_PYTHON_REFRESH=quiet` in Dockerfile
3. **Code-level suppression**: Added `os.environ['GIT_PYTHON_REFRESH'] = 'quiet'` in Python scripts

**Current Implementation**:
- Automatic model size reduction when upload fails
- Fallback to compressed model version
- Detailed logging of optimization steps
- Nginx ingress configured for 1GB upload limit

#### 9. **Airflow 2.0+ Import Errors**
```bash
# Error: ModuleNotFoundError: No module named 'airflow.operators.python_operator'
```

**Solution**: Airflow 2.0+ compatibility fixes:
1. **PythonOperator import**: 
   ```python
   # Old (Airflow 1.x)
   from airflow.operators.python_operator import PythonOperator
   
   # New (Airflow 2.0+)
   from airflow.operators.python import PythonOperator
   ```

2. **HTTP Provider**: Install if needed:
   ```bash
   pip install apache-airflow-providers-http
   ```

3. **Docker Provider**: Install if needed:
   ```bash
   pip install apache-airflow-providers-docker
   ```

**Fixed Files**:
- `dags/mlflow_serving_dag.py`: Updated PythonOperator import
- `dags/mlflow_complete_pipeline_dag.py`: Updated PythonOperator import

#### 10. **Airflow 2.4+ Schedule Parameter Error**
```bash
# Error: TypeError: DAG.__init__() got an unexpected keyword argument 'schedule_interval'
```

**Solution**: Airflow 2.4+ schedule parameter change:
```python
# Old (Airflow < 2.4)
dag = DAG(
    dag_id='example',
    schedule_interval=timedelta(days=1),  # ❌ Deprecated
    ...
)

# New (Airflow 2.4+)
dag = DAG(
    dag_id='example',
    schedule=timedelta(days=1),  # ✅ New parameter name
    ...
)
```

**Fixed Files**:
- `dags/mlflow_serving_dag.py`: Changed `schedule_interval` to `schedule`
- `dags/mlflow_complete_pipeline_dag.py`: Changed `schedule_interval` to `schedule`

#### 11. **DockerOperator Ports Parameter Error**
```bash
# Error: TypeError: Invalid arguments were passed to DockerOperator (task_id: deploy_model_service). Invalid arguments were: **kwargs: {'ports': ['8080:8080']}
```

**Solution**: Airflow 2.0+ DockerOperator parameter changes:
```python
# Old (Airflow 1.x)
DockerOperator(
    task_id='deploy',
    image='example:latest',
    ports=['8080:8080'],  # ❌ Not supported in Airflow 2.0+
    ...
)

# New (Airflow 2.0+)
DockerOperator(
    task_id='deploy',
    image='example:latest',
    # ports=['8080:8080'],  # ✅ Removed - use docker-compose or separate deployment
    ...
)
```

**Alternative Solutions**:
1. **Use KubernetesPodOperator** for port mapping
2. **Use docker-compose** for complex container configurations
3. **Deploy containers separately** and use service discovery

**Fixed Files**:
- `dags/mlflow_serving_dag.py`: Removed `ports` parameter
- `dags/mlflow_complete_pipeline_dag.py`: Removed `ports` parameter
