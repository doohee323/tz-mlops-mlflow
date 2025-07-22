# tz-mlops-mlflow

[ML 실험 코드 (Jupyter)]
     ↓ (nbconvert)
[Python 코드 변환 및 if __name__ 추가]
     ↓
[Docker Image 빌드 및 Push]
     ↓
[Airflow DAG 작성 및 GitOps 배포]
     ↓
[Airflow UI에서 Trigger 및 모니터링]

# 작업 환경 만들기
cd /Users/dhong/workspaces/tz-mlops-mlflow
rm -Rf venv
pyenv install 3.10.13
pyenv local 3.10.13
python -m venv env
source env/bin/activate
python3 -V  # Python 3.10.x

pip3 install -r requirements.txt
pip3 install papermill

# To force python3 version
# pip install ipykernel
# python -m ipykernel install --user --name=python3 --display-name "Python 3 (venv)"
# jupyter kernelspec list

#0. research with jupiter notebook
# get-started.ipynb

#1. Python 코드 준비
#pip install nbconvert
jupyter-nbconvert --to script notebooks/get-started.ipynb
mv notebooks/get-started.py docker/main.py
# add if __name__ == "__main__":

#2. Dockerfile 작성
#3. Docker Image 빌드 및 Push
cd docker
docker build -t doohee323/ml_job_dag:latest .
docker push doohee323/ml_job_dag:latest

#4. Airflow DAG에서 만들기 (KubernetesPodOperator)
# dags/ml_job_dag.py

#5. Airflow gitsync 로 배포
#git clone https://github.com/doohee323/tz-airflow-dags.git
cp -Rf ml_job_dag.py tz-airflow-dags/airflow-dags/ml_job_dag.py
cd tz-airflow-dags
git add airflow-dags/ml_job_dag.py
git commit -m 'ml_job_dag'
git push

#6. 확인
#URL: https://airflow-admin.new-nation.church/

#7 Trigger
#실행: doohee323/ml_job_dag:latest

