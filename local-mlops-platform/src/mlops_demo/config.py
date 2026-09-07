"""Central configuration for the MLOps demo.

All tunable settings are read from environment variables with sensible
defaults so nothing is hardcoded across the codebase. Import ``get_config()``
wherever configuration is needed.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List

# Repository root = three levels up from this file:
# src/mlops_demo/config.py -> src/mlops_demo -> src -> <project root>
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    val = os.getenv(name)
    try:
        return int(val) if val is not None else default
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    val = os.getenv(name)
    try:
        return float(val) if val is not None else default
    except ValueError:
        return default


# Regression targets the model can be trained to predict.
VALID_TARGETS = ("fare_amount", "trip_duration")


@dataclass(frozen=True)
class Config:
    """Immutable runtime configuration resolved from the environment."""

    # --- MLflow ---
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    mlflow_experiment_name: str = os.getenv("MLFLOW_EXPERIMENT_NAME", "nyc-taxi-fare")
    mlflow_enabled: bool = _get_bool("MLFLOW_ENABLED", True)

    # --- Model / registry ---
    model_name: str = os.getenv("MODEL_NAME", "taxi-fare-predictor")
    model_type: str = os.getenv("MODEL_TYPE", "RandomForestRegressor")

    # --- Prediction target: 'fare_amount' (USD) or 'trip_duration' (minutes) ---
    target_column: str = os.getenv("TARGET", "fare_amount")

    # --- Training hyperparameters ---
    random_state: int = _get_int("RANDOM_STATE", 42)
    n_estimators: int = _get_int("N_ESTIMATORS", 200)
    max_depth: int = _get_int("MAX_DEPTH", 0)  # 0 => None (unbounded)
    test_size: float = _get_float("TEST_SIZE", 0.2)

    # --- Data source ---
    n_samples: int = _get_int("N_SAMPLES", 20000)
    use_real_data: bool = _get_bool("USE_REAL_DATA", False)

    # --- Quality gate (regression: minimum R^2 on the test set) ---
    min_r2: float = _get_float("MIN_R2", 0.80)

    # --- Container image ---
    image_name: str = os.getenv("IMAGE_NAME", "localhost:5001/taxi-fare-predictor")
    image_tag: str = os.getenv("IMAGE_TAG", "latest")

    # --- Kubernetes ---
    kubernetes_namespace: str = os.getenv("KUBERNETES_NAMESPACE", "mlops")

    # --- Local artifact paths ---
    model_dir: Path = PROJECT_ROOT / os.getenv("MODEL_DIR", "models")
    data_raw_dir: Path = PROJECT_ROOT / "data" / "raw"
    data_processed_dir: Path = PROJECT_ROOT / "data" / "processed"

    # --- Dataset schema ---
    feature_names: List[str] = field(
        default_factory=lambda: [
            "trip_distance",
            "passenger_count",
            "pickup_hour",
            "pickup_dayofweek",
            "pu_location_id",
            "do_location_id",
        ]
    )

    def __post_init__(self) -> None:
        if self.target_column not in VALID_TARGETS:
            raise ValueError(
                f"TARGET must be one of {VALID_TARGETS}, got '{self.target_column}'."
            )

    @property
    def image_ref(self) -> str:
        """Full immutable-ish image reference ``name:tag``."""
        return f"{self.image_name}:{self.image_tag}"

    @property
    def local_model_path(self) -> Path:
        """Path to the saved local model artifact (joblib)."""
        return self.model_dir / "model.joblib"

    def to_public_dict(self) -> dict:
        """Serializable view (Paths -> str) for logging."""
        d = asdict(self)
        for k, v in d.items():
            if isinstance(v, Path):
                d[k] = str(v)
        return d


_CONFIG: Config | None = None


def get_config() -> Config:
    """Return a process-wide cached ``Config`` instance."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = Config()
    return _CONFIG
