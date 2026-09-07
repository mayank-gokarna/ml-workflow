# Architecture

## Overview

`local-mlops-platform` demonstrates a full ML lifecycle for **NYC Taxi fare /
trip-time prediction** on a local Kubernetes (Kind) cluster.

```mermaid
flowchart LR
    Dev[Developer] --> Git[GitHub]
    Git --> Jenkins[Jenkins CI]
    Jenkins --> Test[Unit Tests]
    Jenkins --> Train[ML Training]
    Train --> MLflow[MLflow Tracking + Registry]
    Train --> Image[Serving Image]
    Image --> Registry[(localhost:5001)]
    Git --> Argo[Argo CD]
    Argo --> K8s[Kubernetes / Kind]
    Registry --> K8s
    K8s --> KServe[KServe InferenceService]
    KServe --> API[Inference API]
    K8s --> Mon[Prometheus + Grafana]
```

## Component responsibilities

| Component | Responsibility | Classification |
|---|---|---|
| `src/mlops_demo` | Data, training, evaluation, prediction, serving | Application code |
| MLflow | Experiment tracking + model registry | Platform service |
| Kubeflow Pipelines | Orchestrated, containerized training steps | Pipeline code |
| Docker | Reproducible images (train + serve) | Infrastructure |
| Kind + `kubernetes/` | Cluster + namespace/config | Infrastructure |
| KServe (`kserve/`) | Model serving runtime | Deployment config |
| Jenkins (`jenkins/`) | CI: test, train, gate, build, push | Pipeline config |
| Argo CD (`argocd/`, `gitops/`) | GitOps CD | Deployment config |
| Prometheus/Grafana | Metrics + dashboards | Observability |

## Data flow

```mermaid
flowchart LR
    D[Synthetic or NYC TLC data] --> F[Feature engineering]
    F --> S[Train/test split]
    S --> M[RandomForestRegressor]
    M --> E[Metrics: rmse/mae/r2/mape]
    E --> G{r2 >= MIN_R2?}
    G -- yes --> R[Register + serve]
    G -- no --> X[Fail / no promotion]
```

## Model lifecycle

```mermaid
flowchart LR
    None --> Candidate --> Staging --> Production
```

A run that passes the quality gate registers a new **version** of
`taxi-fare-predictor`. Promotion between stages uses MLflow aliases
(`@staging`, `@production`).

## CI/CD flow

```mermaid
flowchart TB
    push[git push] --> J[Jenkins CI]
    J --> t[tests] --> tr[train] --> ml[MLflow] --> b[build image] --> p[push image]
    p --> gitops[GitOps manifest/image tag]
    gitops --> a[Argo CD] --> k[Kubernetes] --> ks[KServe] --> inf[Inference endpoint]
```

**CI ends** at "push image" (+ recording the tag). **CD begins** when Argo CD
syncs the Git manifests.

## Why each technology?

- **Why MLflow?** Reproducible tracking of params/metrics/artifacts and a
  registry of versioned models — far better than ad-hoc pickle files.
- **Why Kubeflow?** Portable, containerized, multi-step pipelines with typed
  artifacts; scales training beyond a single script.
- **Why KServe?** Standardized, scalable model serving on Kubernetes with a
  consistent dataplane (`/v1/models/{name}:predict`).
- **Why Jenkins?** Mature CI already present; runs tests/train/build/push.
- **Why Argo CD?** Declarative GitOps CD — the cluster continuously converges to
  the Git-defined desired state (prune + self-heal).
- **Why Kubernetes?** Uniform, declarative substrate for training and serving
  workloads with scaling, health management, and rollout control.

## GitHub Actions alternative

GitHub Actions could replace the Jenkins CI stages (tests → train → build →
push). Argo CD would remain for CD. This project uses Jenkins + Argo CD
deliberately to demonstrate that toolchain.
