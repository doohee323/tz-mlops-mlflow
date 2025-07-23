#!/bin/bash

# GitOps 기반 Serving 배포 스크립트
set -e

echo "🚀 Starting GitOps-based serving deployment..."

# Configuration
GIT_REPO="your-git-repo/mlops-serving"
MODEL_NAME="Best Randomforest Model"
MODEL_VERSION="latest"
ENVIRONMENT="staging"  # or production

# 1. Check if model exists in MLflow
echo "📋 Checking model in MLflow registry..."
python3 -c "
import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri('https://mlflow.new-nation.church')
client = MlflowClient()

models = client.search_registered_models()
model_names = [model.name for model in models]

if '$MODEL_NAME' in model_names:
    print(f'✅ Model {MODEL_NAME} found in registry')
    exit(0)
else:
    print(f'❌ Model {MODEL_NAME} not found')
    print(f'Available models: {model_names}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Model not found in registry. Aborting deployment."
    exit 1
fi

# 2. Clone serving repository
echo "📥 Cloning serving repository..."
git clone https://github.com/$GIT_REPO.git serving-repo
cd serving-repo

# 3. Update deployment configuration
echo "🔧 Updating deployment configuration..."
cat > k8s/overlays/$ENVIRONMENT/deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlflow-serving
  namespace: airflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mlflow-serving
  template:
    metadata:
      labels:
        app: mlflow-serving
    spec:
      containers:
      - name: mlflow-serving
        image: doohee323/ml_serving:latest
        ports:
        - containerPort: 8080
        env:
        - name: MLFLOW_TRACKING_URI
          value: "https://mlflow.new-nation.church"
        - name: MODEL_NAME
          value: "$MODEL_NAME"
        - name: MODEL_VERSION
          value: "$MODEL_VERSION"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
EOF

# 4. Update kustomization
echo "📝 Updating kustomization..."
cat > k8s/overlays/$ENVIRONMENT/kustomization.yaml << EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base
- deployment.yaml

namespace: airflow

patches:
- target:
    kind: Service
    name: mlflow-serving
  patch: |-
    - op: replace
      path: /spec/type
      value: ClusterIP
EOF

# 5. Commit and push changes
echo "💾 Committing changes..."
git add .
git commit -m "Deploy model $MODEL_NAME version $MODEL_VERSION to $ENVIRONMENT"
git push origin main

echo "✅ Changes pushed to Git repository"
echo "🔄 ArgoCD will automatically deploy the changes"
echo "⏳ Waiting for deployment to be ready..."

# 6. Wait for ArgoCD deployment (if ArgoCD is available)
if command -v kubectl &> /dev/null; then
    echo "🔍 Checking deployment status..."
    kubectl wait --for=condition=available --timeout=300s deployment/mlflow-serving -n airflow
    echo "✅ Deployment is ready!"
else
    echo "⚠️ kubectl not available. Please check deployment manually."
fi

echo "🎉 GitOps deployment completed!"
echo "📊 Monitor deployment at: http://your-argocd-url" 