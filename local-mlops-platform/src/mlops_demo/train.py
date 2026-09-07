"""Training entry point: train, evaluate, log to MLflow, save artifact.

MLflow is optional at runtime â€” if the tracking server is unreachable the run
still trains and saves a local model artifact so the workflow never hard-fails
on a missing server. A configurable R^2 quality gate decides promotion.
"""

from __future__ import annotations

import argparse
import logging
import platform
import subprocess
import sys
from typing import Dict, Optional, Tuple

import joblib
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor

from . import __version__
from .config import Config, get_config
from .data import load_dataset, split_dataset
from .evaluate import compute_metrics, passes_quality_gate

logger = logging.getLogger(__name__)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging once, with a concise format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def _git(*args: str) -> str:
    """Run a git command, returning 'unknown' if git/metadata is unavailable."""
    try:
        out = subprocess.check_output(
            ["git", *args], stderr=subprocess.DEVNULL, text=True
        )
        return out.strip() or "unknown"
    except Exception:  # noqa: BLE001 - metadata is best-effort
        return "unknown"


def git_metadata() -> Dict[str, str]:
    """Capture git commit SHA and branch (best-effort, never fails)."""
    return {
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
    }


def build_model(config: Config) -> RandomForestRegressor:
    """Construct the regressor from configured hyperparameters."""
    return RandomForestRegressor(
        n_estimators=config.n_estimators,
        max_depth=(config.max_depth or None),
        random_state=config.random_state,
        n_jobs=-1,
    )


def train_model(
    X_train: pd.DataFrame, y_train: pd.Series, config: Config
) -> RandomForestRegressor:
    """Fit the model on the training set."""
    logger.info("Training %s (n_estimators=%d)", config.model_type, config.n_estimators)
    model = build_model(config)
    model.fit(X_train, y_train)
    logger.info("Training complete")
    return model


def save_local_model(model, config: Config) -> None:
    """Persist the trained model as a joblib fallback artifact."""
    config.model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, config.local_model_path)
    logger.info("Saved local model artifact -> %s", config.local_model_path)


def _log_to_mlflow(
    model,
    params: Dict[str, object],
    metrics: Dict[str, float],
    X_train: pd.DataFrame,
    promote: bool,
    config: Config,
) -> Optional[str]:
    """Log params/metrics/model to MLflow and register if the gate passed.

    Returns the run id on success, or None if MLflow is unavailable (the run
    continues with the local artifact only).
    """
    try:
        import mlflow
        from mlflow.models.signature import infer_signature
    except ImportError:
        logger.warning("mlflow not installed; skipping experiment tracking")
        return None

    try:
        mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        mlflow.set_experiment(config.mlflow_experiment_name)
        with mlflow.start_run() as run:
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            signature = infer_signature(X_train, model.predict(X_train))
            mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                signature=signature,
                input_example=X_train.head(3),
                registered_model_name=config.model_name if promote else None,
            )
            logger.info(
                "Logged run %s to MLflow experiment '%s'",
                run.info.run_id,
                config.mlflow_experiment_name,
            )
            if promote:
                logger.info(
                    "Registered model '%s' (quality gate passed)", config.model_name
                )
            else:
                logger.warning(
                    "Model NOT registered: quality gate failed (r2 < %.2f)",
                    config.min_r2,
                )
            return run.info.run_id
    except Exception as exc:  # noqa: BLE001 - tracking must never break training
        logger.warning(
            "MLflow logging skipped (%s). Is the tracking server at %s running?",
            exc,
            config.mlflow_tracking_uri,
        )
        return None


def run_training(config: Config | None = None) -> Tuple[object, Dict[str, float], bool]:
    """Full training flow. Returns (model, metrics, gate_passed)."""
    config = config or get_config()

    frame = load_dataset(config)
    X_train, X_test, y_train, y_test = split_dataset(frame, config)

    model = train_model(X_train, y_train, config)

    logger.info("Evaluating on held-out test set")
    y_pred = model.predict(X_test)
    metrics = compute_metrics(y_test, y_pred)
    gate_passed = passes_quality_gate(metrics, config)

    meta = git_metadata()
    params = {
        "model_type": config.model_type,
        "target": config.target_column,
        "random_state": config.random_state,
        "n_estimators": config.n_estimators,
        "max_depth": config.max_depth or "none",
        "train_size": len(X_train),
        "test_size": len(X_test),
        "n_features": len(config.feature_names),
        "data_source": "real" if config.use_real_data else "synthetic",
        "python_version": platform.python_version(),
        "sklearn_version": sklearn.__version__,
        "package_version": __version__,
        **meta,
    }

    save_local_model(model, config)

    if config.mlflow_enabled:
        _log_to_mlflow(model, params, metrics, X_train, gate_passed, config)
    else:
        logger.info("MLflow disabled (MLFLOW_ENABLED=false)")

    _print_summary(params, metrics, gate_passed, config)
    return model, metrics, gate_passed


def _print_summary(
    params: Dict[str, object], metrics: Dict[str, float], gate_passed: bool, config: Config
) -> None:
    line = "=" * 60
    print(f"\n{line}")
    print(f" NYC Taxi model training summary  (target: {config.target_column})")
    print(line)
    print(f" model_type    : {params['model_type']}")
    print(f" data_source   : {params['data_source']}")
    print(f" train / test  : {params['train_size']} / {params['test_size']}")
    print(f" git_commit    : {params['git_commit']}")
    print("-" * 60)
    for k in ("rmse", "mae", "r2", "mape"):
        print(f" {k:<13}: {metrics[k]:.4f}")
    print("-" * 60)
    status = "PASSED" if gate_passed else "FAILED"
    print(f" quality gate  : {status} (min_r2={config.min_r2})")
    print(f"{line}\n")


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="Train the NYC Taxi model")
    parser.add_argument(
        "--no-gate",
        action="store_true",
        help="Do not fail the process when the quality gate fails",
    )
    args = parser.parse_args(argv)

    configure_logging()
    try:
        _, _, gate_passed = run_training()
    except Exception as exc:  # noqa: BLE001 - surface a clear CLI failure
        logger.error("Training failed: %s", exc)
        return 2

    if not gate_passed and not args.no_gate:
        logger.error("Exiting non-zero because the quality gate failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
