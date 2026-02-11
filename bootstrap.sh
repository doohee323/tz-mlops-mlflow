#!/usr/bin/env bash
# tz-mlops-mlflow infrastructure bootstrap
# Prerequisites: K8s cluster, kubectl, helm, KUBECONFIG
# Config: /root/.k8s/project (see scripts/load-config.sh, prop function)
# Order: Ingress NGINX (skip if exists) → PostgreSQL → MinIO → MLflow → Airflow → Ingress resources → Jupyter (optional)

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export REPO_ROOT
export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/config}"

# Load prop function
source "${REPO_ROOT}/scripts/load-config.sh"

echo "=============================================="
echo " tz-mlops-mlflow infrastructure bootstrap"
echo " REPO_ROOT=${REPO_ROOT}"
echo " KUBECONFIG=${KUBECONFIG}"
echo "=============================================="

# Phase 0: K8s access check
phase0() {
  echo ""
  echo "[Phase 0] K8s access check"
  if ! kubectl get nodes &>/dev/null; then
    echo "Error: kubectl get nodes failed. Check KUBECONFIG or cluster."
    exit 1
  fi
  kubectl get nodes
  echo ""
}

# 1. Ingress NGINX controller: skip if already installed
install_ingress_controller() {
  echo ""
  echo "[1/7] Ingress NGINX controller"
  if helm list -n default 2>/dev/null | grep -q ingress-nginx; then
    echo "  → Already installed, skipping"
    return 0
  fi
  echo "  → Installing from refer/tz-chatbot..."
  export TZ_REPO_ROOT="${REPO_ROOT}/refer/tz-chatbot"
  (cd "${REPO_ROOT}/refer/tz-chatbot/ingress-nginx" && bash install.sh)
}

# 1.5 Ensure tz-registrykey exists (for MLflow image pull)
ensure_registry_secret() {
  local registry username password
  registry=$(prop 'project' 'docker_registry')
  username=$(prop 'project' 'docker_username')
  password=$(prop 'project' 'docker_password')

  if [[ -z "${username}" ]] || [[ -z "${password}" ]]; then
    echo "  → docker_username/docker_password not set in .k8s/project. Create tz-registrykey manually."
    return 0
  fi
  [[ -z "${registry}" ]] && registry="https://index.docker.io/v1/"

  for ns in mlflow airflow jupyterhub; do
    kubectl create namespace "${ns}" --dry-run=client -o yaml | kubectl apply -f - 2>/dev/null || true
    kubectl create secret docker-registry tz-registrykey \
      --docker-server="${registry}" \
      --docker-username="${username}" \
      --docker-password="${password}" \
      -n "${ns}" --dry-run=client -o yaml | kubectl apply -f - 2>/dev/null || true
  done
  echo "  → tz-registrykey ensured (${username}@${registry})"
}

# 2. PostgreSQL: skip if exists
install_postgresql() {
  echo ""
  echo "[2/7] PostgreSQL (namespace: devops-dev)"
  if helm list -n devops-dev 2>/dev/null | grep -q devops-postgres; then
    echo "  → Already installed, skipping"
    return 0
  fi
  (cd "${REPO_ROOT}/k8s/postgresql" && bash install.sh)
}

# Create mlflow bucket in MinIO (for MLflow artifact storage). Safe to call anytime.
ensure_mlflow_bucket() {
  local minio_access_key minio_secret_key NS=devops
  minio_access_key=$(prop 'project' 'minio_access_key')
  minio_secret_key=$(prop 'project' 'minio_secret_key')
  if [[ -z "${minio_access_key}" || -z "${minio_secret_key}" ]]; then
    echo "  → Set minio_access_key and minio_secret_key in .k8s/project to auto-create mlflow bucket"
    return 0
  fi
  echo "  → Ensuring mlflow bucket exists..."
  local MC_HOST="http://${minio_access_key}:${minio_secret_key}@minio.${NS}.svc.cluster.local:9000"
  kubectl run mc-bucket-init --rm -i --restart=Never -n ${NS} \
    --image=minio/mc:latest \
    --env="MC_HOST_myminio=${MC_HOST}" \
    -- mc mb myminio/mlflow --ignore-existing 2>/dev/null && echo "  → mlflow bucket ready" || true
}

# 3. MinIO: skip if exists
install_minio() {
  echo ""
  echo "[3/7] MinIO (namespace: devops)"
  if helm list -n devops 2>/dev/null | grep -q minio; then
    echo "  → Already installed, skipping"
    ensure_mlflow_bucket
    return 0
  fi
  (cd "${REPO_ROOT}/k8s/minio" && bash install.sh)
}

# 4. MLflow
install_mlflow() {
  echo ""
  echo "[4/7] MLflow (namespace: mlflow)"
  (cd "${REPO_ROOT}/k8s/mlflow" && bash install.sh)
}

# 5. Airflow
install_airflow() {
  echo ""
  echo "[5/7] Airflow (namespace: airflow)"
  (cd "${REPO_ROOT}/k8s/airflow" && bash install.sh)
}

# 6. Apply Ingress resources (MLflow, Airflow, MinIO routing)
apply_ingress_resources() {
  echo ""
  echo "[6/7] Apply Ingress resources (MLflow, Airflow, MinIO, Jupyter)"
  k8s_project=$(prop 'project' 'project')
  k8s_domain=$(prop 'project' 'domain')

  # MLflow Ingress
  if [[ -f "${REPO_ROOT}/k8s/mlflow/mlflow-ingress.yaml" ]]; then
    sed "s/k8s_domain/${k8s_domain}/g" "${REPO_ROOT}/k8s/mlflow/mlflow-ingress.yaml" | kubectl apply -f - -n mlflow
    echo "  → MLflow Ingress applied (mlflow.${k8s_domain})"
  fi

  # Airflow Ingress
  if [[ -f "${REPO_ROOT}/k8s/airflow/airflow-ingress.yaml" ]]; then
    sed "s/k8s_domain/${k8s_domain}/g" "${REPO_ROOT}/k8s/airflow/airflow-ingress.yaml" | kubectl apply -f - -n airflow
    echo "  → Airflow Ingress applied (airflow-admin.${k8s_domain})"
  fi

  # MinIO Ingress
  if [[ -f "${REPO_ROOT}/k8s/minio/minio-ingress.yaml" ]]; then
    sed -e "s/k8s_project/${k8s_project}/g" -e "s/k8s_domain/${k8s_domain}/g" "${REPO_ROOT}/k8s/minio/minio-ingress.yaml" | kubectl apply -f - -n devops
    echo "  → MinIO Ingress applied"
  fi

  # Jupyter Ingress
  if [[ -f "${REPO_ROOT}/k8s/jupyter/jupyter-ingress.yaml" ]]; then
    sed "s/k8s_domain/${k8s_domain}/g" "${REPO_ROOT}/k8s/jupyter/jupyter-ingress.yaml" | kubectl apply -f - -n jupyterhub
    echo "  → Jupyter Ingress applied (jupyter.${k8s_domain})"
  fi
}

# 7. Jupyter: optional, skip if exists
install_jupyter() {
  echo ""
  echo "[7/7] JupyterHub (namespace: jupyterhub, optional)"
  if helm list -n jupyterhub 2>/dev/null | grep -q jupyterhub; then
    echo "  → Already installed, skipping"
    return 0
  fi
  (cd "${REPO_ROOT}/k8s/jupyter" && bash run.sh)
}

summary() {
  k8s_domain=$(prop 'project' 'domain')
  echo ""
  echo "=============================================="
  echo " Bootstrap complete"
  echo "=============================================="
  echo "  Ingress:     NGINX + cert-manager (skip if existed)"
  echo "  PostgreSQL:  devops-dev NS (devops-postgres-postgresql)"
  echo "  MinIO:       devops NS"
  echo "  MLflow:      mlflow NS      → https://mlflow.${k8s_domain}"
  echo "  Airflow:     airflow NS     → https://airflow-admin.${k8s_domain}"
  echo "  Jupyter:     jupyterhub NS  → https://jupyter.${k8s_domain} (if installed)"
  echo ""
  echo "  Config: /root/.k8s/project"
  echo ""
  echo "  Post-bootstrap: Import Airflow Variables for MLflow DAG"
  echo "    Airflow UI → Admin → Variables → Import Variables"
  echo "    Upload: k8s/airflow/airflow-variables.json"
  echo "=============================================="
}

main() {
  phase0
  install_ingress_controller
  ensure_registry_secret
  install_postgresql
  install_minio
  install_mlflow
  install_airflow
  apply_ingress_resources
  install_jupyter
  summary
}

# --- Uninstall: MLflow, Airflow, Jupyter only (PostgreSQL, MinIO, Ingress controller NOT removed) ---
uninstall_mlops() {
  echo ""
  echo "[1/4] Remove MLflow (namespace: mlflow)"
  if helm list -n mlflow 2>/dev/null | grep -q mlflow; then
    helm uninstall mlflow -n mlflow
    kubectl delete ingress mlflow-ingress -n mlflow --ignore-not-found
    echo "  → MLflow removed"
  else
    echo "  → Not installed, skipping"
  fi

  echo ""
  echo "[2/4] Remove Airflow (namespace: airflow)"
  if helm list -n airflow 2>/dev/null | grep -q airflow; then
    helm uninstall airflow -n airflow
    kubectl delete ingress airflow-webserver-ingress airflow-ingress -n airflow --ignore-not-found
    echo "  → Airflow removed"
  else
    echo "  → Not installed, skipping"
  fi

  echo ""
  echo "[3/4] Remove JupyterHub (namespace: jupyterhub)"
  if helm list -n jupyterhub 2>/dev/null | grep -q jupyterhub; then
    helm uninstall jupyterhub -n jupyterhub
    kubectl delete ingress jupyter-ingress -n jupyterhub --ignore-not-found
    echo "  → JupyterHub removed"
  else
    echo "  → Not installed, skipping"
  fi

  echo ""
  echo "[4/4] Remove orphan namespaces (if empty)"
  for ns in mlflow airflow jupyterhub; do
    if kubectl get ns "$ns" &>/dev/null; then
      # Delete only if namespace has no workloads (optional cleanup)
      kubectl delete ns "$ns" --ignore-not-found --timeout=30s 2>/dev/null || true
    fi
  done
}

uninstall_summary() {
  echo ""
  echo "=============================================="
  echo " Uninstall complete (MLflow, Airflow, Jupyter removed)"
  echo "=============================================="
  echo "  Kept: PostgreSQL, MinIO, Ingress controller"
  echo "  Reinstall: ./bootstrap.sh"
  echo "=============================================="
}

if [[ "${1:-}" == "uninstall" ]]; then
  phase0
  uninstall_mlops
  uninstall_summary
else
  main "$@"
fi
