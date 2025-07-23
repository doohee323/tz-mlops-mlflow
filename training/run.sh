#!/usr/bin/env bash

cd training

export MLFLOW_TRACKING_URI="https://mlflow.new-nation.church"
export MLFLOW_TRACKING_USERNAME="user"
export MLFLOW_TRACKING_PASSWORD="xxx"

# get-started.py
docker build --platform linux/amd64 -f docker/Dockerfile_get-started -t doohee323/ml_job_dag:latest .
docker push doohee323/ml_job_dag:latest

# train_model.py
docker build -f docker/Dockerfile_train_model -t doohee323/ml_training:latest .
docker push doohee323/ml_training:latest

# gettingstarted.py
# -> build model and register to mlflow
docker build -f docker/Dockerfile_gettingstarted -t doohee323/ml_started:latest .
docker push doohee323/ml_started:latest

### macos
#export DOCKER_DEFAULT_PLATFORM=linux/amd64
#docker inspect --format '{{.Architecture}}' <image_name>
docker buildx create --use --name mybuilder
docker buildx build --platform linux/amd64 \
  -f docker/Dockerfile_gettingstarted \
  -t doohee323/ml_started:latest \
  --push .




