# KServe serving

Serves the NYC Taxi model as a KServe `InferenceService` in **RawDeployment**
mode (this cluster has no Knative).

## Two variants

| File | Approach | When |
|---|---|---|
| `inference-service.yaml` | **Custom container** — image bakes the model + KServe V1 dataplane | Preferred locally (no external storage) |
| `inference-service-sklearn.yaml` | `modelFormat: sklearn` + `storageUri` | Production-style reference; needs a reachable model store (PVC/S3/HTTP) |

## Deploy (custom container)

```bash
# 1. Train, build & push the serving image to the local registry
make train
make docker-build-kserve
make docker-push

# 2. Apply the namespace + InferenceService
kubectl apply -f namespace.yaml
kubectl apply -f inference-service.yaml

# 3. Watch it become ready
kubectl get inferenceservice -n mlops -w
kubectl get pods -n mlops
```

## Test inference

```bash
kubectl port-forward -n mlops svc/taxi-fare-predictor-predictor 8081:80 &
../scripts/test_endpoint.sh
```

Request/response (KServe V1):

```json
POST /v1/models/taxi-fare-predictor:predict
{ "instances": [[3.2, 1, 8, 2, 100, 230]] }
--> { "predictions": [25.16] }
```

Feature order: `[trip_distance, passenger_count, pickup_hour, pickup_dayofweek,
pu_location_id, do_location_id]`.

## MLflow vs KServe

MLflow's registry decides *which* model version is chosen; KServe is the runtime
that *serves* it behind an HTTP endpoint.
