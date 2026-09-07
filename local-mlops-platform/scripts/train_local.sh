#!/usr/bin/env bash
# Train the model locally against a running (or absent) MLflow server.
set -euo pipefail

cd "$(dirname "$0")/.."

# Point at the local MLflow server unless the caller overrides it.
export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-http://127.0.0.1:5000}"
export MLFLOW_EXPERIMENT_NAME="${MLFLOW_EXPERIMENT_NAME:-nyc-taxi-fare}"

PY="${PYTHON:-python3}"
if [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
fi

echo "Training with MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI"
exec "$PY" -m mlops_demo.train "$@"
