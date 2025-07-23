# tz-mlops-mlflow

MLflow와 Airflow를 활용한 Machine Learning Operations (MLOps) 파이프라인 프로젝트입니다.

## 📋 프로젝트 개요

이 프로젝트는 이미 구축된 외부 MLflow 서버와 Airflow 서버를 활용하여 ML 실험을 자동화하고 관리하는 파이프라인입니다.

### 워크플로우

```
[ML 실험 코드 (Jupyter)]
     ↓ (nbconvert)
[Python 코드 변환 및 if __name__ 추가]
     ↓
[Docker Image 빌드 및 Push]            => CI
     ↓
[Airflow DAG 작성 및 GitOps 배포]       => CI
     ↓
[Airflow UI에서 Trigger 및 모니터링]     => CI
```

## 📁 프로젝트 구조

```
tz-mlops-mlflow/
├── dags/
│   └── mlflow_job_dag.py          # Airflow DAG (외부 Airflow 서버용)
├── ml_code/
│   └── get-started.py             # ML 실행 코드 (외부 MLflow 서버 연동)
├── notebooks/
│   └── get-started.ipynb          # MLflow 실험용 Jupyter 노트북
├── requirements.txt               # Python 패키지 의존성
├── docker/
│   └── Dockerfile                 # ML 코드 실행 환경
├── k8s                            # k8s airflow, mlflow 설치 참조용
└── README.md                      # 프로젝트 문서
```

## 🚀 주요 기능

- **외부 MLflow 서버 연동**: 기존 MLflow 서버에 실험 결과 전송
- **외부 Airflow 서버 연동**: 기존 Airflow 서버에서 DAG 실행
- **Docker Containerization**: 재현 가능한 ML 환경 구성
- **Jupyter Notebook**: 실험 및 개발 환경

## 🛠️ 기술 스택

- **ML Framework**: MLflow, scikit-learn, pandas, numpy
- **Orchestration**: Apache Airflow (외부 서버)
- **Containerization**: Docker
- **Language**: Python 3.10+

## 🔧 환경 설정

### 1. 작업 환경 만들기

```bash
cd tz-mlops-mlflow
rm -Rf venv
pyenv install 3.10.13
pyenv local 3.10.13
python -m venv env
source env/bin/activate
python3 -V  # Python 3.10.x

pip3 install -r requirements.txt
pip3 install papermill
```

### 2. Jupyter Kernel 설정 (선택사항)

```bash
# Python3 버전 강제 설정
pip install ipykernel
python -m ipykernel install --user --name=python3 --display-name "Python 3 (venv)"
jupyter kernelspec list
```

### 3. 환경 변수 설정

```bash
# 외부 MLflow 서버 설정
export MLFLOW_TRACKING_URI=https://mlflow.new-nation.church
export MLFLOW_EXPERIMENT_NAME=production_experiment

# 외부 Airflow 서버 설정
export AIRFLOW_API_URL=https://airflow-admin.new-nation.church
```

## 🏃‍♂️ 사용법

### 0. Jupyter 노트북으로 실험

```bash
# 실험용 노트북 실행
export MLFLOW_TRACKING_URI=https://mlflow.new-nation.church
export MLFLOW_EXPERIMENT_NAME=production_experiment
export MLFLOW_TRACKING_USERNAME=user
export MLFLOW_TRACKING_PASSWORD=xxxx

jupyter-notebook notebooks/get-started.ipynb
```

### 1. Python 코드 준비

```bash
# 노트북을 Python 스크립트로 변환
jupyter-nbconvert --to script notebooks/get-started.ipynb
mv notebooks/get-started.py docker/get-started.py
# get-started.py에 if __name__ == "__main__": 추가 필요

# ML 코드 테스트
pip3 install mlflow
python ml_code/get-started.py
python ml_code/gettingstarted.py

```

### 2. ML 코드 Docker 이미지 빌드 및 Push

```bash
cd docker
docker build -t doohee323/ml_job_dag:latest .
docker push doohee323/ml_job_dag:latest
```

### 3. Airflow DAG 작성

`dags/ml_job_dag.py` 파일을 수정하여 외부 Airflow 서버에 맞게 설정:

### 4. GitOps를 통한 Airflow DAG 배포

```bash
# Airflow DAG 저장소 클론
git clone https://github.com/doohee323/tz-airflow-dags.git

# DAG 파일 복사
cp -Rf dags/ml_job_dag.py tz-airflow-dags/airflow-dags/ml_job_dag.py

# GitOps 배포
cd tz-airflow-dags
git add airflow-dags/ml_job_dag.py
git commit -m 'ml_job_dag'
git push
```

### 5. Airflow UI에서 확인 및 실행

- **Airflow UI**: https://airflow-admin.new-nation.church/
- **DAG 이름**: `ml_job_dag`
- **Docker 이미지**: `doohee323/ml_job_dag:latest`


## 🔍 외부 서버 접속 정보

### MLflow 서버
- **URL**: https://mlflow.new-nation.church
- **기능**: 실험 추적, 모델 관리, 아티팩트 저장

### Airflow 서버
- **URL**: https://airflow-admin.new-nation.church/
- **기능**: 워크플로우 오케스트레이션, DAG 실행 모니터링

## 📊 모니터링

### MLflow 모니터링
- 실험 파라미터 및 메트릭 추적
- 모델 성능 비교
- 아티팩트 버전 관리

### Airflow 모니터링
- DAG 실행 상태 확인
- 태스크 성공/실패 로그
- 워크플로우 성능 메트릭
