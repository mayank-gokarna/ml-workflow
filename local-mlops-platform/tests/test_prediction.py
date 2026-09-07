"""Unit tests for prediction helpers."""

import pytest

from mlops_demo.config import Config
from mlops_demo.predict import ModelNotFoundError, load_model, predict
from mlops_demo.train import run_training


@pytest.fixture
def trained_config(tmp_path) -> Config:
    config = Config(
        n_samples=3000,
        n_estimators=60,
        mlflow_enabled=False,
        model_dir=tmp_path / "models",
    )
    run_training(config)
    return config


def _sample_vector(config: Config):
    # trip_distance, passenger_count, pickup_hour, dow, pu_id, do_id
    return [3.2, 1, 8, 2, 100, 230]


def test_predict_with_list_instance(trained_config):
    model = load_model(config=trained_config)
    preds = predict([_sample_vector(trained_config)], model=model, config=trained_config)
    assert len(preds) == 1
    assert preds[0] > 0


def test_predict_with_dict_instance(trained_config):
    record = dict(zip(trained_config.feature_names, _sample_vector(trained_config)))
    preds = predict([record], config=trained_config)
    assert len(preds) == 1
    assert isinstance(preds[0], float)


def test_predict_rejects_wrong_length(trained_config):
    with pytest.raises(ValueError):
        predict([[1.0, 2.0]], config=trained_config)


def test_predict_rejects_missing_dict_feature(trained_config):
    with pytest.raises(ValueError):
        predict([{"trip_distance": 3.0}], config=trained_config)


def test_load_model_missing_raises(tmp_path):
    config = Config(model_dir=tmp_path / "empty")
    with pytest.raises(ModelNotFoundError):
        load_model(config=config)
