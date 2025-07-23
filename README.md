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
export MLFLOW_TRACKING_USERNAME=user
export MLFLOW_TRACKING_PASSWORD=xxx

# 외부 Airflow 서버 설정
export AIRFLOW_API_URL=https://airflow-admin.new-nation.church
```

## 🏃‍♂️ 사용법

## 📋 **시나리오 1: 새로운 모델 개발 - 상세 작업 순서**

### **1단계: 환경 설정 및 준비**

#### 1.1 현재 환경 확인
```bash
# 현재 디렉토리 및 프로젝트 구조 확인
pwd
ls -la

# Python 버전 확인
python3 --version

# 가상환경 활성화 (있다면)
source env/bin/activate  # 또는 source venv/bin/activate
```

#### 1.2 필요한 패키지 설치
```bash
# requirements.txt 설치
pip install -r requirements.txt

# 추가 패키지 설치
pip install papermill requests
```

#### 1.3 환경 변수 설정
```bash
# MLflow 서버 설정
export MLFLOW_TRACKING_URI=https://mlflow.new-nation.church
export MLFLOW_EXPERIMENT_NAME=production_experiment
export MLFLOW_TRACKING_USERNAME=user
export MLFLOW_TRACKING_PASSWORD=xxx
```

### **2단계: 모델 개발 (Jupyter 노트북)**

#### 2.1 노트북 실행
```bash
# 실험용 노트북 실행
jupyter-notebook training/notebooks/get-started.ipynb
```

#### 2.2 노트북에서 수행할 작업
- 데이터 로드 및 전처리
- 모델 훈련 및 실험
- MLflow로 실험 결과 저장
- 모델 성능 확인 및 하이퍼파라미터 튜닝
- 최적 모델 선택

### **3단계: 훈련 스크립트 개발**

#### 3.1 훈련 스크립트 실행
```bash
cd training/scripts
python train_model.py
```

#### 3.2 훈련 완료 확인사항
훈련이 완료되면 다음과 같은 메시지들이 나타납니다:
```
INFO:__main__:Best Hyperparameters: {...}
INFO:__main__:Mean Squared Error: X.XXXX
INFO:__main__:Root Mean Squared Error: X.XXXX
INFO:__main__:ML pipeline completed successfully!
```

#### 3.3 MLflow 등록 확인
- MLflow UI (https://mlflow.new-nation.church) 접속
- 실험 결과 및 모델 확인
- 모델이 제대로 등록되었는지 확인

### **4단계: Docker 이미지 빌드**

#### 4.1 훈련용 이미지 빌드
```bash
cd training
docker build -f docker/Dockerfile -t doohee323/ml_training:latest .
```

#### 4.2 서빙용 이미지 빌드
```bash
cd serving
docker build -f docker/Dockerfile -t doohee323/ml_serving:latest .
```

#### 4.3 이미지 빌드 확인
```bash
# 빌드된 이미지 확인
docker images | grep doohee323

# 이미지 상세 정보 확인
docker inspect doohee323/ml_training:latest
docker inspect doohee323/ml_serving:latest
```

### **5단계: Docker 이미지 Push**

#### 5.1 Docker Hub 로그인
```bash
docker login
# Username: doohee323
# Password: [Docker Hub 비밀번호]
```

#### 5.2 이미지 Push
```bash
# 훈련용 이미지 Push
docker push doohee323/ml_training:latest

# 서빙용 이미지 Push
docker push doohee323/ml_serving:latest
```

#### 5.3 Push 확인
```bash
# Docker Hub에서 이미지 확인
curl https://hub.docker.com/v2/repositories/doohee323/ml_training/tags/
curl https://hub.docker.com/v2/repositories/doohee323/ml_serving/tags/
```

### **6단계: Airflow Variable 설정**

#### 6.1 Airflow UI 접속
- URL: https://airflow-admin.new-nation.church/
- Admin → Variables 메뉴로 이동

#### 6.2 Variable 설정
다음 Variable들을 추가:

| Key | Value |
|-----|-------|
| `MLFLOW_TRACKING_URI` | `https://mlflow.new-nation.church` |
| `MLFLOW_TRACKING_USERNAME` | `user` |
| `MLFLOW_TRACKING_PASSWORD` | `xxx` |
| `MLFLOW_EXPERIMENT_NAME` | `production_experiment` |

### **7단계: Airflow DAG 배포**

#### 7.1 DAG 파일 선택
```bash
# 전체 파이프라인 DAG 사용 (권장)
cp dags/mlflow_complete_pipeline_dag.py tz-airflow-dags/airflow-dags/

# 또는 훈련 전용 DAG
cp dags/mlflow_job_dag.py tz-airflow-dags/airflow-dags/

# 또는 서빙 전용 DAG
cp dags/mlflow_serving_dag.py tz-airflow-dags/airflow-dags/
```

#### 7.2 GitOps 배포
```bash
# Airflow DAG 저장소 클론 (이미 있다면 생략)
git clone https://github.com/doohee323/tz-airflow-dags.git

# DAG 파일 복사
cp dags/mlflow_complete_pipeline_dag.py tz-airflow-dags/airflow-dags/

# GitOps 배포
cd tz-airflow-dags
git add airflow-dags/mlflow_complete_pipeline_dag.py
git commit -m 'Add complete MLflow pipeline DAG'
git push
```

### **8단계: Airflow에서 실행**

#### 8.1 Airflow UI에서 DAG 확인
- URL: https://airflow-admin.new-nation.church/
- DAG 목록에서 `mlflow_complete_pipeline` 확인
- DAG가 활성화되어 있는지 확인 (On/Off 토글)

#### 8.2 DAG 실행
- DAG 페이지에서 "Trigger DAG" 버튼 클릭
- 실행 파라미터 설정 (필요시)
- "Trigger" 버튼 클릭

#### 8.3 실행 상태 모니터링
- Graph View에서 태스크별 실행 상태 확인
- Log View에서 상세 로그 확인
- 각 태스크의 성공/실패 상태 모니터링

### **9단계: 결과 확인 및 검증**

#### 9.1 MLflow UI에서 결과 확인
- URL: https://mlflow.new-nation.church
- 실험 결과 및 모델 확인
- 모델 버전 및 성능 메트릭 확인

#### 9.2 API 서비스 확인
```bash
# API 서비스가 실행되었는지 확인
curl http://localhost:8080/health

# 예측 테스트
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'

# 배치 예측 테스트
curl -X POST http://localhost:8080/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"features": [[5.1, 3.5, 1.4, 0.2], [6.3, 3.3, 4.7, 1.6]]}'
```

#### 9.3 성능 테스트
```bash
# API 테스트 스크립트 실행
cd serving/api
python test_api.py
```

### **10단계: 모니터링 및 알림 설정**

#### 10.1 Airflow 알림 설정
- 실패 시 이메일 알림 설정
- Slack/Teams 웹훅 설정
- 성공/실패 알림 설정

#### 10.2 모델 모니터링
- 모델 성능 지표 추적
- 데이터 드리프트 감지
- API 응답 시간 모니터링

---

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

## 🚨 문제 해결 가이드

### **자주 발생하는 문제들**

#### 1. **MLflow 연결 오류**
```bash
# 환경 변수 확인
echo $MLFLOW_TRACKING_URI
echo $MLFLOW_TRACKING_USERNAME
echo $MLFLOW_TRACKING_PASSWORD

# 네트워크 연결 확인
curl -I https://mlflow.new-nation.church
```

#### 2. **Docker 빌드 오류**
```bash
# Docker 데몬 상태 확인
docker info

# 이미지 빌드 로그 확인
docker build -f docker/Dockerfile -t test-image . --progress=plain
```

#### 3. **Airflow DAG 실행 오류**
```bash
# DAG 구문 오류 확인
python -c "import dags.mlflow_complete_pipeline_dag"

# Airflow Variable 확인
airflow variables get MLFLOW_TRACKING_URI
```

#### 4. **API 서비스 오류**
```bash
# 포트 사용 확인
lsof -i :8080

# 컨테이너 로그 확인
docker logs mlflow_api_service
```
