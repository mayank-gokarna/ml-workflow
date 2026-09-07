# NYC Taxi MLOps demo — developer convenience targets.
# On Windows, run these from WSL (recommended) or use the documented
# PowerShell equivalents in docs/local-setup.md.

PYTHON ?= python3
VENV   ?= .venv
BIN    := $(VENV)/bin
PY     := $(BIN)/python
PIP    := $(BIN)/pip

IMAGE_NAME ?= localhost:5001/taxi-fare-predictor
IMAGE_TAG  ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo latest)
IMAGE_REF  := $(IMAGE_NAME):$(IMAGE_TAG)
NAMESPACE  ?= mlops

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

$(VENV): ## Create the virtualenv
	$(PYTHON) -m venv $(VENV)

.PHONY: install
install: $(VENV) ## Install runtime + dev deps (editable)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

.PHONY: lint
lint: ## Lint with ruff
	$(BIN)/ruff check src tests

.PHONY: test
test: ## Run unit tests
	$(PY) -m pytest -m "not integration and not e2e"

.PHONY: test-all
test-all: ## Run all tests including integration
	$(PY) -m pytest

.PHONY: train
train: ## Train the model (logs to MLflow if available)
	$(PY) -m mlops_demo.train

.PHONY: evaluate
evaluate: ## Evaluate the saved model against fresh data
	$(PY) -m mlops_demo.evaluate

.PHONY: mlflow
mlflow: ## Start a local MLflow tracking server (sqlite backend)
	$(BIN)/mlflow server --host 127.0.0.1 --port 5000 \
		--backend-store-uri sqlite:///mlflow.db \
		--default-artifact-root ./mlruns

.PHONY: data
data: ## Download a real NYC TLC sample into data/raw
	$(PY) scripts/download_data.py

.PHONY: kfp-compile
kfp-compile: ## Compile the Kubeflow pipeline to YAML
	$(PY) kubeflow/pipeline.py

.PHONY: docker-build
docker-build: ## Build the training/serving image
	docker build -f docker/Dockerfile -t $(IMAGE_REF) .

.PHONY: docker-build-kserve
docker-build-kserve: ## Build the KServe serving image (bakes model; train first)
	docker build -f docker/Dockerfile.kserve -t $(IMAGE_NAME)-serve:$(IMAGE_TAG) .

.PHONY: serve
serve: ## Run the model server locally on :8080
	$(BIN)/uvicorn mlops_demo.serve:app --host 0.0.0.0 --port 8080

.PHONY: docker-run
docker-run: ## Run training inside the container
	docker run --rm $(IMAGE_REF)

.PHONY: docker-push
docker-push: ## Push images to the local kind registry
	docker push $(IMAGE_REF)
	docker push $(IMAGE_NAME)-serve:$(IMAGE_TAG)

.PHONY: k8s-install
k8s-install: ## Create the mlops namespace + base config
	kubectl apply -f kubernetes/namespace.yaml
	kubectl apply -f kubernetes/configmap.yaml

.PHONY: kserve-deploy
kserve-deploy: ## Deploy the KServe InferenceService
	kubectl apply -f kserve/namespace.yaml
	kubectl apply -f kserve/inference-service.yaml

.PHONY: kserve-test
kserve-test: ## Send a test inference request
	./scripts/test_endpoint.sh

.PHONY: clean
clean: ## Remove build/artifact/cache files
	rm -rf $(VENV) build dist *.egg-info src/*.egg-info \
		.pytest_cache .ruff_cache .coverage htmlcov \
		models mlruns mlflow.db
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
