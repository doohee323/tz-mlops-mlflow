#!/usr/bin/env bash
# MinIO for MLflow artifacts (namespace: devops)
# In-cluster: http://minio.devops.svc.cluster.local:9000

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "${REPO_ROOT}/scripts/load-config.sh"

cd "${REPO_ROOT}/k8s/minio"
shopt -s expand_aliases
alias k='kubectl --kubeconfig ~/.kube/config'

k8s_project=$(prop 'project' 'project')
k8s_domain=$(prop 'project' 'domain')
basic_password=$(prop 'project' 'basic_password')
[[ -z "${k8s_project}" ]] && k8s_project=drillquiz
[[ -z "${basic_password}" ]] && basic_password=ChangeMeSecurePassword123
NS=devops

kubectl create namespace ${NS} --dry-run=client -o yaml | kubectl apply -f -

helm repo add minio https://charts.min.io/ 2>/dev/null || true
helm repo update

sed -e "s/k8s_project/${k8s_project}/g" -e "s/basic_password/${basic_password}/g" values.yaml > values.yaml_bak
helm upgrade --install minio minio/minio --version 5.4.0 -n ${NS} -f values.yaml_bak

echo "Waiting for MinIO to be ready..."
sleep 30
kubectl wait --for=condition=ready pod -l app=minio -n ${NS} --timeout=120s 2>/dev/null || true

# Create mlflow bucket (for MLflow artifact storage)
minio_access_key=$(prop 'project' 'minio_access_key')
minio_secret_key=$(prop 'project' 'minio_secret_key')
if [[ -n "${minio_access_key}" && -n "${minio_secret_key}" ]]; then
  echo "Creating mlflow bucket in MinIO..."
  MC_HOST="http://${minio_access_key}:${minio_secret_key}@minio.${NS}.svc.cluster.local:9000"
  kubectl run mc-bucket-init --rm -i --restart=Never -n ${NS} \
    --image=minio/mc:latest \
    --env="MC_HOST_myminio=${MC_HOST}" \
    -- mc mb myminio/mlflow --ignore-existing 2>/dev/null && echo "  → mlflow bucket ready" || true
else
  echo "  → Set minio_access_key and minio_secret_key in .k8s/project to auto-create mlflow bucket"
fi

# Ingress (also applied by bootstrap)
sed -e "s/k8s_project/${k8s_project}/g" -e "s/k8s_domain/${k8s_domain}/g" minio-ingress.yaml | kubectl apply -f - -n ${NS}

echo "MinIO installed. API: http://minio.${NS}.svc.cluster.local:9000"
