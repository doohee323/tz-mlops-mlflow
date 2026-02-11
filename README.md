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

### run.sh Pipeline Flow (Step Descriptions)

Steps performed when running `./run.sh` and what each step does:

| Step | Stage | Description |
|------|-------|-------------|
| **1** | Environment Setup | Activate `env/` venv, verify Python version (must match Docker 3.12), set `MLFLOW_TRACKING_URI` and `MLFLOW_EXPERIMENT_NAME` |
| **2** | Model Development (Jupyter) | Data loading, preprocessing, experiments, and MLflow logging in Jupyter Notebook. Script skips this manual step and waits for Enter |
| **3** | Training Script Execution | Run `train_model.py` — hyperparameter tuning (GridSearchCV), model training, register metrics/model in MLflow, upload artifacts (S3/MinIO) |
| **4** | Docker Image Build | `ml_training`: training code and environment image; `ml_serving`: Flask API serving image. Verify with `docker images` |
| **5** | Docker Image Push | After `docker login`, push `ml_training` and `ml_serving` to Docker Hub. Airflow/K8s pull these images to run pipelines |
| **6** | Airflow Variable Setup | Manual step. Add `MLFLOW_TRACKING_URI`, `MLFLOW_EXPERIMENT_NAME` in Airflow UI → Admin → Variables. DAGs reference these variables |
| **7** | Airflow DAG Deployment | Clone `tz-airflow-dags` repo (if missing), copy `mlflow_training_pipeline_dag.py`, deploy via git add/commit/push. Airflow loads DAGs via repo sync |
| **8** | Execute in Airflow | Manual step. Trigger `mlflow_training_pipeline` DAG in Airflow UI. Training/serving pipeline runs on K8s |
| **9** | Result Verification | Check experiments and models in MLflow UI, API health check (`localhost:8080`), prediction test with `test_api.py`. API is reachable only when running locally or on server |
| **10** | Monitoring | Manual. Configure Airflow alerts, model monitoring, drift detection, and other operations |

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
│   ├── mlflow_training_pipeline_dag.py  # Complete pipeline DAG
│   └── mlflow_serving_dag.py    # Serving-only DAG
├── k8s/                         # k8s installation (PostgreSQL, MinIO, MLflow, Airflow, Jupyter)
│   ├── postgresql/              # PostgreSQL for MLflow
│   ├── minio/                   # MinIO for MLflow artifacts
│   ├── mlflow/                  # MLflow tracking server
│   ├── airflow/                 # Apache Airflow
│   ├── jupyter/                 # JupyterHub
│   └── project.example          # Config example for /root/.k8s/project
├── scripts/
│   └── load-config.sh           # prop function, config loader
├── run.sh                       # MLOps pipeline runner (README Scenario 1)
├── bootstrap.sh                 # One-shot infrastructure install
├── requirements.txt             # Python package dependencies (MLflow, training)
├── requirements-airflow.txt     # Airflow for DAG dev (optional, separate venv)
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
- **Language**: Python 3.12 (matches Docker)

## 🔧 Environment Setup

### 0. Bootstrap (K8s infrastructure)

One-shot install of PostgreSQL, MinIO, MLflow, Airflow. Config: `/root/.k8s/project`.

```bash
# 1. Create config: cp k8s/project.example /root/.k8s/project
# 2. Edit /root/.k8s/project with your values
# 3. Run bootstrap
./bootstrap.sh
```

| Component | Skip if exists | Namespace |
|-----------|----------------|-----------|
| Ingress NGINX | ✅ | default |
| PostgreSQL | ✅ | devops-dev |
| MinIO | ✅ | devops |
| MLflow | — | mlflow |
| Airflow | — | airflow |
| Jupyter | ✅ | jupyterhub |

### 1. Create Working Environment

Python version must match Docker (see `training/docker/Dockerfile`). Use `scripts/ensure-venv.sh`:

```bash
cd tz-mlops-mlflow
./scripts/ensure-venv.sh --create   # Creates env/ with Docker Python version
source env/bin/activate
pip install -r requirements.txt
pip install papermill
```

**Airflow DAG development** (optional, separate from main env due to dependency conflicts):

```bash
python -m venv env-airflow
source env-airflow/bin/activate
pip install -r requirements-airflow.txt
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
# MLflow (auth disabled in default setup)
export MLFLOW_TRACKING_URI=https://mlflow.drillquiz.com
export MLFLOW_EXPERIMENT_NAME=production_experiment

# Airflow
export AIRFLOW_API_URL=https://airflow-admin.drillquiz.com
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

### **Quick Start: run.sh (Recommended)**

`run.sh` automates Scenario 1 (New Model Development) step-by-step. Stops on first error.

```bash
# Prerequisites: env/ exists, pip install -r requirements.txt done
./run.sh
```

| Option | Description |
|--------|-------------|
| `./run.sh` | Interactive: prompts for manual steps (Jupyter, Airflow UI, git push) |
| `NON_INTERACTIVE=1 ./run.sh` | Skip prompts (for CI); manual steps still need separate handling |

**Steps executed**: Environment check → Training script → Docker build → Docker push → DAG copy & git commit (with confirmation). Steps 2, 6, 8 require manual actions (Jupyter, Airflow Variables, DAG trigger).

---

## 📋 **Scenario 1: New Model Development - Detailed Step-by-Step Guide**

### **Step 1: Environment Setup and Preparation**

> See **1. Create Working Environment** above for initial setup (`ensure-venv.sh`, `pip install -r requirements.txt`).

#### 1.1 Activate and Verify
```bash
source env/bin/activate
python --version   # Should match Docker (3.12)
```

#### 1.2 Environment Variables (optional)
```bash
# MLflow (auth disabled in default bootstrap)
export MLFLOW_TRACKING_URI=https://mlflow.drillquiz.com   # or from .k8s/project domain
export MLFLOW_EXPERIMENT_NAME=production_experiment
```

### **Step 2: Model Development (Jupyter Notebook)**

#### 2.1 Run Notebook
```bash
# Run experiment notebook
# pip install jupyter notebook
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
- Access MLflow UI (https://mlflow.drillquiz.com)
- Check experiment results and model
- Verify that model is properly registered

### **Step 4: Docker Image Build**

#### 4.1 Build Training Image
```bash
# cd tz-mlops-mlflow
# docker build -f training/docker/Dockerfile -t doohee323/ml_training:latest .
bash ./training/ml_training.sh

```

#### 4.2 Build Serving Image
```bash
#cd tz-mlops-mlflow
docker rmi doohee323/ml_serving:latest
docker build -f serving/docker/Dockerfile -t doohee323/ml_serving:latest .
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
- URL: https://airflow-admin.drillquiz.com/
- Navigate to Admin → Variables menu

#### 6.2 Variable Configuration
Add the following Variables (required for `mlflow_training_pipeline_dag`):

**Option A: Import JSON file (recommended)**
1. Airflow UI → **Admin** → **Variables** → **Import Variables**
2. Upload `k8s/airflow/airflow-variables.json`
3. Select conflict resolution (Overwrite / Skip / Fail) and import

**Option B: Add manually**

| Key | Value |
|-----|-------|
| `MLFLOW_TRACKING_URI` | `https://mlflow.${domain}` (e.g. `https://mlflow.drillquiz.com`) |
| `MLFLOW_EXPERIMENT_NAME` | `production_experiment` |

Optional (if MLflow auth enabled):

| Key | Value |
|-----|-------|
| `MLFLOW_TRACKING_USERNAME` | `user` |
| `MLFLOW_TRACKING_PASSWORD` | `xxx` |

### **Step 7: Airflow DAG Deployment**

#### 7.1 Select DAG File
```bash
# Use complete pipeline DAG (recommended)
cp -Rf dags/mlflow_training_pipeline_dag.py tz-airflow-dags/airflow-dags/

# Or training-only DAG
cp -Rf dags/mlflow_serving_dag.py tz-airflow-dags/airflow-dags/

# Or serving-only DAG
cp -Rf dags/mlflow_serving_dag.py tz-airflow-dags/airflow-dags/
```

#### 7.2 GitOps Deployment
```bash
# Clone Airflow DAG repository (skip if already exists)
git clone https://github.com/doohee323/tz-airflow-dags.git

# Copy DAG file
cp -Rf dags/mlflow_training_pipeline_dag.py tz-airflow-dags/airflow-dags/

# GitOps deployment
cd tz-airflow-dags
git add airflow-dags/mlflow_training_pipeline_dag.py
git commit -m 'Add complete MLflow pipeline DAG'
git push
```

### **Step 8: Execute in Airflow**

#### 8.1 Verify DAG in Airflow UI
- URL: https://airflow-admin.drillquiz.com/
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
- URL: https://mlflow.drillquiz.com
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

#### 1. **Full Pipeline (mlflow_training_pipeline_dag.py)**
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
- **URL**: https://mlflow.drillquiz.com
- **Function**: Experiment tracking, model management, artifact storage

### Airflow Server
- **URL**: https://airflow-admin.drillquiz.com/
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
