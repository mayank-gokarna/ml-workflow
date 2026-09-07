"""Kubeflow Pipelines v2 component: evaluate the trained model."""

from kfp import dsl
from kfp.dsl import Dataset, Input, Metrics, Model, Output

BASE_IMAGE = "python:3.12-slim"
PACKAGES = ["numpy==2.*", "pandas==2.*", "scikit-learn==1.*", "joblib==1.*"]


@dsl.component(base_image=BASE_IMAGE, packages_to_install=PACKAGES)
def evaluate(
    dataset: Input[Dataset],
    model: Input[Model],
    metrics: Output[Metrics],
    min_r2: float = 0.80,
) -> bool:
    """Evaluate on the dataset, log metrics, and return whether the gate passed."""
    import joblib
    import numpy as np
    import pandas as pd
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    features = [
        "trip_distance",
        "passenger_count",
        "pickup_hour",
        "pickup_dayofweek",
        "pu_location_id",
        "do_location_id",
    ]
    df = pd.read_csv(dataset.path)
    X, y = df[features], df["label"]

    reg = joblib.load(model.path)
    pred = reg.predict(X)

    rmse = float(np.sqrt(mean_squared_error(y, pred)))
    mae = float(mean_absolute_error(y, pred))
    r2 = float(r2_score(y, pred))

    metrics.log_metric("rmse", rmse)
    metrics.log_metric("mae", mae)
    metrics.log_metric("r2", r2)

    passed = r2 >= min_r2
    print(f"evaluate: rmse={rmse:.4f} mae={mae:.4f} r2={r2:.4f} gate_passed={passed}")
    return passed
