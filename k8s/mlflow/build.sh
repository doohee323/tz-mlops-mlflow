#!/usr/bin/env bash
# Build MLflow image with PostgreSQL support. Push to your registry before install.
set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "${REPO_ROOT}/scripts/load-config.sh" 2>/dev/null || true

github_id=$(prop 'project' 'github_id' 2>/dev/null || echo "tz-mlops")
TAG="${1:-ghcr.io/${github_id}/mlflow-pg:v2.22.2}"

cd "${REPO_ROOT}/k8s/mlflow"
docker build --platform linux/amd64 --no-cache -t "${TAG}" .
echo "Built ${TAG}"
echo "Push: docker push ${TAG}"
echo "Then set in .k8s/project: mlflow_image = ${TAG}"
