#!/bin/bash
# run.sh - MLOps pipeline execution script
# Follows README Scenario 1: New Model Development
# Stops on first error (set -e)
#
# Usage: ./run.sh
#   NON_INTERACTIVE=1 ./run.sh   # Skip read prompts (for CI)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "MLOps Pipeline - run.sh"
echo "=========================================="

# ---------------------------------------------------------------------------
# Step 1: Environment Setup and Preparation
# ---------------------------------------------------------------------------
echo ""
echo "[Step 1] Environment Setup and Preparation"

if [ ! -d "env/bin" ]; then
    echo "ERROR: env/ not found. Run: ./scripts/ensure-venv.sh --create && source env/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate venv and verify Python version
source env/bin/activate
PYTHON_VER=$(python --version 2>&1)
echo "  Using: $PYTHON_VER (should match Docker 3.12)"

# Optional: set MLflow env vars
export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-https://mlflow.drillquiz.com}"
export MLFLOW_EXPERIMENT_NAME="${MLFLOW_EXPERIMENT_NAME:-production_experiment}"
echo "  MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI"

# ---------------------------------------------------------------------------
# Step 2: Model Development (Jupyter Notebook)
# ---------------------------------------------------------------------------
echo ""
echo "[Step 2] Model Development (Jupyter Notebook)"
echo "  SKIP: Interactive step - run manually: jupyter-notebook training/notebooks/get-started.ipynb"
echo "  Perform: data loading, training, MLflow logging, model selection in notebook"
[ -z "${NON_INTERACTIVE}" ] && read -p "  Press Enter after completing notebook, or Ctrl+C to exit..." || echo "  (NON_INTERACTIVE: skipping)"

# ---------------------------------------------------------------------------
# Step 3: Training Script Development
# ---------------------------------------------------------------------------
echo ""
echo "[Step 3] Training Script Execution"
echo "  Running: python training/scripts/train_model.py"
echo "  ⏳ This may take several minutes (hyperparameter tuning, model training)..."
python training/scripts/train_model.py
echo "  Training completed successfully"

# ---------------------------------------------------------------------------
# Step 4: Docker Image Build
# ---------------------------------------------------------------------------
echo ""
echo "[Step 4] Docker Image Build"

echo "  [4.1] Building training image..."
echo "  ⏳ This may take 1–2 minutes..."
bash ./training/ml_training.sh

echo "  [4.2] Building serving image..."
echo "  ⏳ This may take 1–2 minutes..."
docker rmi doohee323/ml_serving:latest 2>/dev/null || true
docker build -f serving/docker/Dockerfile -t doohee323/ml_serving:latest .

echo "  [4.3] Verifying images..."
docker images | grep doohee323 || (echo "ERROR: No doohee323 images found" && exit 1)

# ---------------------------------------------------------------------------
# Step 5: Docker Image Push
# ---------------------------------------------------------------------------
echo ""
echo "[Step 5] Docker Image Push"

echo "  [5.1] Docker login (interactive)..."
docker login

echo "  [5.2] Pushing images..."
echo "  ⏳ Push may take a few minutes depending on network speed..."
docker push doohee323/ml_training:latest
docker push doohee323/ml_serving:latest

echo "  [5.3] Verify on Docker Hub (optional):"
echo "    curl https://hub.docker.com/v2/repositories/doohee323/ml_training/tags/"
echo "    curl https://hub.docker.com/v2/repositories/doohee323/ml_serving/tags/"

# ---------------------------------------------------------------------------
# Step 6: Airflow Variable Setup
# ---------------------------------------------------------------------------
echo ""
echo "[Step 6] Airflow Variable Setup"
echo "  SKIP: Manual step in Airflow UI"
echo "  URL: https://airflow-admin.drillquiz.com/ -> Admin -> Variables"
echo "  Add: MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME"
[ -z "${NON_INTERACTIVE}" ] && read -p "  Press Enter after configuring variables, or Ctrl+C to exit..." || echo "  (NON_INTERACTIVE: skipping)"

# ---------------------------------------------------------------------------
# Step 7: Airflow DAG Deployment
# ---------------------------------------------------------------------------
echo ""
echo "[Step 7] Airflow DAG Deployment"

if [ ! -d "tz-airflow-dags" ]; then
    echo "  [7.1] Cloning tz-airflow-dags repo..."
    git clone https://github.com/doohee323/tz-airflow-dags.git
else
    echo "  [7.1] tz-airflow-dags exists, skipping clone"
fi

echo "  [7.2] Copying DAG file..."
cp -f dags/mlflow_training_pipeline_dag.py tz-airflow-dags/airflow-dags/

echo "  [7.3] Git add/commit/push..."
cd tz-airflow-dags
git add airflow-dags/mlflow_training_pipeline_dag.py
git status
if [ -n "${NON_INTERACTIVE}" ]; then
    DO_COMMIT="y"
else
    read -p "  Proceed with commit and push? [y/N] " -n 1 -r
    echo
    DO_COMMIT="$REPLY"
fi
if [[ "$DO_COMMIT" =~ ^[Yy]$ ]]; then
    git commit -m 'Add MLflow training pipeline DAG' || echo "  (no changes to commit)"
    git push
fi
cd "$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# Step 8: Execute in Airflow
# ---------------------------------------------------------------------------
echo ""
echo "[Step 8] Execute in Airflow"
echo "  SKIP: Manual step in Airflow UI"
echo "  URL: https://airflow-admin.drillquiz.com/"
echo "  DAG: mlflow_training_pipeline - click Trigger DAG"
[ -z "${NON_INTERACTIVE}" ] && read -p "  Press Enter after triggering DAG, or Ctrl+C to exit..." || echo "  (NON_INTERACTIVE: skipping)"

# ---------------------------------------------------------------------------
# Step 9: Result Verification
# ---------------------------------------------------------------------------
echo ""
echo "[Step 9] Result Verification"

echo "  [9.1] MLflow UI: https://mlflow.drillquiz.com - check experiment/model"
echo "  [9.2] API health (if serving is running locally):"
echo "    curl http://localhost:8080/health"
echo ""
echo "  [9.3] API test script:"
if [ -f "serving/api/test_api.py" ]; then
    if [ -n "${NON_INTERACTIVE}" ]; then
        RUN_TEST="n"
    else
        read -p "  Run serving/api/test_api.py? [y/N] " -n 1 -r
        echo
        RUN_TEST="$REPLY"
    fi
    if [[ "$RUN_TEST" =~ ^[Yy]$ ]]; then
        python serving/api/test_api.py || echo "  (API may not be running)"
    fi
fi

# ---------------------------------------------------------------------------
# Step 10: Monitoring
# ---------------------------------------------------------------------------
echo ""
echo "[Step 10] Monitoring"
echo "  Manual: Configure Airflow alerts, model monitoring, drift detection"

echo ""
echo "=========================================="
echo "Pipeline run.sh completed successfully!"
echo "=========================================="
