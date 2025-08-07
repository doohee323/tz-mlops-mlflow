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

export MLFLOW_TRACKING_URI="https://mlflow.drillquiz.com"
export MLFLOW_TRACKING_USERNAME="user"
export MLFLOW_TRACKING_PASSWORD="xxx"

#jupyter-notebook training/notebooks/get-started.ipynb

papermill training/notebooks/get-started.ipynb output.ipynb

