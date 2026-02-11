# run.sh Execution Output Guide

This document explains the output of `./run.sh` and the meaning of each step.

---

## Step 1: Environment Setup and Preparation

```
[Step 1] Environment Setup and Preparation
  Using: Python 3.12.10 (should match Docker 3.12)
  MLFLOW_TRACKING_URI=https://mlflow.drillquiz.com
```

**Explanation:**
- Activates the `env/` virtual environment and checks the Python version.
- The version must match the Docker image (Python 3.12) so that training and builds behave consistently.
- `MLFLOW_TRACKING_URI`: MLflow server address. Experiments and models are sent to this server.

---

## Step 2: Model Development (Jupyter Notebook)

```
[Step 2] Model Development (Jupyter Notebook)
  SKIP: Interactive step - run manually: jupyter-notebook training/notebooks/get-started.ipynb
```

**Explanation:**
- Notebook execution is a manual step, so the script skips it.
- Press Enter to proceed to the next step. You can continue after finishing experiments and logging in the notebook.

**Data and testing:**
- This notebook is for **testing MLflow Tracking server connectivity**.
- It does not use separate training data; it only logs dummy metrics (`test`, `Dewey`, etc.) to verify server communication.
- The goal is to verify that experiment creation and `mlflow.log_metric()` calls work correctly.
- Actual **California Housing** data and RandomForest training are done in Step 3 by `train_model.py`.

**Related files:**
| File | Role |
|------|------|
| `training/notebooks/get-started.ipynb` | Notebook for MLflow connectivity test |
| `shared/utils/mlflow_utils.py` | MLflow URI setup, experiment creation utilities |

---

## Step 3: Training Script Execution

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

**Explanation:**
- **GridSearchCV**: 24 hyperparameter combinations × 3-fold CV = 72 fits to search for optimal parameters.
- **Best parameters**: The selected optimal parameters.
- **MSE, RMSE**: Mean Squared Error and Root Mean Squared Error for the regression model.
- **Model logged successfully**: Model, metrics, and artifacts have been uploaded to MLflow.
- `Read-only file system` warning: May appear when `/app` is read-only (e.g. in some containers); using the default cache to load data works normally.

**Local training vs Airflow training:**
| Aspect | Step 3 (Local) | Airflow DAG (K8s, after Step 8) |
|--------|----------------|----------------------------------|
| Performer | Developer | Runs at deployment/operations stage |
| Nature | Pre-deployment pipeline validation | Post-deployment training, model registration, serving pipeline |
| Execution | Local venv (Python directly) | K8s Pod (ml_training image) |
| Purpose | Validate script before Docker build | Production training and model deployment |

Step 3 is local validation by the developer; the Airflow DAG is the actual training pipeline running in the operational environment after deployment. Both run `train_model.py`; Step 3 is for pipeline behavior verification (not a test run), and the Airflow run is the production training.

---

## Step 4: Docker Image Build

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

**Explanation:**
- **ml_training**: Image that includes training code (`training/scripts/`), shared utils (`shared/`), Python dependencies, and California Housing data (downloaded at build time via `prepare_data.py`). Used by the Airflow DAG for the training task.
- **ml_serving**: Image with the Flask API. Loads the model from MLflow and handles prediction requests via REST API; used by the K8s serving service. **Final artifact of this pipeline**; it provides predictions at the end of the flow: training → MLflow storage → serving deployment.
- `CACHED`: Reuses previously built layers so the build finishes faster.

---

## Step 5: Docker Image Push

```
[Step 5] Docker Image Push
  [5.1] Docker login (interactive)...
  Login Succeeded
  [5.2] Pushing images...
  ...
  latest: digest: sha256:b54c8088... size: 856
  latest: digest: sha256:ca7a9122... size: 856
```

**Explanation:**
- After Docker Hub authentication, the `ml_training` and `ml_serving` images are pushed.
- K8s and Airflow pull these images to run the training and serving pipelines.
- `digest`: Unique identifier for the image; used to reference a specific version.

---

## Step 6: Airflow Variable Setup

```
[Step 6] Airflow Variable Setup
  SKIP: Manual step in Airflow UI
  URL: https://airflow-admin.drillquiz.com/ -> Admin -> Variables
  Add: MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME
```

**Explanation:**
- This step is configured manually in the Airflow UI.
- The DAG uses `MLFLOW_TRACKING_URI` and `MLFLOW_EXPERIMENT_NAME`, so these variables must be added.
- You can upload `k8s/airflow/airflow-variables.json` via Import Variables for convenience.

---

## Step 7: Airflow DAG Deployment

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

**Explanation:**
- **7.1**: If `tz-airflow-dags` already exists, the clone is skipped.
- **7.2**: Copies `dags/mlflow_training_pipeline_dag.py` to `tz-airflow-dags/airflow-dags/`.
- **7.3**: Commits and pushes to the DAG repo.
- `nothing to commit`: If the DAG content is unchanged, there is nothing to commit. This is expected.

---

## Step 8: Execute in Airflow

```
[Step 8] Execute in Airflow
  SKIP: Manual step in Airflow UI
  URL: https://airflow-admin.drillquiz.com/
  DAG: mlflow_training_pipeline - click Trigger DAG
```

**Explanation:**
- Manually trigger the `mlflow_training_pipeline` DAG in the Airflow UI.
- After triggering, the training, model registration, and serving pipeline run on K8s.

---

## Step 9: Result Verification

```
[Step 9] Result Verification
  [9.1] MLflow UI: https://mlflow.drillquiz.com
  [9.2] API health: curl http://localhost:8080/health
  [9.3] API test script:
  ❌ Error: Could not connect to API. Make sure the Flask server is running on http://localhost:8080
```

**Explanation:**
- **9.1**: Check experiments, models, and metrics in the MLflow UI. Model registration is done automatically at training time via `registered_model_name`, so manual registration is not required. Optional UI tasks: compare experiments/runs, change model stage (Staging→Production), clean up versions.
- **9.2**: Health check for the serving service (ml_serving Flask API). Use `localhost:8080` when running ml_serving locally via Docker or when forwarding the K8s service with `kubectl port-forward svc/mlflow-serving 8080:8080 -n airflow`. A successful check returns a response at `/health`.
- **9.3**: Test script that sends prediction requests to the serving API.
- Serving usually runs via the Airflow DAG on K8s, so if the API is not running locally, this error is expected. Use the K8s serving service or Ingress URL to access the API.

---

## Step 10: Monitoring

```
[Step 10] Monitoring
  Manual: Configure Airflow alerts, model monitoring, drift detection
```

**Explanation:**
- Airflow alerts, model monitoring, drift detection, and other operational settings are configured manually.

---

## Summary

| Step | Auto/Manual | Description |
|------|-------------|-------------|
| 1–3 | Auto | Environment setup, training, MLflow logging |
| 4–5 | Auto | Docker build and push |
| 6, 8 | Manual | Airflow variable setup, DAG trigger |
| 7 | Auto (when changed) | DAG file copy and Git push |
| 9–10 | Manual/Optional | Result verification, monitoring setup |
