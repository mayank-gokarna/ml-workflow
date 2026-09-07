# Argo CD GitOps (CD)

Argo CD performs **Continuous Deployment** by syncing the Kubernetes/KServe
manifests from Git. The application code and CI live elsewhere; Argo CD only
cares about the declarative desired state in `../gitops`.

```mermaid
flowchart LR
    GitHub --> ArgoCD[Argo CD]
    ArgoCD --> K8s[Kubernetes]
    K8s --> KServe[KServe InferenceService]
```

## What it deploys

`application.yaml` uses an Argo CD **directory source** with an `include` glob so
it deploys exactly these manifests from the repo (no duplication into a separate
overlay):

- `kubernetes/namespace.yaml` — the `mlops` namespace
- `kubernetes/configmap.yaml` — app config
- `kserve/inference-service.yaml` — the KServe InferenceService

`secret.yaml.example` and the sklearn variant are excluded. Sync policy:
**automated** with `prune` and `selfHeal` (declarative, self-correcting).

## Register the application

Argo CD is already running (do not reinstall). UI: https://127.0.0.1:8443.

```bash
kubectl apply -f application.yaml

# Inspect
kubectl get applications -n argocd
kubectl describe application taxi-fare-predictor -n argocd

# CLI (optional)
argocd app get taxi-fare-predictor
argocd app sync taxi-fare-predictor
```

## Sync status

```bash
kubectl get application taxi-fare-predictor -n argocd \
  -o jsonpath='{.status.sync.status} / {.status.health.status}{"\n"}'
```

Expect `Synced / Healthy` once the serving image is present in the registry and
the InferenceService is running.

## Troubleshooting

- **OutOfSync**: run a manual sync, or check `kubectl describe application ...`.
- **ImagePullBackOff**: ensure `make docker-build-kserve && make docker-push`
  pushed `localhost:5001/taxi-fare-predictor-serve:latest`.
- **Repo not accessible**: confirm the `repoURL`/branch and that the repo is
  reachable from the Argo CD repo-server.
