#!/usr/bin/env bash
# Health check for every service in the local MLOps platform.
# Prints an UP/DOWN table and exits non-zero if anything is down.
#
# Usage: ./scripts/status.sh   (or: make status)
set -uo pipefail

green() { printf '\033[32m%s\033[0m' "$1"; }
red()   { printf '\033[31m%s\033[0m' "$1"; }

fail=0
row() { # name  status(UP/DOWN)  detail
  local name="$1" st="$2" detail="${3:-}"
  if [ "$st" = "UP" ]; then printf "  %-22s %s  %s\n" "$name" "$(green UP)" "$detail";
  else printf "  %-22s %s  %s\n" "$name" "$(red DOWN)" "$detail"; fail=1; fi
}

http() { # url  [curl-extra-args...]
  local url="$1"; shift
  curl -s -o /dev/null -w "%{http_code}" --max-time 8 "$@" "$url" 2>/dev/null
}

# A 2xx/3xx/401/403 response means the service is listening (auth/redirects are fine).
up_code() { case "$1" in 2??|3??|401|403) return 0;; *) return 1;; esac; }

pods_ready() { # namespace -> "n/t"
  kubectl get pods -n "$1" --no-headers 2>/dev/null \
    | awk '$2 ~ /^[0-9]+\/[0-9]+$/{split($2,a,"/"); if(a[1]==a[2])n++; t++} END{printf "%d/%d", n, t}'
}
all_ready() { local r; r=$(pods_ready "$1"); [ -n "$r" ] && [ "${r%/*}" = "${r#*/}" ] && [ "${r%/*}" != "0" ]; }

echo "Local MLOps platform — service status"
echo "======================================="

# --- Kubernetes cluster ---
if kubectl get nodes --no-headers >/dev/null 2>&1; then
  row "Kind cluster" UP "$(kubectl get nodes --no-headers 2>/dev/null | awk '{print $1" ("$2")"}')"
else
  row "Kind cluster" DOWN "kubectl cannot reach the cluster"
fi

# --- In-cluster workloads ---
for ns in kubeflow monitoring; do
  r=$(pods_ready "$ns")
  if all_ready "$ns"; then row "ns/$ns pods" UP "$r ready"; else row "ns/$ns pods" DOWN "${r:-no pods} ready"; fi
done

isvc=$(kubectl get isvc taxi-fare-predictor -n mlops -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
[ "$isvc" = "True" ] && row "KServe InferenceSvc" UP "READY=True" || row "KServe InferenceSvc" DOWN "READY=${isvc:-?}"

app=$(kubectl get applications.argoproj.io taxi-fare-predictor -n argocd -o jsonpath='{.status.sync.status}/{.status.health.status}' 2>/dev/null)
[ "$app" = "Synced/Healthy" ] && row "Argo CD application" UP "$app" || row "Argo CD application" DOWN "${app:-not found}"

echo "---------------------------------------"

# --- Host endpoints (UIs) ---
c=$(http http://localhost:8080/);                 up_code "$c" && row "Jenkins (8080)"      UP "HTTP $c" || row "Jenkins (8080)"      DOWN "HTTP ${c:-000}"
c=$(http https://127.0.0.1:8443/ -k);             up_code "$c" && row "Argo CD UI (8443)"   UP "HTTP $c" || row "Argo CD UI (8443)"   DOWN "HTTP ${c:-000} (port-forward?)"
c=$(http http://127.0.0.1:5000/);                 up_code "$c" && row "MLflow (5000)"       UP "HTTP $c" || row "MLflow (5000)"       DOWN "HTTP ${c:-000} (run scripts/up.sh)"
c=$(http http://127.0.0.1:8082/);                 up_code "$c" && row "Kubeflow UI (8082)"  UP "HTTP $c" || row "Kubeflow UI (8082)"  DOWN "HTTP ${c:-000} (port-forward?)"
c=$(http http://127.0.0.1:8081/v1/models/taxi-fare-predictor); up_code "$c" && row "KServe API (8081)"   UP "HTTP $c" || row "KServe API (8081)"   DOWN "HTTP ${c:-000} (port-forward?)"
c=$(http http://localhost:5001/v2/_catalog);      up_code "$c" && row "Registry (5001)"     UP "HTTP $c" || row "Registry (5001)"     DOWN "HTTP ${c:-000}"
c=$(http http://127.0.0.1:8000/);                 up_code "$c" && row "Evidently UI (8000)"  UP "HTTP $c" || row "Evidently UI (8000)"  DOWN "HTTP ${c:-000} (make evidently-ui)"

echo "======================================="
if [ "$fail" -eq 0 ]; then echo "$(green "All services UP.")"; else echo "$(red "Some services are DOWN")  — run ./scripts/up.sh to start host services/port-forwards."; fi
exit "$fail"
