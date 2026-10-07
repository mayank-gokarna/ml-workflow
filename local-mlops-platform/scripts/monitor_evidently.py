#!/usr/bin/env python3
"""Evidently monitoring for the NYC Taxi model.

Builds a *reference* dataset (the training distribution) and a *current* dataset
(a deliberately drifted sample), scores both with the trained model, and runs
Evidently Data Drift + Regression Performance + Data Summary reports. Results are
saved as a standalone HTML report and added to a local Evidently *workspace* that
the Evidently UI can serve.

Usage:
    python scripts/monitor_evidently.py              # reference vs drifted current
    python scripts/monitor_evidently.py --no-drift   # current == fresh in-distribution

Then launch the UI:
    evidently ui --workspace ./monitoring/evidently_workspace --port 8000
    # open http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

# Make the package importable when run as a plain script.
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mlops_demo.config import get_config  # noqa: E402
from mlops_demo.data import generate_synthetic_data  # noqa: E402
from mlops_demo.predict import load_model  # noqa: E402

from evidently import DataDefinition, Dataset, Regression, Report  # noqa: E402
from evidently.presets import (  # noqa: E402
    DataDriftPreset,
    DataSummaryPreset,
    RegressionPreset,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("monitor")

OUT_DIR = Path(__file__).resolve().parents[1] / "monitoring"
WORKSPACE_DIR = OUT_DIR / "evidently_workspace"
PROJECT_NAME = "NYC Taxi Model Monitoring"


def _inject_drift(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Simulate real-world drift: longer trips, more rush-hour, more passengers."""
    df = df.copy()
    df["trip_distance"] = np.clip(df["trip_distance"] * rng.uniform(1.25, 1.6), 0.3, 60)
    # Shift pickups toward evening rush hours.
    df["pickup_hour"] = np.clip(df["pickup_hour"] + rng.integers(2, 6, len(df)), 0, 23)
    df["passenger_count"] = np.clip(df["passenger_count"] + 1, 1, 6)
    return df


def _score(df: pd.DataFrame, model, features) -> pd.DataFrame:
    """Add the model's prediction column."""
    df = df.copy()
    df["prediction"] = model.predict(df[features])
    return df


def build_datasets(drift: bool):
    config = get_config()
    features = list(config.feature_names)
    target = config.target_column  # 'fare_amount'
    model = load_model(config=config)

    # Reference = the training distribution.
    ref = generate_synthetic_data(n_samples=4000, config=config)
    # Current = a fresh sample, optionally drifted.
    rng = np.random.default_rng(123)
    cur = generate_synthetic_data(n_samples=4000, config=config)
    if drift:
        cur = _inject_drift(cur, rng)

    ref = _score(ref, model, features)
    cur = _score(cur, model, features)

    definition = DataDefinition(
        numerical_columns=features + [target, "prediction"],
        regression=[Regression(target=target, prediction="prediction")],
    )
    keep = features + [target, "prediction"]
    ref_ds = Dataset.from_pandas(ref[keep], data_definition=definition)
    cur_ds = Dataset.from_pandas(cur[keep], data_definition=definition)
    return ref_ds, cur_ds


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evidently monitoring for the taxi model")
    parser.add_argument("--no-drift", action="store_true", help="do not inject drift")
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ref_ds, cur_ds = build_datasets(drift=not args.no_drift)

    report = Report(
        metrics=[DataDriftPreset(), RegressionPreset(), DataSummaryPreset()],
        include_tests=True,
    )
    logger.info("Running Evidently report (drift=%s)...", not args.no_drift)
    run = report.run(current_data=cur_ds, reference_data=ref_ds)

    html_path = OUT_DIR / "evidently_report.html"
    run.save_html(str(html_path))
    logger.info("Saved standalone report -> %s", html_path)

    # Add the run to a local workspace so the Evidently UI can show it over time.
    from evidently.ui.workspace import Workspace

    ws = Workspace.create(str(WORKSPACE_DIR))
    projects = ws.search_project(PROJECT_NAME)
    project = projects[0] if projects else ws.create_project(PROJECT_NAME)
    ws.add_run(project.id, run)
    logger.info("Added run to Evidently workspace -> %s", WORKSPACE_DIR)

    print("\nNext:")
    print(f"  evidently ui --workspace {WORKSPACE_DIR} --port 8000")
    print("  open http://127.0.0.1:8000")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
