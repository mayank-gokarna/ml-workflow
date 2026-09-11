"""NYC Taxi training pipeline (Kubeflow Pipelines v2).

Wires the components together and passes typed artifacts between steps:

    preprocess -> train -> evaluate -> (register, gated on evaluate)

Compile with:
    python kubeflow/pipeline.py            # -> iris_training_pipeline.yaml
or:
    make kfp-compile
"""

import os
import sys

from kfp import compiler, dsl
from kfp.dsl import Metrics, Model, Output

# Allow running as a plain script from the repo root.
sys.path.insert(0, os.path.dirname(__file__))

from components.evaluate import evaluate  # noqa: E402
from components.preprocess import preprocess  # noqa: E402
from components.train import train  # noqa: E402


@dsl.component(base_image="python:3.12-slim")
def register_model(model_in: dsl.Input[Model], registered: Output[Model], gate_passed: bool):
    """Placeholder 'register' step.

    In a full setup this pushes the model to the MLflow Model Registry. Here it
    only promotes the artifact when the quality gate passed, keeping the demo
    self-contained (no in-cluster MLflow dependency required to compile/run).
    """
    import shutil

    if not gate_passed:
        raise RuntimeError("Quality gate failed; refusing to register the model.")
    shutil.copyfile(model_in.path, registered.path)
    registered.metadata["registered"] = True
    print("register: model promoted (quality gate passed)")


@dsl.pipeline(
    name="nyc-taxi-training-pipeline",
    description="Preprocess -> Train -> Evaluate -> Register for NYC taxi fare prediction",
)
def iris_training_pipeline(
    n_samples: int = 20000,
    n_estimators: int = 100,
    min_r2: float = 0.80,
    target: str = "fare_amount",
):
    preprocess_task = preprocess(n_samples=n_samples, target=target)

    train_task = train(
        dataset=preprocess_task.outputs["dataset"],
        n_estimators=n_estimators,
    )

    evaluate_task = evaluate(
        dataset=preprocess_task.outputs["dataset"],
        model=train_task.outputs["model"],
        min_r2=min_r2,
    )

    register_model(
        model_in=train_task.outputs["model"],
        gate_passed=evaluate_task.outputs["Output"],
    )


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "nyc_taxi_pipeline.yaml")
    compiler.Compiler().compile(iris_training_pipeline, out)
    print(f"Compiled pipeline -> {out}")
