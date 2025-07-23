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
├── training/                    # 모델 개발/훈련
│   ├── scripts/                 # 훈련 스크립트
│   │   ├── train_model.py       # 메인 훈련 스크립트
│   │   ├── gettingstarted.py    # 기존 훈련 스크립트
│   │   └── get-started.py       # 기존 훈련 스크립트
│   ├── notebooks/               # 실험용 노트북
│   │   └── get-started.ipynb    # MLflow 실험용 Jupyter 노트북
│   └── docker/                  # 훈련용 Docker
│       └── Dockerfile           # 훈련 환경
├── serving/                     # 모델 서빙
│   ├── api/                     # API 서버
│   │   ├── app.py               # Flask API 서버
│   │   └── test_api.py          # API 테스트 클라이언트
│   └── docker/                  # 서빙용 Docker
│       └── Dockerfile           # 서빙 환경
├── shared/                      # 공통 유틸리티
│   └── utils/                   # 공통 함수
│       └── mlflow_utils.py      # MLflow 유틸리티
├── dags/                        # Airflow DAG
│   ├── mlflow_job_dag.py        # 기존 훈련 전용 DAG
│   ├── mlflow_complete_pipeline_dag.py  # 전체 파이프라인 DAG
│   └── mlflow_serving_dag.py    # 서빙 전용 DAG
├── k8s/                         # k8s airflow, mlflow 설치 참조용
├── requirements.txt             # Python 패키지 의존성
└── README.md                    # 프로젝트 문서
```

## 🚀 주요 기능

- **외부 MLflow 서버 연동**: 기존 MLflow 서버에 실험 결과 전송
- **외부 Airflow 서버 연동**: 기존 Airflow 서버에서 DAG 실행
- **Docker Containerization**: 재현 가능한 ML 환경 구성
- **Flask API 서비스**: MLflow 모델을 REST API로 서비스
- **Jupyter Notebook**: 실험 및 개발 환경
- **모듈화된 구조**: 훈련과 서빙 분리
- **완전한 MLOps 파이프라인**: 훈련 → 등록 → 배포 → 서빙

## 🛠️ 기술 스택

- **ML Framework**: MLflow, scikit-learn, pandas, numpy
- **Orchestration**: Apache Airflow (외부 서버)
- **Containerization**: Docker
- **Web Framework**: Flask
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

jupyter-notebook training/notebooks/get-started.ipynb
```

### 1. 모델 훈련

```bash
# 훈련 스크립트 실행
cd training/scripts
python train_model.py

# 또는 Docker로 훈련
cd training
docker build -f docker/Dockerfile -t mlflow-training:latest .
docker run mlflow-training:latest
```

### 2. ML 코드 Docker 이미지 빌드 및 Push

```bash
# 훈련용 이미지
cd training
docker build -f docker/Dockerfile -t doohee323/ml_training:latest .
docker push doohee323/ml_training:latest

# 서빙용 이미지
cd serving
docker build -f docker/Dockerfile -t doohee323/ml_serving:latest .
docker push doohee323/ml_serving:latest
```

### 3. Airflow DAG 선택 및 배포

#### 옵션 A: 훈련 전용 DAG (기존)
```bash
# 훈련만 실행하는 DAG
cp dags/mlflow_job_dag.py tz-airflow-dags/airflow-dags/
```

#### 옵션 B: 전체 파이프라인 DAG (권장)
```bash
# 훈련 → 등록 → 배포 → 서빙 전체 파이프라인
cp dags/mlflow_complete_pipeline_dag.py tz-airflow-dags/airflow-dags/
```

#### 옵션 C: 서빙 전용 DAG
```bash
# 이미 훈련된 모델을 서빙하는 DAG
cp dags/mlflow_serving_dag.py tz-airflow-dags/airflow-dags/
```

### 4. GitOps를 통한 Airflow DAG 배포

```bash
# Airflow DAG 저장소 클론
git clone https://github.com/doohee323/tz-airflow-dags.git

# DAG 파일 복사 (원하는 옵션 선택)
cp dags/mlflow_complete_pipeline_dag.py tz-airflow-dags/airflow-dags/

# GitOps 배포
cd tz-airflow-dags
git add airflow-dags/mlflow_complete_pipeline_dag.py
git commit -m 'Add complete MLflow pipeline DAG'
git push
```

### 5. Airflow UI에서 확인 및 실행

- **Airflow UI**: https://airflow-admin.new-nation.church/
- **DAG 이름**: 
  - `mlflow_job_dag` (훈련 전용)
  - `mlflow_complete_pipeline` (전체 파이프라인)
  - `mlflow_serving` (서빙 전용)

## 🔄 MLflow 모델 사용 방법
#### 1. **전체 파이프라인 (mlflow_complete_pipeline_dag.py)**
```
[모델 훈련] → [MLflow 등록] → [모델 배포] → [API 서빙] → [테스트] → [모니터링]
```

#### 2. **서빙 전용 (mlflow_serving_dag.py)**
```
[기존 모델 로드] → [API 서빙] → [테스트] → [성능 측정]
```

### **Airflow DAG의 역할**

| DAG | 역할 | 설명 |
|-----|------|------|
| `mlflow_job_dag` | 훈련만 | 모델 훈련 후 MLflow에 등록 |
| `mlflow_complete_pipeline` | 전체 파이프라인 | 훈련 → 등록 → 배포 → 서빙 → 테스트 |
| `mlflow_serving_dag` | 서빙만 | 기존 모델을 API로 서빙 |

### **실제 사용 예시**

#### 1. **자동화된 모델 배포**
```python
# Airflow DAG에서 실행
deploy_model = DockerOperator(
    task_id='deploy_model',
    image='doohee323/ml_serving:latest',
    environment={
        'MODEL_NAME': 'Best Randomforest Model',
        'MODEL_VERSION': 'latest',
    }
)
```

#### 2. **모델 성능 테스트**
```python
# Airflow DAG에서 자동 테스트
def test_model_performance(**context):
    response = requests.post(
        'http://localhost:8080/predict',
        json={"features": [5.1, 3.5, 1.4, 0.2]}
    )
    return response.status_code == 200
```

#### 3. **모델 모니터링**
```python
# Airflow DAG에서 모니터링 설정
def setup_monitoring(**context):
    monitoring_config = {
        "metrics_endpoint": "http://localhost:8080/health",
        "prediction_endpoint": "http://localhost:8080/predict",
        "alert_threshold": 0.95
    }
    return True
```

## 🚀 Flask API 서비스

### API 서버 실행

```bash
# 로컬에서 실행
cd serving/api
python app.py

# 또는 Docker로 실행
cd serving
docker build -f docker/Dockerfile -t mlflow-api:latest .
docker run -p 8080:8080 mlflow-api:latest
```

### API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | API 문서 |
| `/health` | GET | 헬스 체크 |
| `/model/info` | GET | 모델 정보 |
| `/example` | GET | 예제 데이터 |
| `/predict` | POST | 단일 예측 |
| `/predict/batch` | POST | 배치 예측 |

### API 사용 예시

#### 단일 예측
```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

#### 배치 예측
```bash
curl -X POST http://localhost:8080/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"features": [[5.1, 3.5, 1.4, 0.2], [6.3, 3.3, 4.7, 1.6]]}'
```

### API 테스트

```bash
# API 테스트 실행
cd serving/api
python test_api.py
```

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

### API 모니터링
- 헬스 체크 엔드포인트
- 예측 요청 로그
- 모델 로딩 상태 확인

## 🏗️ 프로젝트 구조의 장점

### 1. **관심사 분리 (Separation of Concerns)**
- **훈련**: 모델 개발, 실험, 하이퍼파라미터 튜닝
- **서빙**: 모델 배포, API 서비스, 예측
- **공통**: 재사용 가능한 유틸리티

### 2. **독립적 배포**
- 훈련과 서빙을 독립적으로 배포 가능
- 각각 다른 Docker 이미지 사용
- 서로 다른 리소스 요구사항

### 3. **확장성**
- 새로운 모델 추가 시 훈련만 수정
- API 서비스는 모델 변경 없이 동작
- 공통 유틸리티 재사용

### 4. **유지보수성**
- 코드 중복 최소화
- 명확한 책임 분리
- 테스트 용이성

### 5. **완전한 MLOps 파이프라인**
- **훈련**: 모델 개발 및 실험
- **등록**: MLflow에 모델 저장
- **배포**: Docker 컨테이너로 배포
- **서빙**: REST API로 예측 서비스
- **모니터링**: 성능 및 상태 추적
