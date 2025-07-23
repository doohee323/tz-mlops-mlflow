#!/usr/bin/env bash

source /root/.bashrc
function prop { key="${2}=" file="/root/.k8s/${1}" rslt=$(grep "${3:-}" "$file" -A 10 | grep "$key" | head -n 1 | cut -d '=' -f2 | sed 's/ //g'); [[ -z "$rslt" ]] && key="${2} = " && rslt=$(grep "${3:-}" "$file" -A 10 | grep "$key" | head -n 1 | cut -d '=' -f2 | sed 's/ //g'); rslt=$(echo "$rslt" | tr -d '\n' | tr -d '\r'); echo "$rslt"; }
#bash /vagrant/tz-local/resource/mlflow/install.sh
cd /vagrant/tz-local/resource/mlflow

#set -x
shopt -s expand_aliases
alias k='kubectl --kubeconfig ~/.kube/config'

export k8s_project=$(prop 'project' 'project')
export admin_password=$(prop 'project' 'admin_password')
NS=devops-dev

helm repo add community-charts https://community-charts.github.io/helm-charts
helm repo update

#S3 (Minio) and PostgreSQL DB Configuration on Helm Upgrade Command Example
#helm uninstall mlflow -n ${NS}
#helm upgrade --install mlflow community-charts/mlflow \
#  --namespace ${NS} \
#  --set backendStore.databaseMigration=true \
#  --set backendStore.postgres.enabled=true \
#  --set backendStore.postgres.host=devops-postgres-postgresql.devops-dev.svc.cluster.local \
#  --set backendStore.postgres.port=5432 \
#  --set backendStore.postgres.database=mlflow \
#  --set backendStore.postgres.user=admin \
#  --set backendStore.postgres.password='DevOps!323' \
#  --set artifactRoot.s3.enabled=true \
#  --set artifactRoot.s3.bucket=mlflow \
#  --set artifactRoot.s3.awsAccessKeyId=${k8s_project} \
#  --set artifactRoot.s3.awsSecretAccessKey=${admin_password} \
#  --set extraEnvVars.MLFLOW_S3_ENDPOINT_URL=http://minio.devops.svc.cluster.local:9000 \
#  --set serviceMonitor.enabled=true \
#  --set image.tag=2.12.1

helm install my-release oci://registry-1.docker.io/bitnamicharts/mlflow

helm upgrade --install mlflow oci://registry-1.docker.io/bitnamicharts/mlflow \
  --namespace ${NS} --create-namespace \
  --set backendStore.databaseMigration=true \
  --set backendStore.postgres.enabled=true \
  --set backendStore.postgres.host=devops-postgres-postgresql.devops-dev.svc.cluster.local \
  --set backendStore.postgres.port=5432 \
  --set backendStore.postgres.database=mlflow \
  --set backendStore.postgres.user=admin \
  --set backendStore.postgres.password='DevOps!323' \
  --set artifactRoot.s3.enabled=true \
  --set artifactRoot.s3.bucket=mlflow \
  --set artifactRoot.s3.awsAccessKeyId="${k8s_project}" \
  --set artifactRoot.s3.awsSecretAccessKey="${admin_password}" \
  --set extraEnvVars[0].name=MLFLOW_S3_ENDPOINT_URL \
  --set extraEnvVars[0].value=http://minio.devops.svc.cluster.local:9000 \
  --set serviceMonitor.enabled=true

cp -Rf mlflow-ingress.yaml mlflow-ingress.yaml_bak
sed -ie "s/k8s_project/${k8s_project}/g" mlflow-ingress.yaml_bak
sed -ie "s/k8s_domain/${k8s_domain}/g" mlflow-ingress.yaml_bak
#kubectl delete -f mlflow-ingress.yaml_bak -n mlflow
kubectl apply -f mlflow-ingress.yaml_bak -n ${NS}


rm -Rf .venv
#conda create -p .venv python==3.13
#conda activate .venv
#conda deactivate

pyenv install 3.10.13
pyenv local 3.10.13
python -m venv env
source env/bin/activate

cd /vagrant/tz-local/resource/mlflow
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
pip3 install papermill

pip install ipykernel
python -m ipykernel install --user --name=python3 --display-name "Python 3 (venv)"
jupyter kernelspec list

export MLFLOW_TRACKING_URI="https://mlflow.new-nation.church"
export MLFLOW_TRACKING_USERNAME="user"
export MLFLOW_TRACKING_PASSWORD="xxx"

papermill get-started.ipynb output.ipynb

