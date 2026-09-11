# ml-workflow

This repository hosts a complete, **local, production-style MLOps platform** built
around a **NYC Taxi fare / trip-time prediction** model. It demonstrates the full
machine-learning lifecycle running end-to-end on a local Kubernetes (Kind)
cluster:

> Data → Training → Experiment Tracking (MLflow) → Model Registry → CI (Jenkins)
> → Container Image → Kubernetes → Serving (KServe) → GitOps (Argo CD) → Monitoring

The actual project lives in **[local-mlops-platform/](local-mlops-platform/)** —
see its [README](local-mlops-platform/README.md) for architecture, code, and
detailed docs. This top-level README is a quick map of the repo and, most
importantly, **how to open every UI/endpoint**.

## Purpose

- A realistic MLOps/DevOps **portfolio and interview** project that runs locally.
- Shows clear separation of concerns: **Jenkins = CI**, **Argo CD = CD/GitOps**,
  **MLflow = tracking + registry**, **KServe = serving**, **Prometheus/Grafana =
  monitoring**.
- Small, open dataset (synthetic NYC-taxi generator by default) so the whole
  workflow runs on a laptop.

## Repository layout

| Path | What it is |
|---|---|
| `local-mlops-platform/` | The MLOps project (code, Docker, K8s, KServe, Jenkins, Argo CD, docs) |
| `specs/` | Nova spec scaffolds (requirements/design/tasks) |
| `.github/` | Agent/skill customization files |

---

## Accessing the UIs / endpoints

Some services are exposed directly; in-cluster services need a `kubectl
port-forward` first. Run these from **WSL**.

### Directly available (already running)

| Service | URL | Purpose | Notes |
|---|---|---|---|
| **Jenkins** | http://localhost:8080 | CI pipeline | Requires login |
| **Argo CD** | https://127.0.0.1:8443 | GitOps CD dashboard | Self-signed cert — accept the warning |
| **Local registry** | http://localhost:5001/v2/_catalog | Container image registry | Lists pushed images |

### MLflow (start it, then browse)

```bash
cd local-mlops-platform
make mlflow            # serves on http://127.0.0.1:5000
```

| Service | URL | Purpose |
|---|---|---|
| **MLflow UI** | http://127.0.0.1:5000 | Experiments, runs, metrics, model registry |

### Model serving (KServe) — needs a port-forward

```bash
kubectl port-forward -n mlops svc/taxi-fare-predictor-predictor 8081:80
```

| Endpoint | Method | URL |
|---|---|---|
| Predict | POST | http://127.0.0.1:8081/v1/models/taxi-fare-predictor:predict |
| Model ready | GET | http://127.0.0.1:8081/v1/models/taxi-fare-predictor |
| Health | GET | http://127.0.0.1:8081/healthz |
| Prometheus metrics | GET | http://127.0.0.1:8081/metrics |

Example request (feature order: `trip_distance, passenger_count, pickup_hour,
pickup_dayofweek, pu_location_id, do_location_id`):

```bash
curl -X POST http://127.0.0.1:8081/v1/models/taxi-fare-predictor:predict \
  -H 'Content-Type: application/json' \
  -d '{"instances": [[3.2, 1, 8, 2, 100, 230]]}'
# -> {"predictions":[25.16]}
```

Or run the helper script: `./local-mlops-platform/scripts/test_endpoint.sh`.

### Monitoring — needs a port-forward

```bash
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
kubectl port-forward -n monitoring svc/grafana 3000:80
```

| Service | URL | Purpose |
|---|---|---|
| **Prometheus** | http://127.0.0.1:9090 | Metrics store / queries |
| **Grafana** | http://127.0.0.1:3000 | Dashboards |

### Kubeflow Pipelines UI (optional / not currently available)

The Kubeflow Pipelines UI is **not running** in this cluster. The KFP 2.2.0
`frontend` and `minio` images were removed from `gcr.io` (Google's gcr.io
deprecation), so the standalone install can't complete. The pipeline itself is
authored and **compiles** to `local-mlops-platform/kubeflow/nyc_taxi_pipeline.yaml`.
If a working KFP backend is installed later, its UI is reached with:

```bash
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8082:80
# UI: http://127.0.0.1:8082
```

---

## Quick health check

```bash
kubectl get inferenceservice -n mlops                  # model serving (expect READY=True)
kubectl get applications -n argocd                     # GitOps app (expect Synced/Healthy)
curl -s http://localhost:5001/v2/_catalog              # registry images
```

For everything else — setup, architecture, troubleshooting, interview notes —
see [local-mlops-platform/docs/](local-mlops-platform/docs/).
