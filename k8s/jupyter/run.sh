#!/usr/bin/env bash
# JupyterHub (namespace: jupyterhub)

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "${REPO_ROOT}/scripts/load-config.sh"

cd "${REPO_ROOT}/k8s/jupyter"
shopt -s expand_aliases
alias k='kubectl --kubeconfig ~/.kube/config'

k8s_project=$(prop 'project' 'project')
k8s_domain=$(prop 'project' 'domain')
basic_password=$(prop 'project' 'basic_password')
NS=jupyterhub

kubectl create namespace ${NS} --dry-run=client -o yaml | kubectl apply -f -

helm repo add jupyterhub https://hub.jupyter.org/helm-chart/ 2>/dev/null || true
helm repo update

APP_VERSION="1.2.0"
helm show values jupyterhub/jupyterhub --version ${APP_VERSION} > values-current.yaml 2>/dev/null || true
helm upgrade --install jupyterhub jupyterhub/jupyterhub -f values.yaml -n ${NS} --version ${APP_VERSION}

echo "JupyterHub installed. Default: jovyan / jupyter"
