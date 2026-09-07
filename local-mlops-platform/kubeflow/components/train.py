"""Kubeflow Pipelines v2 component: train the model."""

from kfp import dsl
from kfp.dsl import Dataset, Input, Model, Output

BASE_IMAGE = "python:3.12-slim"
PACKAGES = ["numpy==2.*", "pandas==2.*", "scikit-learn==1.*", "joblib==1.*"]

FEATURES = [
    "trip_distance",
    "passenger_count",
    "pickup_hour",
    "pickup_dayofweek",
    "pu_location_id",
    "do_location_id",
]


@dsl.component(base_image=BASE_IMAGE, packages_to_install=PACKAGES)
def train(
    dataset: Input[Dataset],
    model: Output[Model],
    n_estimators: int = 200,
    random_state: int = 42,
):
    """Train a RandomForestRegressor and emit a joblib Model artifact."""
    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor

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

    reg = RandomForestRegressor(
        n_estimators=n_estimators, random_state=random_state, n_jobs=-1
    )
    reg.fit(X, y)

    model.metadata["framework"] = "scikit-learn"
    model.metadata["n_estimators"] = n_estimators
    joblib.dump(reg, model.path)
    print(f"train: saved model -> {model.path}")
