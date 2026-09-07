# Jenkins CI

Jenkins runs **Continuous Integration** for this project. It does **not** deploy
to Kubernetes — that is Argo CD's job (GitOps CD).

## Pipeline stages

```
Checkout → Tooling check → Setup & Install → Lint → Unit Tests
        → Train Model → Evaluate/Quality Gate → Build Image
        → Image Validation → Push Image → Update Deployment Metadata
```

The quality gate stage fails the build when `r2 < MIN_R2` (default `0.80`), so a
weak model never gets promoted.

## Create the job

Jenkins is already running at http://localhost:8080 (do not reinstall).

1. **New Item → Pipeline** (or *Multibranch Pipeline*), name it `taxi-mlops-ci`.
2. **Pipeline → Definition:** *Pipeline script from SCM*.
3. **SCM:** Git, repository URL of this repo, branch `main`.
4. **Script Path:** `local-mlops-platform/jenkins/Jenkinsfile`.
5. Save and **Build Now**.

## Agent requirements

- `python3` + `venv` (required for tests/train).
- `docker` (required for Build/Push). If the agent has no Docker, those stages
  are skipped with a warning — run them on a Docker-capable node, or configure a
  Docker cloud agent. The pipeline **detects** this rather than failing silently.
- Network access to the local registry `localhost:5001`.

## CI vs CD boundary

```
Jenkins  ──►  tests, train, quality gate, build+push image   (CI ends here)
Argo CD  ──►  sync Kubernetes/KServe manifests from Git       (CD begins here)
```

CI ends when a validated image is pushed and the image tag is recorded. CD
begins when the GitOps manifests reference that image and Argo CD syncs them.
