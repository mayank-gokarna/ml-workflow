# Troubleshooting

## kubectl cannot connect
- Check context: `kubectl config current-context` (should be `kind-platform`).
- `kubectl cluster-info`; ensure the Kind container is running: `docker ps | grep control-plane`.

## KServe CRD missing
- `kubectl get crd | grep serving.kserve.io` — should list `inferenceservices...`.
- If missing, the KServe controller isn't installed; this cluster already has it.

## InferenceService stuck / not Ready
- `kubectl get inferenceservice -n mlops`
- `kubectl describe inferenceservice taxi-fare-predictor -n mlops`
- `kubectl get pods -n mlops` then `kubectl logs <pod> -n mlops`.
- RawDeployment: confirm the predictor Deployment/Service exist.

## ImagePullBackOff
- The image must be in the Kind registry: `make docker-build-kserve && make docker-push`.
- Verify: `curl -s http://localhost:5001/v2/_catalog`.
- Manifest uses `localhost:5001/taxi-fare-predictor-serve:latest`.

## MLflow unavailable
- Start it: `make mlflow`. Training still succeeds and saves a local artifact if
  MLflow is down (logging is best-effort).
- `log_model` errors about `name=`: you're on MLflow 2.x — use `artifact_path=`.

## Kubeflow pipeline compilation failure
- Install a matching SDK: `pip install "kfp>=2.7,<3"`.
- Run `python kubeflow/pipeline.py`; read the KFP validation error and fix the
  offending component signature.

## Argo CD OutOfSync
- `kubectl describe application taxi-fare-predictor -n argocd`.
- Manual sync: `argocd app sync taxi-fare-predictor` (or click Sync in the UI).
- Confirm `repoURL`/branch/path are correct and the repo is reachable.

## Jenkins Docker permission problems
- The agent user needs Docker access (member of the `docker` group or a Docker
  cloud agent). The pipeline skips Build/Push with a warning if `docker` is
  absent rather than failing silently.

## localhost registry problems
- Registry container: `docker ps | grep kind-registry` (expects `:5001`).
- Catalog: `curl http://localhost:5001/v2/_catalog`.

## WSL / OneDrive install corruption
- Symptom: `FileNotFoundError: .../pip/_vendor/.../jisfreq.py` or partial venvs.
- Cause: the OneDrive-synced `/mnt/c` path + concurrent installs.
- Fix: create the venv on native fs — `make install VENV=~/venvs/mlops-demo` —
  and avoid running two installs into the same venv at once.
