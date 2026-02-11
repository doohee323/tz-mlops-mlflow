# run.sh 실행 결과 해설

`./run.sh` 실행 시 출력되는 내용과 각 단계의 의미를 설명합니다.

---

## Step 1: 환경 설정 및 준비

```
[Step 1] Environment Setup and Preparation
  Using: Python 3.12.10 (should match Docker 3.12)
  MLFLOW_TRACKING_URI=https://mlflow.drillquiz.com
```

**해설:**
- `env/` 가상환경을 활성화하고 Python 버전을 확인합니다.
- Docker 이미지(Python 3.12)와 버전이 같아야 학습·빌드가 일관되게 동작합니다.
- `MLFLOW_TRACKING_URI`: MLflow 서버 주소. 실험·모델이 이 서버로 전송됩니다.

---

## Step 2: 모델 개발 (Jupyter Notebook)

```
[Step 2] Model Development (Jupyter Notebook)
  SKIP: Interactive step - run manually: jupyter-notebook training/notebooks/get-started.ipynb
```

**해설:**
- 노트북 실행은 수동 단계라 스크립트에서는 건너뜁니다.
- Enter를 누르면 다음 단계로 진행합니다. 노트북에서 실험과 로깅을 완료한 뒤 진행하면 됩니다.

**데이터 및 테스트:**
- 이 노트북은 **MLflow Tracking 서버 연결 테스트**용입니다.
- 별도의 학습 데이터를 사용하지 않고, 더미 메트릭(`test`, `Dewey` 등)만 로깅하여 서버 통신을 확인합니다.
- 실험 생성 및 `mlflow.log_metric()` 호출이 정상 동작하는지 검증하는 목적입니다.
- 실제 **California Housing** 데이터와 RandomForest 학습은 Step 3의 `train_model.py`에서 수행됩니다.

**관련 파일:**
| 파일 | 역할 |
|------|------|
| `training/notebooks/get-started.ipynb` | MLflow 연결 테스트용 노트북 |
| `shared/utils/mlflow_utils.py` | MLflow URI 설정, 실험 생성 유틸 |

---

## Step 3: 학습 스크립트 실행

```
[Step 3] Training Script Execution
  Running: python training/scripts/train_model.py
  ...
  Fitting 3 folds for each of 24 candidates, totalling 72 fits
  [CV] END max_depth=5, min_samples_leaf=1, ...
  INFO:__main__:Best parameters: {'max_depth': None, 'min_samples_leaf': 1, ...}
  INFO:__main__:Model logged successfully with compression
  INFO:__main__:Mean Squared Error: 0.2606
  INFO:__main__:Root Mean Squared Error: 0.5105
  🏃 View run suave-newt-276 at: https://mlflow.drillquiz.com/...
  INFO:__main__:ML pipeline completed successfully!
```

**해설:**
- **GridSearchCV**: 24개 하이퍼파라미터 조합 × 3-fold CV = 72회 학습으로 최적 파라미터 탐색.
- **Best parameters**: 선택된 최적 파라미터.
- **MSE, RMSE**: 회귀 모델의 평균 제곱 오차, 제곱근 평균 제곱 오차.
- **Model logged successfully**: MLflow에 모델·메트릭·artifact 업로드 완료.
- `Read-only file system` 경고: `/app`이 읽기 전용인 환경(예: 일부 컨테이너)에서 나올 수 있으며, 기본 캐시로 데이터를 불러오면 정상 동작합니다.

**로컬 학습 vs Airflow 학습:**
| 구분 | Step 3 (로컬) | Airflow DAG (K8s, Step 8 이후) |
|------|----------------|--------------------------------|
| 수행자 | 개발자 | 배포·운영 단계에서 실행 |
| 성격 | 배포 전 파이프라인 동작 검증 | 배포 후 실제 학습·모델 등록·서빙 파이프라인 |
| 실행 위치 | 로컬 가상환경(Python 직접 실행) | K8s Pod(ml_training 이미지 실행) |
| 목적 | Docker 빌드 전 스크립트 검증 | 운영 환경에서 학습·모델 배포 수행 |

Step 3은 개발자가 수행하는 로컬 검증이고, Airflow DAG는 배포 후 운영 환경에서 돌아가는 실제 학습 파이프라인입니다. 둘 다 `train_model.py`를 실행하지만, Step 3은 테스트가 아니라 파이프라인 동작 확인용이며, Airflow 실행이 본업(production) 학습입니다.

---

## Step 4: Docker 이미지 빌드

```
[Step 4] Docker Image Build
  [4.1] Building training image...
  [+] Building 2.3s (15/15) FINISHED
  => CACHED [2/9] WORKDIR /app
  ...
  => naming to docker.io/doohee323/ml_training:latest

  [4.2] Building serving image...
  [+] Building 6.1s (13/13) FINISHED
  => naming to docker.io/doohee323/ml_serving:latest

  [4.3] Verifying images...
  doohee323/ml_serving    latest
  doohee323/ml_training   latest
```

**해설:**
- **ml_training**: 학습 코드(`training/scripts/`), 공용 유틸(`shared/`), Python 의존성, California Housing 데이터(빌드 시 `prepare_data.py`로 미리 다운로드)가 포함된 이미지. Airflow DAG에서 학습 태스크에 사용.
- **ml_serving**: Flask API가 포함된 이미지. MLflow에서 모델을 불러와 REST API로 예측 요청을 처리하며, K8s 서빙 서비스에서 사용. **이 파이프라인의 최종 결과물**이며, 학습→MLflow 저장→서빙 배포 흐름의 끝단에서 예측을 제공한다.
- `CACHED`: 이전에 빌드된 레이어를 재사용하여 빌드 시간이 짧아집니다.

---

## Step 5: Docker 이미지 푸시

```
[Step 5] Docker Image Push
  [5.1] Docker login (interactive)...
  Login Succeeded
  [5.2] Pushing images...
  ...
  latest: digest: sha256:b54c8088... size: 856
  latest: digest: sha256:ca7a9122... size: 856
```

**해설:**
- Docker Hub 인증 후 `ml_training`, `ml_serving` 이미지를 푸시합니다.
- K8s·Airflow에서 이 이미지를 pull해 학습·서빙 파이프라인을 실행합니다.
- `digest`: 이미지 고유 식별자로, 특정 버전 참조에 사용됩니다.

---

## Step 6: Airflow 변수 설정

```
[Step 6] Airflow Variable Setup
  SKIP: Manual step in Airflow UI
  URL: https://airflow-admin.drillquiz.com/ -> Admin -> Variables
  Add: MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME
```

**해설:**
- Airflow UI에서 수동으로 설정하는 단계입니다.
- DAG가 `MLFLOW_TRACKING_URI`, `MLFLOW_EXPERIMENT_NAME`를 사용하므로 반드시 추가해야 합니다.
- `k8s/airflow/airflow-variables.json`을 Import Variables로 업로드하면 편리합니다.

---

## Step 7: Airflow DAG 배포

```
[Step 7] Airflow DAG Deployment
  [7.1] tz-airflow-dags exists, skipping clone
  [7.2] Copying DAG file...
  [7.3] Git add/commit/push...
  On branch main
  nothing to commit, working tree clean
  (no changes to commit)
  Everything up-to-date
```

**해설:**
- **7.1**: `tz-airflow-dags`가 이미 있으면 클론을 건너뜁니다.
- **7.2**: `dags/mlflow_training_pipeline_dag.py`를 `tz-airflow-dags/airflow-dags/`로 복사합니다.
- **7.3**: DAG 레포에 커밋·푸시합니다.
- `nothing to commit`: DAG 내용이 이전과 같으면 변경 사항이 없어 커밋되지 않습니다. 정상 동작입니다.

---

## Step 8: Airflow에서 실행

```
[Step 8] Execute in Airflow
  SKIP: Manual step in Airflow UI
  URL: https://airflow-admin.drillquiz.com/
  DAG: mlflow_training_pipeline - click Trigger DAG
```

**해설:**
- Airflow UI에서 `mlflow_training_pipeline` DAG를 수동으로 Trigger합니다.
- Trigger 후 K8s에서 학습·모델 등록·서빙 파이프라인이 실행됩니다.

---

## Step 9: 결과 확인

```
[Step 9] Result Verification
  [9.1] MLflow UI: https://mlflow.drillquiz.com
  [9.2] API health: curl http://localhost:8080/health
  [9.3] API test script:
  ❌ Error: Could not connect to API. Make sure the Flask server is running on http://localhost:8080
```

**해설:**
- **9.1**: MLflow UI에서 실험·모델·메트릭을 확인합니다. 모델 등록은 학습 시 `registered_model_name`으로 자동 처리되므로 수동 등록은 필요 없습니다. UI에서 할 수 있는 선택적 작업: 실험/run 비교, 모델 Stage 변경(Staging→Production), 버전 정리 등.
- **9.2**: 서빙 서비스(ml_serving Flask API) 헬스 체크. `localhost:8080`은 로컬에서 Docker로 ml_serving을 띄웠거나, `kubectl port-forward svc/mlflow-serving 8080:8080 -n airflow`로 K8s 서비스를 포워딩했을 때 사용. 정상이면 `/health`에서 응답을 받는다.
- **9.3**: 서빙 API로 예측 요청을 보내는 테스트 스크립트.
- 서빙은 보통 Airflow DAG가 K8s에서 실행하므로, API가 로컬에 없으면 이 에러는 자연스러운 상황입니다. K8s 서빙 서비스나 Ingress URL로 접근하면 됩니다.

---

## Step 10: 모니터링

```
[Step 10] Monitoring
  Manual: Configure Airflow alerts, model monitoring, drift detection
```

**해설:**
- Airflow 알림, 모델 모니터링, drift 탐지 등 운영 설정은 수동으로 구성하는 단계입니다.

---

## 요약

| 단계 | 자동/수동 | 설명 |
|------|-----------|------|
| 1–3 | 자동 | 환경 설정, 학습, MLflow 로깅 |
| 4–5 | 자동 | Docker 빌드 및 푸시 |
| 6, 8 | 수동 | Airflow 변수 설정, DAG Trigger |
| 7 | 자동(변경 시) | DAG 파일 복사 및 Git 푸시 |
| 9–10 | 수동/선택 | 결과 확인, 모니터링 설정 |
