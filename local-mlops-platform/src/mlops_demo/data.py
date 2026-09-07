"""Dataset loading, validation and splitting for NYC Taxi fare/time prediction.

By default this generates a small, deterministic **synthetic** taxi dataset so
the whole workflow runs offline (no download, reproducible tests/CI). Set
``USE_REAL_DATA=true`` (and run ``scripts/download_data.py``) to instead train
on a sampled slice of the real NYC TLC yellow-taxi trip data.

Everything returns tidy pandas objects with the canonical schema:
features + both possible targets (``fare_amount``, ``trip_duration``).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .config import VALID_TARGETS, Config, get_config

logger = logging.getLogger(__name__)

# All engineered columns a valid dataframe must carry (features + targets).
_ALL_COLUMNS = [
    "trip_distance",
    "passenger_count",
    "pickup_hour",
    "pickup_dayofweek",
    "pu_location_id",
    "do_location_id",
    "fare_amount",
    "trip_duration",
]

# Filename of the cached real-data sample produced by scripts/download_data.py.
SAMPLE_FILENAME = "nyc_taxi_sample.parquet"


class DataValidationError(ValueError):
    """Raised when a dataframe does not match the expected taxi schema."""


def generate_synthetic_data(
    n_samples: int | None = None, config: Config | None = None
) -> pd.DataFrame:
    """Generate a deterministic synthetic NYC-taxi-like dataset.

    Fares and durations are derived from trip distance and time-of-day with
    realistic coefficients plus noise, giving learnable (high-R^2) targets.
    """
    config = config or get_config()
    n = n_samples or config.n_samples
    rng = np.random.default_rng(config.random_state)

    # Trip distance (miles): most trips short, long tail. Clip to sane bounds.
    trip_distance = np.clip(rng.gamma(shape=2.0, scale=1.6, size=n), 0.3, 40.0)
    passenger_count = rng.integers(1, 7, size=n)
    pickup_hour = rng.integers(0, 24, size=n)
    pickup_dayofweek = rng.integers(0, 7, size=n)
    pu_location_id = rng.integers(1, 264, size=n)
    do_location_id = rng.integers(1, 264, size=n)

    is_weekend = pickup_dayofweek >= 5
    is_rush = np.isin(pickup_hour, [7, 8, 9, 16, 17, 18, 19]) & ~is_weekend
    is_night = np.isin(pickup_hour, [0, 1, 2, 3, 4, 5, 22, 23])

    # Average speed (mph) is lower during weekday rush, higher at night/weekend.
    speed = np.full(n, 16.0)
    speed[is_rush] = 9.0
    speed[is_night] = 22.0
    speed[is_weekend & ~is_night] = 18.0

    duration = (trip_distance / speed) * 60.0 + rng.normal(0.0, 1.5, size=n)
    trip_duration = np.clip(duration, 1.0, None)

    # Standard NYC-style fare: base + per-mile + per-minute + surcharges + noise.
    surcharge = np.where(is_rush, 2.5, 0.0) + np.where(is_night, 1.0, 0.0)
    fare_amount = (
        3.0
        + 2.5 * trip_distance
        + 0.5 * trip_duration
        + surcharge
        + rng.normal(0.0, 1.2, size=n)
    )
    fare_amount = np.clip(fare_amount, 3.0, None)

    frame = pd.DataFrame(
        {
            "trip_distance": trip_distance,
            "passenger_count": passenger_count,
            "pickup_hour": pickup_hour,
            "pickup_dayofweek": pickup_dayofweek,
            "pu_location_id": pu_location_id,
            "do_location_id": do_location_id,
            "fare_amount": fare_amount.round(2),
            "trip_duration": trip_duration.round(2),
        }
    )
    logger.info("Generated %d synthetic taxi trips", len(frame))
    return frame


def load_real_sample(config: Config | None = None) -> pd.DataFrame:
    """Load the cached real NYC TLC sample written by download_data.py."""
    config = config or get_config()
    path = Path(config.data_raw_dir) / SAMPLE_FILENAME
    if not path.exists():
        raise FileNotFoundError(
            f"Real-data sample not found at {path}. Run "
            "`python scripts/download_data.py` first, or unset USE_REAL_DATA "
            "to use the synthetic generator."
        )
    logger.info("Loading real NYC taxi sample from %s", path)
    frame = pd.read_parquet(path)
    validate_dataset(frame, config)
    return frame


def load_dataset(config: Config | None = None) -> pd.DataFrame:
    """Load the taxi dataset (real sample if enabled, else synthetic)."""
    config = config or get_config()
    if config.use_real_data:
        frame = load_real_sample(config)
    else:
        logger.info("Using synthetic taxi dataset (USE_REAL_DATA=false)")
        frame = generate_synthetic_data(config=config)
    validate_dataset(frame, config)
    logger.info(
        "Loaded %d rows; target=%s", len(frame), config.target_column
    )
    return frame


def validate_features(frame: pd.DataFrame, config: Config | None = None) -> None:
    """Validate that ``frame`` has the expected feature schema."""
    config = config or get_config()

    missing = [c for c in config.feature_names if c not in frame.columns]
    if missing:
        raise DataValidationError(
            f"Dataset is missing required feature columns: {missing}. "
            f"Expected features: {config.feature_names}"
        )

    features = frame[config.feature_names]
    if features.isnull().any().any():
        null_cols = features.columns[features.isnull().any()].tolist()
        raise DataValidationError(
            f"Feature columns contain null values: {null_cols}. "
            "Clean or impute the data before training."
        )

    non_numeric = [
        c for c in config.feature_names if not np.issubdtype(features[c].dtype, np.number)
    ]
    if non_numeric:
        raise DataValidationError(
            f"Feature columns must be numeric, but these are not: {non_numeric}."
        )

    if (features < 0).any().any():
        raise DataValidationError(
            "Feature values must be non-negative; found negative values."
        )


def validate_dataset(frame: pd.DataFrame, config: Config | None = None) -> None:
    """Validate features and that the configured target column is present."""
    config = config or get_config()
    validate_features(frame, config)

    if config.target_column not in frame.columns:
        raise DataValidationError(
            f"Target column '{config.target_column}' not found. "
            f"Available targets: {list(VALID_TARGETS)}"
        )
    if frame[config.target_column].isnull().any():
        raise DataValidationError(
            f"Target column '{config.target_column}' contains null values."
        )


def split_dataset(
    frame: pd.DataFrame, config: Config | None = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split into train/test features and target (reproducible)."""
    config = config or get_config()
    validate_dataset(frame, config)

    X = frame[config.feature_names]
    y = frame[config.target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config.test_size,
        random_state=config.random_state,
    )
    logger.info("Split dataset: %d train / %d test rows", len(X_train), len(X_test))
    return X_train, X_test, y_train, y_test
