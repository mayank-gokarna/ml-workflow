# MLflow (local)

MLflow provides **experiment tracking** and a **model registry** for this project.

## Run a local tracking server

```bash
make mlflow
# equivalently:
mlflow server --host 127.0.0.1 --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns
```

Then point training at it (defaults already match):

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
export MLFLOW_EXPERIMENT_NAME=nyc-taxi-fare
make train
```

Open the UI at http://127.0.0.1:5000.

## Concepts demonstrated

```
Experiment (nyc-taxi-fare)
  └── Run
        ├── Parameters (model_type, n_estimators, random_state, git_commit, ...)
        ├── Metrics (rmse, mae, r2, mape)
        └── Model Artifact (sklearn model + signature + input example)
              └── Registered Model (taxi-fare-predictor)  ← only if quality gate passes
```

- **MLflow Tracking** — records params, metrics, and artifacts per run so results
  are reproducible and comparable.
- **MLflow Model Registry** — versions a named model (`taxi-fare-predictor`) and
  manages its lifecycle. Training registers a new version only when the quality
  gate (`r2 >= MIN_R2`) passes.

## Model versioning & stages

Each qualifying training run creates a new **version** of `taxi-fare-predictor`
(v1, v2, v3, …). Newer MLflow versions favor **aliases** (e.g. `@champion`,
`@staging`, `@production`) and tags over the deprecated stage transitions
(`Staging`/`Production`). Conceptual promotion path:

```
None → Candidate → Staging → Production
```

Assign an alias to promote a version, for example:

```python
from mlflow import MlflowClient
c = MlflowClient()
c.set_registered_model_alias("taxi-fare-predictor", "production", version="3")
```

## MLflow vs KServe

- **MLflow Model Registry** = *system of record* for model versions/metadata.
- **KServe** = *runtime* that serves a chosen model version behind an HTTP API.

The registry decides *which* model; KServe *runs* it.
