#!/usr/bin/env bash
# Ensure local venv matches Docker Python version (from training/serving Dockerfiles).
# Usage: ./scripts/ensure-venv.sh [--create]
#   --create  Recreate env/ with the Docker Python version if mismatch.

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

# Detect Python version from Docker (training/serving use python:3.9-slim)
DOCKER_PY=$(grep -h '^FROM python:' training/docker/Dockerfile serving/docker/Dockerfile 2>/dev/null | head -1 | sed -E 's/.*python:([0-9]+\.[0-9]+).*/\1/')
[[ -z "${DOCKER_PY}" ]] && DOCKER_PY="3.12"

CURRENT_PY=""
if [[ -f env/bin/python ]]; then
  CURRENT_PY=$(env/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)
fi

echo "Docker Python: ${DOCKER_PY}"
echo "Current env:  ${CURRENT_PY:-none}"

if [[ "${CURRENT_PY}" != "${DOCKER_PY}" ]]; then
  if [[ "${1:-}" == "--create" ]]; then
    echo "Recreating env with python${DOCKER_PY}..."
    rm -rf env
    if command -v "python${DOCKER_PY}" &>/dev/null; then
      "python${DOCKER_PY}" -m venv env
      echo "Done. Run: source env/bin/activate && pip install -r requirements.txt"
      echo "  (Airflow DAG dev: use requirements-airflow.txt in separate venv)"
    else
      echo "python${DOCKER_PY} not found. Install it (e.g. pyenv install ${DOCKER_PY}) and run again."
      exit 1
    fi
  else
    echo "Mismatch. Recreate venv: ./scripts/ensure-venv.sh --create"
    exit 1
  fi
else
  echo "OK (env matches Docker)."
fi
