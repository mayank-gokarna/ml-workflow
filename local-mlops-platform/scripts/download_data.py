#!/usr/bin/env python3
"""Download a small sample of real NYC TLC yellow-taxi data.

Fetches one monthly parquet file from the official NYC TLC bucket, cleans it,
engineers the same feature schema used by the synthetic generator, samples it
down to a manageable size, and writes it to ``data/raw/nyc_taxi_sample.parquet``.

Usage:
    python scripts/download_data.py --year 2023 --month 1 --rows 20000

Then train on it with:
    USE_REAL_DATA=true python -m mlops_demo.train
"""

from __future__ import annotations

import argparse
import logging
import sys
import tempfile
import urllib.request
from pathlib import Path

import pandas as pd

# Make the package importable when run as a plain script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mlops_demo.config import get_config  # noqa: E402
from mlops_demo.data import SAMPLE_FILENAME  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("download_data")

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def build_url(year: int, month: int) -> str:
    return f"{BASE_URL}/yellow_tripdata_{year:04d}-{month:02d}.parquet"


def clean_and_engineer(frame: pd.DataFrame) -> pd.DataFrame:
    """Reduce raw TLC columns to the canonical feature + target schema."""
    df = frame.rename(
        columns={
            "PULocationID": "pu_location_id",
            "DOLocationID": "do_location_id",
        }
    )
    pickup = pd.to_datetime(df["tpep_pickup_datetime"])
    dropoff = pd.to_datetime(df["tpep_dropoff_datetime"])
    df["pickup_hour"] = pickup.dt.hour
    df["pickup_dayofweek"] = pickup.dt.dayofweek
    df["trip_duration"] = (dropoff - pickup).dt.total_seconds() / 60.0

    cols = [
        "trip_distance",
        "passenger_count",
        "pickup_hour",
        "pickup_dayofweek",
        "pu_location_id",
        "do_location_id",
        "fare_amount",
        "trip_duration",
    ]
    df = df[cols].copy()

    # Basic sanity filtering to drop bad rows.
    df = df[
        (df["fare_amount"] > 0)
        & (df["fare_amount"] < 250)
        & (df["trip_distance"] > 0)
        & (df["trip_distance"] < 100)
        & (df["passenger_count"] > 0)
        & (df["trip_duration"] >= 1)
        & (df["trip_duration"] <= 180)
    ]
    df["passenger_count"] = df["passenger_count"].astype(int)
    return df.dropna()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Download NYC TLC taxi sample")
    parser.add_argument("--year", type=int, default=2023)
    parser.add_argument("--month", type=int, default=1)
    parser.add_argument("--rows", type=int, default=20000, help="rows to sample")
    args = parser.parse_args(argv)

    config = get_config()
    url = build_url(args.year, args.month)
    out_dir = Path(config.data_raw_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / SAMPLE_FILENAME

    logger.info("Downloading %s", url)
    try:
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
            urllib.request.urlretrieve(url, tmp.name)
            raw = pd.read_parquet(tmp.name)
    except Exception as exc:  # noqa: BLE001 - clear guidance on network failure
        logger.error("Download/read failed: %s", exc)
        logger.error(
            "Check connectivity or pick another year/month. You can still train "
            "offline with the synthetic generator (unset USE_REAL_DATA)."
        )
        return 1

    logger.info("Raw rows: %d. Cleaning + engineering features...", len(raw))
    clean = clean_and_engineer(raw)
    if len(clean) > args.rows:
        clean = clean.sample(n=args.rows, random_state=config.random_state)
    clean = clean.reset_index(drop=True)

    clean.to_parquet(out_path, index=False)
    logger.info("Wrote %d rows -> %s", len(clean), out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
