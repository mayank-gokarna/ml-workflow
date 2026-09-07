"""Prediction utilities.

Loads the trained model (local joblib artifact by default, or from MLflow if
a model URI is provided) and turns raw feature vectors / records into
predictions. The same feature ordering used in training is enforced here.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List, Sequence, Union

import numpy as np
import pandas as pd

from .config import Config, get_config

logger = logging.getLogger(__name__)

Instance = Union[Sequence[float], dict]


class ModelNotFoundError(FileNotFoundError):
    """Raised when no trained model artifact can be located."""


def load_model(model_path: Union[str, Path, None] = None, config: Config | None = None):
    """Load the trained model from a local joblib artifact.

    ``model_path`` overrides the configured default. Raises
    ``ModelNotFoundError`` with guidance if the artifact is missing.
    """
    import joblib

    config = config or get_config()
    path = Path(model_path) if model_path else config.local_model_path
    if not path.exists():
        raise ModelNotFoundError(
            f"No model artifact at {path}. Train first with "
            "`python -m mlops_demo.train` (or `make train`)."
        )
    logger.info("Loading model from %s", path)
    return joblib.load(path)


def _to_dataframe(instances: Iterable[Instance], config: Config) -> pd.DataFrame:
    """Normalize a batch of records/vectors into an ordered feature frame."""
    rows: List[dict] = []
    for i, inst in enumerate(instances):
        if isinstance(inst, dict):
            missing = [f for f in config.feature_names if f not in inst]
            if missing:
                raise ValueError(
                    f"Instance {i} is missing features: {missing}. "
                    f"Required: {config.feature_names}"
                )
            rows.append({f: inst[f] for f in config.feature_names})
        else:
            values = list(inst)
            if len(values) != len(config.feature_names):
                raise ValueError(
                    f"Instance {i} has {len(values)} values but "
                    f"{len(config.feature_names)} features are required: "
                    f"{config.feature_names}"
                )
            rows.append(dict(zip(config.feature_names, values)))
    return pd.DataFrame(rows, columns=config.feature_names)


def predict(
    instances: Iterable[Instance],
    model=None,
    config: Config | None = None,
) -> List[float]:
    """Return predictions for a batch of feature vectors or records.

    Each instance is either an ordered list matching ``feature_names`` or a
    dict keyed by feature name.
    """
    config = config or get_config()
    if model is None:
        model = load_model(config=config)

    frame = _to_dataframe(instances, config)
    preds = np.asarray(model.predict(frame), dtype=float)
    logger.info("Produced %d prediction(s)", len(preds))
    return preds.tolist()

