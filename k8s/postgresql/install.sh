#!/usr/bin/env bash
# PostgreSQL for MLflow (namespace: devops-dev)
# Service: devops-postgres-postgresql.devops-dev.svc.cluster.local

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "${REPO_ROOT}/scripts/load-config.sh"

cd "${REPO_ROOT}/k8s/postgresql"
shopt -s expand_aliases
alias k='kubectl --kubeconfig ~/.kube/config'

POSTGRES_PASSWORD=$(prop 'project' 'admin_password')
[[ -z "${POSTGRES_PASSWORD}" ]] && POSTGRES_PASSWORD='DevOps!323'
NS=devops-dev

kubectl create namespace ${NS} --dry-run=client -o yaml | kubectl apply -f -

helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
helm repo update

helm upgrade --install devops-postgres bitnami/postgresql \
  --namespace ${NS} --create-namespace \
  --set auth.username=admin \
  --set auth.password="${POSTGRES_PASSWORD}" \
  --set auth.database=mlflow \
  --set primary.persistence.size=5Gi

echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n ${NS} --timeout=120s 2>/dev/null || true

echo "PostgreSQL installed. Service: devops-postgres-postgresql.${NS}.svc.cluster.local:5432"
