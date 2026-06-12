# MLOps with GCP: Automatic ONNX Model Deployment

A complete CI/CD system for deploying ONNX emotion classification models to Google Cloud Platform (GCP) using FastAPI, GitHub Actions, and Cloud Run.

## Overview

This project implements an automated pipeline that:
- Tests new model versions on each push to `dev` or `prod`
- Builds Docker images with quantized ONNX models
- Deploys to Google Cloud Run with automatic endpoint updates
- Logs predictions to Cloud Storage
- Enforces branch policies (feature → dev → prod)

## Architecture

The system follows a **layered architecture**:

```
API Layer         → FastAPI routes (/health, /predict)
Service Layer     → Orchestration & logging
Domain Layer      → ONNX inference & schemas
Infrastructure    → GCS client & model loader
Core              → Configuration & logging
```

## Setup

### Prerequisites

- Python 3.12+
- `uv` package manager
- GCP project with Cloud Run, GCS, and Artifact Registry enabled
- Service account with appropriate IAM roles
- GitHub repository with branch protection rules

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <repo>
   cd mlops-with-gcp
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your GCP credentials and settings
   ```

3. **Run tests:**
   ```bash
   uv run python scripts/fetch_artifacts.py  # Download model from GCS
   uv run pytest -v
   ```

4. **Start development server:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

Visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### GET /health
Returns service status and model metadata.

**Response:**
```json
{
  "status": "ok",
  "env": "dev",
  "model": "model_quantized.onnx",
  "labels": 28
}
```

### POST /predict
Classify text into emotion categories.

**Request:**
```json
{
  "text": "I love this!"
}
```

**Response:**
```json
{
  "emotions": [
    {"label": "joy", "score": 0.92},
    {"label": "admiration", "score": 0.78}
  ],
  "env": "dev"
}
```

## Model

The system uses a **multi-label emotion classifier** based on GoEmotions (28 emotion categories). The model is:
- **Type:** RoBERTa-based transformer
- **Format:** ONNX (quantized for efficiency)
- **Input:** Text (variable length)
- **Output:** Sigmoid probabilities for each emotion label

### Model Artifacts

Four files are required in the GCS bucket:
- `model_quantized.onnx` — ONNX inference graph
- `config.json` — Model configuration (includes id2label mapping)
- `tokenizer.json` — Fast tokenizer
- `tokenizer_config.json` — Tokenizer configuration

These are **downloaded at CI/CD time** and **not stored in the repository**.

## Tests

Two test suites validate model correctness:

### T1: Model Response (test_model_response.py)
Verifies that the model returns valid predictions:
- Text input triggers inference
- All 28 emotions are scored in [0, 1]
- Scores are sorted descending
- Structure matches PredictResponse schema

### T2: Model Metric (test_model_metric.py)
Ensures quality threshold on test data:
- Inference on `goemotions_test.jsonl`
- Calculates F1 micro score
- Asserts F1 ≥ METRIC_THRESHOLD (default: 0.40)
- Blocks deployment if metric fails

## CI/CD Pipeline

### Branch Policy
```
feature/* → (PR to dev) → dev → (PR to prod) → prod
```

- PRs to `dev` only accepted from `feature/**` branches
- PRs to `prod` only accepted from `dev`
- Validated by `.github/workflows/branch-policy.yml`

### Deployment Flow

**On push to dev/prod:**

1. **Test Stage**
   - Checkout code
   - Install dependencies with `uv sync --frozen`
   - Authenticate to GCP via Workload Identity Federation
   - Download model artifacts from GCS
   - Run T1 + T2 tests

2. **Build Stage** (if tests pass)
   - Download model artifacts
   - Build Docker image (multi-stage with uv)
   - Push to Google Artifact Registry

3. **Deploy Stage**
   - Deploy image to Cloud Run
   - Update endpoint URL
   - Set environment variables per deployment

## GCP Configuration

### Required Resources

| Resource | Name | Purpose |
|----------|------|---------|
| GCS Bucket | `model` | Model artifacts |
| GCS Bucket | `data-test` | Test data (goemotions_test.jsonl) |
| GCS Bucket | `predictions` | Prediction logs |
| Artifact Registry | `models-repo` | Docker images |
| Cloud Run | `model-api-dev` | Dev endpoint |
| Cloud Run | `model-api-prod` | Prod endpoint |
| Service Account | `deployer` | CI/CD authentication (WIF) |

### Workload Identity Federation Setup

1. Enable required APIs: `iam.googleapis.com`, `sts.googleapis.com`, `run.googleapis.com`
2. Create WIF Pool + Provider for GitHub OIDC token
3. Bind pool to service account with attribute condition:
   ```
   assertion.repository == "org/repo" && 
   assertion.ref == "refs/heads/dev" || 
   assertion.ref == "refs/heads/prod"
   ```
4. Grant service account:
   - `roles/run.admin` (deploy to Cloud Run)
   - `roles/artifactregistry.writer` (push images)
   - `roles/storage.objectAdmin` (buckets)

### GitHub Secrets

```
GCP_PROJECT_ID         # GCP project ID
MODEL_BUCKET           # GCS bucket for models
MODEL_PREFIX           # Optional prefix in bucket
MODEL_ONNX_BLOB        # ONNX file name
TEST_DATA_BUCKET       # GCS bucket for test data
TEST_DATA_BLOB         # Test data file name
PREDICTIONS_BUCKET     # GCS bucket for logs
PROB_THRESHOLD         # Sigmoid threshold for emotion filtering
METRIC_THRESHOLD       # F1 minimum for tests
WIF_PROVIDER           # Workload Identity Provider resource name
WIF_SERVICE_ACCOUNT    # Service account email
```

## Prediction Logging

Each successful prediction is logged to `predicciones_{env}.txt` in the predictions bucket:

```
2026-06-11T10:00:00Z	I love this!	joy,admiration
2026-06-11T10:00:05Z	Good morning	neutral,contentment
```

Format: `{ISO8601_timestamp}\t{text}\t{emotion_labels_csv}`

## Troubleshooting

### Model download fails in CI
- Verify service account has `storage.objectViewer` on model bucket
- Check `MODEL_BUCKET` and artifact names in GitHub secrets
- Ensure WIF attribute condition includes current repo/branch

### Tests fail with F1 below threshold
- Verify model quantization is correct
- Check test data (goemotions_test.jsonl) format
- Adjust `METRIC_THRESHOLD` if model changed
- Run locally: `uv run pytest tests/test_model_metric.py -v`

### Cloud Run deployment timeout
- Check Docker image size (should be < 500MB)
- Verify model artifacts copied to image
- Increase timeout in GitHub Actions workflow

## Project Structure

```
.
├── .github/workflows/          # CI/CD pipelines
│   ├── branch-policy.yml       # PR source validation
│   ├── reusable-deploy.yml     # Shared test+build+deploy
│   ├── dev.yml                 # Trigger for dev pushes
│   └── prod.yml                # Trigger for prod pushes
├── app/
│   ├── main.py                 # FastAPI factory & dependency injection
│   ├── core/                   # Configuration & logging
│   ├── infrastructure/         # GCS & model loading
│   ├── domain/                 # ONNX classifier & schemas
│   ├── services/               # Inference & logging
│   └── api/routes/             # HTTP endpoints
├── tests/                      # Test suites (T1, T2)
├── scripts/                    # Utilities (fetch_artifacts.py)
├── Dockerfile                  # Multi-stage build
├── pyproject.toml              # Dependencies (uv)
├── .env.example                # Environment template
└── README.md                   # This file
```

## License

MIT
