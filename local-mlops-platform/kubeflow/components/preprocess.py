"""Kubeflow Pipelines v2 component: preprocess / generate the dataset.

Self-contained (runs in its own container), so it re-implements the synthetic
NYC-taxi generator rather than importing the project package. Emits a CSV
``Dataset`` artifact consumed by downstream components.
"""

from kfp import dsl
from kfp.dsl import Dataset, Output

BASE_IMAGE = "python:3.12-slim"
PACKAGES = ["numpy==2.*", "pandas==2.*"]


@dsl.component(base_image=BASE_IMAGE, packages_to_install=PACKAGES)
def preprocess(
    dataset: Output[Dataset],
    n_samples: int = 20000,
    random_state: int = 42,
    target: str = "fare_amount",
):
    """Generate a synthetic NYC-taxi dataset and write it as CSV."""
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(random_state)
    n = n_samples

    trip_distance = np.clip(rng.gamma(2.0, 1.6, n), 0.3, 40.0)
    passenger_count = rng.integers(1, 7, n)
    pickup_hour = rng.integers(0, 24, n)
    pickup_dayofweek = rng.integers(0, 7, n)
    pu_location_id = rng.integers(1, 264, n)
    do_location_id = rng.integers(1, 264, n)

    is_weekend = pickup_dayofweek >= 5
    is_rush = np.isin(pickup_hour, [7, 8, 9, 16, 17, 18, 19]) & ~is_weekend
    is_night = np.isin(pickup_hour, [0, 1, 2, 3, 4, 5, 22, 23])

    speed = np.full(n, 16.0)
    speed[is_rush] = 9.0
    speed[is_night] = 22.0
    speed[is_weekend & ~is_night] = 18.0

    duration = np.clip((trip_distance / speed) * 60.0 + rng.normal(0, 1.5, n), 1.0, None)
    surcharge = np.where(is_rush, 2.5, 0.0) + np.where(is_night, 1.0, 0.0)
    fare = np.clip(
        3.0 + 2.5 * trip_distance + 0.5 * duration + surcharge + rng.normal(0, 1.2, n),
        3.0,
        None,
    )

    df = pd.DataFrame(
        {
            "trip_distance": trip_distance,
            "passenger_count": passenger_count,
            "pickup_hour": pickup_hour,
            "pickup_dayofweek": pickup_dayofweek,
            "pu_location_id": pu_location_id,
            "do_location_id": do_location_id,
            "fare_amount": fare.round(2),
            "trip_duration": duration.round(2),
        }
    )
    # Keep the chosen target as the canonical 'label' column for downstream steps.
    df["label"] = df[target]
    df.to_csv(dataset.path, index=False)
    print(f"preprocess: wrote {len(df)} rows -> {dataset.path}")
