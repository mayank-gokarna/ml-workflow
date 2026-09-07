"""Unit tests for data loading, validation and splitting."""

import numpy as np
import pandas as pd
import pytest

from mlops_demo.config import Config
from mlops_demo.data import (
    DataValidationError,
    generate_synthetic_data,
    load_dataset,
    split_dataset,
    validate_dataset,
    validate_features,
)


@pytest.fixture
def config() -> Config:
    return Config(n_samples=1500, mlflow_enabled=False)


def test_synthetic_data_shape_and_columns(config):
    frame = generate_synthetic_data(config=config)
    assert len(frame) == config.n_samples
    for col in config.feature_names + ["fare_amount", "trip_duration"]:
        assert col in frame.columns


def test_synthetic_data_is_deterministic(config):
    a = generate_synthetic_data(config=config)
    b = generate_synthetic_data(config=config)
    pd.testing.assert_frame_equal(a, b)


def test_fare_and_duration_are_positive(config):
    frame = generate_synthetic_data(config=config)
    assert (frame["fare_amount"] > 0).all()
    assert (frame["trip_duration"] > 0).all()


def test_load_dataset_uses_synthetic_by_default(config):
    frame = load_dataset(config)
    validate_dataset(frame, config)
    assert not frame.empty


def test_validate_features_rejects_missing_column(config):
    frame = generate_synthetic_data(config=config).drop(columns=["trip_distance"])
    with pytest.raises(DataValidationError):
        validate_features(frame, config)


def test_validate_features_rejects_nulls(config):
    frame = generate_synthetic_data(config=config)
    frame.loc[0, "trip_distance"] = np.nan
    with pytest.raises(DataValidationError):
        validate_features(frame, config)


def test_validate_dataset_rejects_missing_target():
    config = Config(target_column="trip_duration", n_samples=500)
    frame = generate_synthetic_data(config=config).drop(columns=["trip_duration"])
    with pytest.raises(DataValidationError):
        validate_dataset(frame, config)


def test_split_sizes_add_up(config):
    frame = load_dataset(config)
    X_train, X_test, y_train, y_test = split_dataset(frame, config)
    assert len(X_train) + len(X_test) == len(frame)
    assert len(X_train) == len(y_train)
    assert list(X_train.columns) == config.feature_names


def test_invalid_target_rejected():
    with pytest.raises(ValueError):
        Config(target_column="not_a_target")
