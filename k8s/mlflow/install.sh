#!/usr/bin/env bash
# MLflow (namespace: mlflow)
# Requires: PostgreSQL, MinIO in cluster

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "${REPO_ROOT}/scripts/load-config.sh"

cd "${REPO_ROOT}/k8s/mlflow"
shopt -s expand_aliases
alias k='kubectl --kubeconfig ~/.kube/config'

k8s_project=$(prop 'project' 'project')
k8s_domain=$(prop 'project' 'domain')
[[ -z "${k8s_domain}" ]] && k8s_domain="local"
admin_password=$(prop 'project' 'admin_password')
[[ -z "${admin_password}" ]] && admin_password='DevOps!323'
MLFLOW_IMAGE="${MLFLOW_IMAGE:-$(prop 'project' 'mlflow_image')}"
[[ -z "${MLFLOW_IMAGE}" ]] && { echo "Set mlflow_image in .k8s/project (run k8s/mlflow/build.sh first)"; exit 1; }
minio_access_key=$(prop 'project' 'minio_access_key')
minio_secret_key=$(prop 'project' 'minio_secret_key')
[[ -z "${minio_access_key}" || -z "${minio_secret_key}" ]] && { echo "Set minio_access_key and minio_secret_key in .k8s/project"; exit 1; }
NS=mlflow

helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
helm repo update

# External PostgreSQL + MinIO (subcharts disabled, use externalDatabase + externalS3)
PG_HOST="devops-postgres-postgresql.devops-dev.svc.cluster.local"
MINIO_HOST="minio.devops.svc.cluster.local"

helm upgrade --install mlflow oci://registry-1.docker.io/bitnamicharts/mlflow \
  --namespace ${NS} --create-namespace \
  --set global.imagePullSecrets[0].name=tz-registrykey \
  --set global.security.allowInsecureImages=true \
  --set postgresql.enabled=false \
  --set minio.enabled=false \
  --set externalDatabase.host=${PG_HOST} \
  --set externalDatabase.port=5432 \
  --set externalDatabase.user=admin \
  --set externalDatabase.database=mlflow \
  --set externalDatabase.authDatabase=mlflow \
  --set externalDatabase.dialectDriver=postgresql \
  --set externalDatabase.password="${admin_password}" \
  --set externalS3.host=${MINIO_HOST} \
  --set externalS3.port=9000 \
  --set externalS3.bucket=mlflow \
  --set externalS3.protocol=http \
  --set externalS3.accessKeyID="${minio_access_key}" \
  --set externalS3.accessKeySecret="${minio_secret_key}" \
  --set tracking.auth.enabled=false \
  --set tracking.runUpgradeDB=false \
  --set tracking.extraEnvVars[0].name=MLFLOW_S3_ENDPOINT_URL \
  --set tracking.extraEnvVars[0].value=http://${MINIO_HOST}:9000 \
  --set image.registry="$(echo "${MLFLOW_IMAGE}" | cut -d/ -f1)" \
  --set image.repository="$(echo "${MLFLOW_IMAGE}" | cut -d/ -f2- | cut -d: -f1)" \
  --set image.tag="$(echo "${MLFLOW_IMAGE}" | cut -d: -f2)" \
  --set waitContainer.image.registry=docker.io \
  --set waitContainer.image.repository=bitnami/os-shell \
  --set waitContainer.image.tag=latest \
  --set serviceMonitor.enabled=false

# Ingress (also applied by bootstrap)
sed "s/k8s_domain/${k8s_domain}/g" mlflow-ingress.yaml | kubectl apply -f - -n mlflow

echo "MLflow installed. URL: https://mlflow.${k8s_domain}"
