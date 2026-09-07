"""Unit tests for training, evaluation and the quality gate."""

import pytest
from sklearn.ensemble import RandomForestRegressor

from mlops_demo.config import Config
from mlops_demo.evaluate import compute_metrics, passes_quality_gate
from mlops_demo.train import build_model, run_training


@pytest.fixture
def config(tmp_path) -> Config:
    # Small, fast, offline: no MLflow, temp artifact dir.
    return Config(
        n_samples=3000,
        n_estimators=60,
        mlflow_enabled=False,
        model_dir=tmp_path / "models",
    )


def test_build_model_uses_config(config):
    model = build_model(config)
    assert isinstance(model, RandomForestRegressor)
    assert model.n_estimators == config.n_estimators
    assert model.random_state == config.random_state


def test_run_training_produces_good_model(config):
    model, metrics, gate_passed = run_training(config)
    assert set(metrics) == {"rmse", "mae", "r2", "mape"}
    # Synthetic fares are highly learnable; expect a strong fit.
    assert metrics["r2"] > 0.85
    assert gate_passed is True


def test_run_training_saves_local_artifact(config):
    run_training(config)
    assert config.local_model_path.exists()


def test_quality_gate_thresholds():
    strict = Config(min_r2=0.99)
    assert passes_quality_gate({"r2": 0.95}, strict) is False
    lenient = Config(min_r2=0.50)
    assert passes_quality_gate({"r2": 0.95}, lenient) is True


def test_compute_metrics_perfect_prediction():
    y = [10.0, 20.0, 30.0]
    metrics = compute_metrics(y, y)
    assert metrics["rmse"] == pytest.approx(0.0)
    assert metrics["r2"] == pytest.approx(1.0)
