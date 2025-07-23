# install jupyter

source /root/.bashrc
#bash /vagrant/sl-local/resource/jupyter/run.sh
cd /vagrant/sl-local/resource/jupyter

#set -x
shopt -s expand_aliases
alias k='kubectl --kubeconfig ~/.kube/config'

k8s_project=$(prop 'project' 'project')
k8s_domain=$(prop 'project' 'domain')
admin_password=$(prop 'project' 'admin_password')
basic_password=$(prop 'project' 'basic_password')
NS=jupyterhub

helm repo add jupyterhub https://hub.jupyter.org/helm-chart/
helm repo update
helm uninstall jupyterhub -n jupyterhub
kubectl delete ns jupyterhub
kubectl create ns jupyterhub

APP_VERSION="1.2.0"
#helm show values jupyterhub/jupyterhub > values.yaml
helm show values jupyterhub/jupyterhub --version ${APP_VERSION} > values.yaml
cp -Rf values.yaml values.yaml_bak
helm upgrade --debug --install --reuse-values jupyterhub jupyterhub/jupyterhub -f values.yaml_bak -n jupyterhub \
  --version ${APP_VERSION}

jovyan / jupyter
