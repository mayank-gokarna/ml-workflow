#!/usr/bin/env bash
# Bring up all host-side services for the local MLOps platform:
#   - MLflow tracking server (persistent store, survives reboots)
#   - Port-forwards for the in-cluster UIs (Argo CD, Kubeflow, KServe, Grafana, Prometheus)
#
# Idempotent: skips anything already running. Run after a reboot.
# Usage: ./scripts/up.sh   (or: make up)
set -uo pipefail

cd "$(dirname "$0")/.."
PROJECT_DIR="$(pwd)"

# Resolve a Python/MLflow from the project venv, then a native venv, then PATH.
if   [ -x ".venv/bin/mlflow" ]; then BIN=".venv/bin";
elif [ -x "$HOME/venvs/mlops-demo/bin/mlflow" ]; then BIN="$HOME/venvs/mlops-demo/bin";
else BIN="$(dirname "$(command -v mlflow || true)")"; fi

# Persistent MLflow store on the native filesystem (NOT /tmp, which is wiped on reboot).
MLFLOW_DIR="${MLFLOW_DIR:-$HOME/mlflow-data}"
mkdir -p "$MLFLOW_DIR/artifacts"

log() { printf '  %s\n' "$*"; }

start_bg() { # name  pgrep-pattern  command...
  local name="$1" pat="$2"; shift 2
  if pgrep -f "$pat" >/dev/null 2>&1; then
    log "$name already running"
  else
    nohup "$@" >"/tmp/${name}.log" 2>&1 &
    log "$name started (pid $!)"
  fi
}

echo "Starting local MLOps host services..."

# 1) MLflow tracking server (persistent)
start_bg "mlflow" "mlflow server .*${MLFLOW_DIR}" \
  "$BIN/mlflow" server --host 127.0.0.1 --port 5000 \
  --backend-store-uri "sqlite:///$MLFLOW_DIR/mlflow.db" \
  --default-artifact-root "$MLFLOW_DIR/artifacts"

# 2) Port-forwards for in-cluster UIs (only if the cluster is reachable)
if kubectl get nodes >/dev/null 2>&1; then
  start_bg "pf-argocd"     "port-forward.*argocd-server 8443"             kubectl port-forward -n argocd    svc/argocd-server 8443:443
  start_bg "pf-kubeflow"   "port-forward.*ml-pipeline-ui 8082"            kubectl port-forward -n kubeflow  svc/ml-pipeline-ui 8082:80
  start_bg "pf-kserve"     "port-forward.*taxi-fare-predictor-predictor 8081" kubectl port-forward -n mlops     svc/taxi-fare-predictor-predictor 8081:80
  start_bg "pf-grafana"    "port-forward.*grafana 3000"                   kubectl port-forward -n monitoring svc/grafana 3000:80
  start_bg "pf-prometheus" "port-forward.*prometheus-server 9090"         kubectl port-forward -n monitoring svc/prometheus-server 9090:80
else
  log "WARN: cluster not reachable — skipped port-forwards (is Kind/Docker running?)"
fi

echo "Waiting a few seconds for services to settle..."
sleep 6

# 3) Report status
exec "$PROJECT_DIR/scripts/status.sh"
