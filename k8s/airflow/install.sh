#!/usr/bin/env bash
# Airflow (namespace: airflow)

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "${REPO_ROOT}/scripts/load-config.sh"

cd "${REPO_ROOT}/k8s/airflow"
shopt -s expand_aliases
alias k='kubectl --kubeconfig ~/.kube/config'

k8s_project=$(prop 'project' 'project')
k8s_domain=$(prop 'project' 'domain')
[[ -z "${k8s_domain}" ]] && k8s_domain="local"
admin_password=$(prop 'project' 'admin_password')
github_id=$(prop 'project' 'github_id')
github_token=$(prop 'project' 'github_token')
webserver_secret=$(prop 'project' 'webserver_secret')
[[ -z "${webserver_secret}" ]] && webserver_secret='topzone!323'
NS=airflow

kubectl create namespace ${NS} --dry-run=client -o yaml | kubectl apply -f -

kubectl delete secret git-credentials -n ${NS} 2>/dev/null || true
kubectl create secret generic git-credentials \
  --from-literal=GIT_SYNC_USERNAME="${github_id}" \
  --from-literal=GIT_SYNC_PASSWORD="${github_token}" \
  --from-literal=GITSYNC_USERNAME="${github_id}" \
  --from-literal=GITSYNC_PASSWORD="${github_token}" \
  -n ${NS}

kubectl delete secret airflow-webserver-secret -n ${NS} 2>/dev/null || true
kubectl create secret generic airflow-webserver-secret \
  --from-literal=webserver-secret-key="${webserver_secret}" \
  -n ${NS}

helm repo add apache-airflow https://airflow.apache.org 2>/dev/null || true
helm repo update

# Use devops PostgreSQL (devops-dev NS) + airflow-redis if present
PG_HOST="devops-postgres-postgresql.devops-dev.svc.cluster.local"
[[ -z "${admin_password}" ]] && admin_password='DevOps!323'
EXTRA_SET=""
echo "  → Using PostgreSQL: ${PG_HOST}"
EXTRA_SET="${EXTRA_SET} --set postgresql.enabled=false"
EXTRA_SET="${EXTRA_SET} --set data.metadataConnection.host=${PG_HOST}"
EXTRA_SET="${EXTRA_SET} --set data.metadataConnection.port=5432"
EXTRA_SET="${EXTRA_SET} --set data.metadataConnection.user=admin"
EXTRA_SET="${EXTRA_SET} --set data.metadataConnection.pass=${admin_password}"
EXTRA_SET="${EXTRA_SET} --set data.metadataConnection.protocol=postgresql"
EXTRA_SET="${EXTRA_SET} --set data.metadataConnection.db=airflow"
EXTRA_SET="${EXTRA_SET} --set data.metadataConnection.sslmode=disable"
# Use Redis in devops NS (e.g. redis-master from bitnami/redis, or redis)
REDIS_NS="devops"
REDIS_HOST="redis-master.${REDIS_NS}.svc.cluster.local"
if ! k get svc redis-master -n ${REDIS_NS} &>/dev/null; then
  REDIS_HOST="redis.${REDIS_NS}.svc.cluster.local"
fi
echo "  → Using Redis: ${REDIS_HOST}"
EXTRA_SET="${EXTRA_SET} --set redis.enabled=false"
REDIS_PASS=$(k get secret redis -n ${REDIS_NS} -o jsonpath='{.data.redis-password}' 2>/dev/null | base64 -d 2>/dev/null || k get secret redis-master -n ${REDIS_NS} -o jsonpath='{.data.redis-password}' 2>/dev/null | base64 -d 2>/dev/null || true)
if [[ -n "${REDIS_PASS}" ]]; then
  EXTRA_SET="${EXTRA_SET} --set data.brokerUrl=redis://:${REDIS_PASS}@${REDIS_HOST}:6379/0"
else
  EXTRA_SET="${EXTRA_SET} --set data.brokerUrl=redis://${REDIS_HOST}:6379/0"
fi

helm upgrade --install --reuse-values airflow apache-airflow/airflow -n ${NS} -f values.yaml ${EXTRA_SET}

# Ingress (also applied by bootstrap)
sed "s/k8s_domain/${k8s_domain}/g" airflow-ingress.yaml | kubectl apply -f - -n ${NS}

echo "Airflow installed. URL: https://airflow-admin.${k8s_domain}"
