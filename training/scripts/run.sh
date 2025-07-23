#!/usr/bin/env bash

cd training/scripts

export MLFLOW_TRACKING_URI="https://mlflow.new-nation.church"
export MLFLOW_TRACKING_USERNAME="user"
export MLFLOW_TRACKING_PASSWORD="xxx"

#jupyter-notebook training/notebooks/get-started.ipynb

python get-started.py

python gettingstarted.py

python train_model.py

mlflow experiments restore --experiment-id 8
#mlflow experiments delete --experiment-id 8

