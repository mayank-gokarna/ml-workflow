"""FastAPI model server implementing the KServe V1 dataplane.

Endpoints:
- ``GET  /v1/models/{name}``          -> readiness (KServe model-ready probe)
- ``POST /v1/models/{name}:predict``  -> {"instances": [[...]]} -> {"predictions": [...]}
- ``GET  /healthz``                   -> liveness
- ``GET  /metrics``                   -> Prometheus metrics

The model is loaded once at startup from the local joblib artifact (baked into
the serving image or mounted). Prometheus metrics expose prediction count,
latency and the served model version for basic ML monitoring.
"""

from __future__ import annotations

import logging
import os
import time
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel

from .config import get_config
from .predict import load_model, predict

logger = logging.getLogger(__name__)

CONFIG = get_config()
MODEL_NAME = CONFIG.model_name
MODEL_VERSION = os.getenv("MODEL_VERSION", "local")

# --- Prometheus metrics ---
PREDICTION_COUNT = Counter(
    "model_prediction_total",
    "Total number of predictions served",
    ["model", "model_version"],
)
PREDICTION_ERRORS = Counter(
    "model_prediction_errors_total",
    "Total number of failed prediction requests",
    ["model"],
)
PREDICTION_LATENCY = Histogram(
    "model_prediction_latency_seconds",
    "Prediction request latency in seconds",
    ["model"],
)
LAST_PREDICTION = Gauge(
    "model_last_prediction_value",
    "Value of the most recent prediction",
    ["model"],
)

app = FastAPI(title=f"{MODEL_NAME} server", version=MODEL_VERSION)
_MODEL = None


class PredictRequest(BaseModel):
    instances: List[list]


def get_model():
    """Lazily load and cache the model artifact."""
    global _MODEL
    if _MODEL is None:
        _MODEL = load_model(config=CONFIG)
        logger.info("Model '%s' (version %s) loaded", MODEL_NAME, MODEL_VERSION)
    return _MODEL


@app.on_event("startup")
def _startup() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    try:
        get_model()
    except Exception as exc:  # noqa: BLE001 - surface load failure in logs, stay up for probes
        logger.error("Failed to load model at startup: %s", exc)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/v1/models/{name}")
def model_ready(name: str) -> dict:
    ready = _MODEL is not None or name == MODEL_NAME
    return {"name": name, "ready": ready}


@app.post("/v1/models/{name}:predict")
def predict_v1(name: str, request: PredictRequest) -> dict:
    if name != MODEL_NAME:
        raise HTTPException(status_code=404, detail=f"Model '{name}' not found")
    if not request.instances:
        raise HTTPException(status_code=400, detail="'instances' must be non-empty")

    start = time.perf_counter()
    try:
        model = get_model()
        preds = predict(request.instances, model=model, config=CONFIG)
    except Exception as exc:  # noqa: BLE001 - convert to a clean 400 for the client
        PREDICTION_ERRORS.labels(MODEL_NAME).inc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    PREDICTION_LATENCY.labels(MODEL_NAME).observe(time.perf_counter() - start)
    PREDICTION_COUNT.labels(MODEL_NAME, MODEL_VERSION).inc(len(preds))
    LAST_PREDICTION.labels(MODEL_NAME).set(preds[-1])
    return {"predictions": preds}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
