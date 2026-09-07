# Kubernetes base resources

Namespace and shared configuration for the demo. Serving is handled by KServe
(see `../kserve/`).

## Apply

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
# secrets: copy the example, fill real values locally, then apply (git-ignored)
cp secret.yaml.example secret.yaml   # edit secret.yaml
kubectl apply -f secret.yaml
```

## Files

| File | Kind | Purpose |
|---|---|---|
| `namespace.yaml` | Namespace | Creates the `mlops` namespace |
| `configmap.yaml` | ConfigMap | Non-secret app config (model name, quality gate, MLflow) |
| `secret.yaml.example` | Secret (template) | Template for credentials — **never commit the real one** |

## Verify

```bash
kubectl get ns mlops
kubectl get configmap mlops-demo-config -n mlops -o yaml
```

## Security

- Real secrets live only in `secret.yaml` (git-ignored) or a secrets manager.
- The serving workload runs as non-root (see the Docker image) and needs no
  elevated privileges.
