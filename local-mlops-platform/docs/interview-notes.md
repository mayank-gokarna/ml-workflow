# Interview notes (MLOps architect perspective)

Concise Q&A for discussing this project.

### Why MLflow instead of just saving pickle files?
Pickle files lose context. MLflow records params, metrics, code version (git
SHA), environment, and the model artifact per run, and versions models in a
registry — making results reproducible, comparable, and auditable.

### Why Kubeflow if Jenkins already exists?
Jenkins orchestrates CI on build agents. Kubeflow orchestrates **ML training as
containerized, typed-artifact pipelines** on Kubernetes — scalable, portable,
and reproducible per step (preprocess/train/evaluate/register). They complement
each other.

### What problem does KServe solve?
Standardized, production-grade model serving on Kubernetes: a consistent
dataplane, autoscaling, canary rollouts, and pluggable runtimes — without
hand-writing a serving stack per model.

### Why Kubernetes for ML workloads?
A uniform declarative substrate for both training and serving: scheduling,
scaling, health/rollout management, resource isolation, and GPU support.

### Difference between MLflow and Kubeflow?
MLflow = tracking + registry (the *what* and *results*). Kubeflow = pipeline
orchestration (the *steps* that produce models). Often used together.

### Difference between MLflow Model Registry and KServe?
Registry = system of record for versioned models and their lifecycle. KServe =
runtime that serves a chosen version behind HTTP. Registry decides *which*;
KServe *runs* it.

### Why Jenkins and Argo CD together?
Separation of concerns: Jenkins = CI (test/train/build/push); Argo CD = CD via
GitOps (declarative, self-healing sync from Git). Neither does the other's job.

### Where does CI end and CD begin?
CI ends when a validated image is pushed and its tag recorded. CD begins when
GitOps manifests reference that tag and Argo CD syncs the cluster to match.

### How would you implement model rollback?
Point the serving manifest (or MLflow `@production` alias) back to the previous
image tag / model version and let Argo CD sync. Because it's GitOps, rollback is
a git revert.

### How would you implement canary deployment?
KServe canary: set `canaryTrafficPercent` on the InferenceService so a
percentage of traffic hits the new revision; ramp up as metrics stay healthy.

### How would you implement A/B testing?
Deploy two InferenceServices (or a KServe InferenceGraph) and split traffic,
tagging predictions with the model version for downstream metric comparison.

### How would you monitor model drift?
Log feature/prediction distributions (the server already exposes Prometheus
metrics). Compare live distributions to a training baseline (PSI/KS tests) and
alert on threshold breaches; feed back into retraining.

### How would you handle GPU workloads?
Request `nvidia.com/gpu` in the pod spec, schedule onto GPU nodes with the
device plugin, and use GPU-enabled serving runtimes/base images.

### How would you scale KServe?
Horizontal autoscaling on CPU/RPS (RawDeployment HPA, or Knative
concurrency-based autoscaling), plus replicas and resource tuning.

### How would you secure the model endpoint?
Network policies, an ingress/gateway with authN/authZ (JWT/mTLS), do not expose
externally by default, and use Kubernetes Secrets for credentials.

### How would you move this architecture to AWS?
See below.

## AWS mapping

| Local | AWS |
|---|---|
| Kind Kubernetes | Amazon EKS |
| `localhost:5001` registry | Amazon ECR |
| Local object storage | Amazon S3 |
| Local MLflow | MLflow on EC2/ECS + RDS + S3 artifacts |
| KServe | KServe on EKS |
| Jenkins | Jenkins / CodePipeline / GitHub Actions |
| Argo CD | Argo CD on EKS |
| Prometheus/Grafana | Amazon Managed Prometheus + Managed Grafana |

Where AWS services fit: **S3** (data/artifacts), **ECR** (images), **EKS**
(compute), **IAM** (access), **CloudWatch** (logs/metrics), **Managed
Prometheus** (metrics), **Secrets Manager** (credentials), **RDS** (MLflow
backend), **SageMaker** (managed training/serving alternative).
