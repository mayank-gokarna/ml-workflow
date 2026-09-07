"""Model evaluation utilities and the quality gate.

Kept separate from training so metrics can be recomputed against any saved
model (e.g. in CI or a Kubeflow evaluate component). This is a regression
problem (predicting fare or trip duration), so we track error + R^2 metrics.
"""

from __future__ import annotations

import logging
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from .config import Config, get_config

logger = logging.getLogger(__name__)


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean absolute percentage error, guarding against divide-by-zero."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = np.abs(y_true) > 1e-9
    if not mask.any():
        return 0.0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)


def compute_metrics(y_true, y_pred) -> Dict[str, float]:
    """Compute the tracked regression metrics."""
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    metrics = {
        "rmse": rmse,
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
        "mape": _mape(y_true, y_pred),
    }
    logger.info(
        "Metrics: rmse=%.4f mae=%.4f r2=%.4f mape=%.2f%%",
        metrics["rmse"],
        metrics["mae"],
        metrics["r2"],
        metrics["mape"],
    )
    return metrics


def evaluate_model(
    model, X_test: pd.DataFrame, y_test: pd.Series, config: Config | None = None
) -> Dict[str, float]:
    """Predict on the test set and return metrics."""
    config = config or get_config()
    y_pred = model.predict(X_test)
    return compute_metrics(y_test, y_pred)


def passes_quality_gate(metrics: Dict[str, float], config: Config | None = None) -> bool:
    """Return True if R^2 meets the configurable minimum threshold."""
    config = config or get_config()
    r2 = metrics.get("r2", 0.0)
    passed = r2 >= config.min_r2
    if passed:
        logger.info("Quality gate PASSED: r2 %.4f >= %.4f", r2, config.min_r2)
    else:
        logger.warning("Quality gate FAILED: r2 %.4f < %.4f", r2, config.min_r2)
    return passed


def main() -> int:
    """Evaluate the saved local model against a fresh data sample."""
    from .data import load_dataset, split_dataset
    from .predict import load_model

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    config = get_config()
    model = load_model(config=config)
    frame = load_dataset(config)
    _, X_test, _, y_test = split_dataset(frame, config)
    metrics = evaluate_model(model, X_test, y_test, config)
    passed = passes_quality_gate(metrics, config)
    print({k: round(v, 4) for k, v in metrics.items()})
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
