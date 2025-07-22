#!/usr/bin/env bash

# install airflow

source /root/.bashrc
#bash /vagrant/tz-local/resource/airflow/run.sh
cd /vagrant/tz-local/resource/airflow

#set -x
shopt -s expand_aliases
alias k='kubectl --kubeconfig ~/.kube/config'

k8s_project=$(prop 'project' 'project')
k8s_domain=$(prop 'project' 'domain')
admin_password=$(prop 'project' 'admin_password')
github_id=$(prop 'project' 'github_id')
github_token=$(prop 'project' 'github_token')
NS=airflow

#helm uninstall airflow -n ${NS}
#kubectl delete pod airflow-redis-0 --grace-period=0 --force -n airflow
#kubectl delete pod airflow-worker-0 --grace-period=0 --force -n airflow
#kubectl delete ns ${NS}
kubectl create ns ${NS}

kubectl delete secret git-credentials
kubectl create secret generic git-credentials \
  --from-literal=GIT_SYNC_USERNAME=${github_id} \
  --from-literal=GIT_SYNC_PASSWORD=${github_token} \
  --from-literal=GITSYNC_USERNAME=${github_id} \
  --from-literal=GITSYNC_PASSWORD=${github_token} \
  -n airflow

kubectl create secret generic airflow-webserver-secret \
  --from-literal=webserver-secret-key='topzone!323' \
  -n airflow

helm repo add apache-airflow https://airflow.apache.org
#helm show values apache-airflow/airflow > values.yaml
#kubectl cp values.yaml devops-dev/bastion:/vagrant/tz-local/resource/airflow
#--reuse-values
helm upgrade --install --reuse-values airflow apache-airflow/airflow -n ${NS} -f values.yaml

#echo Fernet Key: $(kubectl get secret --namespace airflow airflow-fernet-key -o jsonpath="{.data.fernet-key}" | base64 --decode)

cp -Rf airflow-ingress.yaml airflow-ingress.yaml_bak
sed -ie "s/k8s_project/${k8s_project}/g" airflow-ingress.yaml_bak
sed -ie "s/k8s_domain/${k8s_domain}/g" airflow-ingress.yaml_bak
#kubectl delete -f airflow-ingress.yaml_bak -n airflow
kubectl apply -f airflow-ingress.yaml_bak -n airflow

exit 0

admin / admin

https://airflow-admin.new-nation.church/connections
my_postgres_connection	postgres		devops-postgres-postgresql.devops-dev.svc.cluster.local	5432  admin/passwd drillquiz
nasa_api	http		api.nasa.gov	443 https   passwd




