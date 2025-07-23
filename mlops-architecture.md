# MLOps Architecture Guide

## Standard MLOps Architecture

### 1. Training Pipeline (Airflow)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Pipeline │───▶│ Model Training  │───▶│ Model Registry  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. Serving Pipeline (GitOps)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Model Registry  │───▶│ Git Repository  │───▶│ K8s Deployment  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Recommended Serving Architecture

### Option 1: ArgoCD + GitOps
```yaml
# Git Repository Structure
mlops-serving/
├── k8s/
│   ├── base/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── kustomization.yaml
│   └── overlays/
│       ├── staging/
│       └── production/
├── scripts/
│   ├── deploy.sh
│   └── rollback.sh
└── monitoring/
    ├── prometheus/
    └── grafana/
```

### Option 2: Kubeflow Serving
```yaml
# Kubeflow KFServing
apiVersion: "serving.kubeflow.org/v1beta1"
kind: "InferenceService"
metadata:
  name: "mlflow-model"
spec:
  predictor:
    sklearn:
      storageUri: "s3://mlflow/models/Best-Randomforest-Model"
```

### Option 3: Seldon Core
```yaml
# Seldon Core
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: mlflow-model
spec:
  predictors:
  - name: default
    replicas: 1
    graph:
      name: classifier
      type: MODEL
      modelUri: s3://mlflow/models/Best-Randomforest-Model
```

## Current Project Improvement Plan

### 1. Airflow DAG Modification (Training Only)
```python
# mlflow_training_pipeline_dag.py
dag = DAG(
    dag_id='mlflow_training_pipeline',
    description='MLflow Training Pipeline only',
    # ...
)

# Tasks
train_model >> validate_model >> register_model >> notify_completion
```

### 2. Separate Serving Pipeline
```python
# mlflow_serving_pipeline_dag.py
dag = DAG(
    dag_id='mlflow_serving_pipeline',
    description='MLflow Serving Pipeline',
    # ...
)

# Tasks
check_model_registry >> deploy_service >> health_check >> monitor_service
```

### 3. GitOps Workflow
```bash
# 1. When model is registered in MLflow
# 2. Update deployment.yaml in Git Repository
# 3. ArgoCD automatically deploys to K8s
# 4. Monitoring and alerts
```

## Recommendations

### 1. Phased Migration
1. **Phase 1**: Separate Training and Serving
2. **Phase 2**: Introduce GitOps
3. **Phase 3**: Introduce specialized Serving platform

### 2. Tool Selection
- **Small Scale**: ArgoCD + GitOps
- **Medium Scale**: Kubeflow Serving
- **Large Scale**: Seldon Core + MLflow

### 3. Monitoring
- **Prometheus + Grafana**: Metric collection
- **Jaeger**: Distributed tracing
- **AlertManager**: Alert management 