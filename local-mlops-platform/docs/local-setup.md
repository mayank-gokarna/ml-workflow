# Local setup

Verified local environment (detected during Phase 1):

| Tool | Version |
|---|---|
| Python | 3.12 (`python3`) |
| Docker | 29.x |
| kubectl | 1.35 |
| Helm | 3.21 |
| Kind cluster | `kind-platform`, K8s 1.30 |
| KServe | RawDeployment, sklearn runtime |
| Argo CD | running (`argocd` ns), UI `https://127.0.0.1:8443` |
| Jenkins | running, `http://localhost:8080` |
| Registry | `localhost:5001` (Kind-attached) |
| Monitoring | Prometheus + Grafana (`monitoring` ns) |

> Run everything from **WSL**. Put the virtualenv on the native Linux
> filesystem — the OneDrive-synced `/mnt/c` path is slow and can corrupt large
> installs like MLflow.

## Python

```bash
cd local-mlops-platform
make install VENV=~/venvs/mlops-demo
make test
```

### Windows PowerShell (no Make)

```powershell
cd local-mlops-platform
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt -e .
pytest -q
python -m mlops_demo.train
```

## MLflow

```bash
make mlflow VENV=~/venvs/mlops-demo   # http://127.0.0.1:5000
MLFLOW_TRACKING_URI=http://127.0.0.1:5000 make train VENV=~/venvs/mlops-demo
```

## Docker + local registry

```bash
make train                 # produces models/model.joblib
make docker-build-kserve   # builds localhost:5001/taxi-fare-predictor-serve
make docker-push           # pushes to the Kind registry (localhost:5001)
```

## Kubernetes

```bash
make k8s-install           # namespace + configmap
kubectl get ns mlops
```

## Kubeflow (compile the pipeline)

```bash
pip install "kfp>=2.7,<3"
make kfp-compile           # -> kubeflow/nyc_taxi_pipeline.yaml
```

## KServe

```bash
make kserve-deploy
kubectl get inferenceservice -n mlops -w
kubectl port-forward -n mlops svc/taxi-fare-predictor-predictor 8081:80 &
./scripts/test_endpoint.sh
```

## Jenkins integration

Create a Pipeline job pointing at `local-mlops-platform/jenkins/Jenkinsfile`
(branch `main`). See `jenkins/README.md`.

## Argo CD integration

```bash
kubectl apply -f argocd/application.yaml
kubectl get applications -n argocd
```

See `argocd/README.md`.

## GitHub

The repo is `mayank-gokarna/ml-workflow`; the project lives under
`local-mlops-platform/`. Argo CD and Jenkins both reference this repo/branch.
