# MLOps with GCP: ONNX GoEmotions API

Sistema de despliegue automatico para un modelo ONNX de clasificacion de emociones en texto. La solucion usa FastAPI, GitHub Actions, Docker, Google Cloud Storage, Artifact Registry y Cloud Run.

## Arquitectura

- `app/api`: rutas HTTP de FastAPI.
- `app/services`: orquestacion de inferencia y logging.
- `app/domain`: clasificador ONNX, tokenizer y schemas Pydantic.
- `app/infrastructure`: adaptadores para GCS y carga de artefactos.
- `app/core`: configuracion centralizada.
- `tests`: pruebas del modelo usadas por CI/CD.
- `.github/workflows`: politica de ramas y despliegue reutilizable para `dev` y `prod`.

## Modelo y datos

El repositorio no versiona artefactos del modelo ni datos de prueba. Deben vivir en buckets de GCS:

```text
gs://model/
  model_quantized.onnx
  tokenizer.json
  tokenizer_config.json
  config.json

gs://data-test/
  goemotions_test.jsonl

gs://predictions/
  predicciones_dev.txt
  predicciones_prod.txt
```

Modelo usado: `SamLowe/roberta-base-go_emotions-onnx`, archivo `onnx/model_quantized.onnx`.

## API

```http
GET /health
POST /predict
```

Ejemplo:

```bash
curl -X POST "$URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"text":"I am so happy this worked!"}'
```

Cada llamada exitosa a `/predict` agrega una linea JSON a `predicciones_{APP_ENV}.txt` en el bucket de predicciones.

## Variables

Ver [.env.example](.env.example). Las mas importantes son:

- `APP_ENV`: `dev` o `prod`.
- `MODEL_BUCKET`: bucket con los 4 artefactos.
- `TEST_DATA_BUCKET`: bucket con `goemotions_test.jsonl`.
- `PREDICTIONS_BUCKET`: bucket de logs.
- `PROB_THRESHOLD`: umbral por etiqueta.
- `METRIC_THRESHOLD`: F1 micro minima para aprobar el despliegue.

## Pruebas

```bash
uv sync
uv run python scripts/fetch_artifacts.py
uv run pytest
```

Pruebas incluidas:

- El modelo responde con scores validos para una entrada de texto.
- El F1 micro sobre `goemotions_test.jsonl` es mayor o igual a `METRIC_THRESHOLD`.

## CI/CD

Flujo de ramas:

```text
feature/** -> dev -> prod
```

- Pull requests a `dev` solo desde `feature/**`.
- Pull requests a `prod` solo desde `dev`.
- Push a `dev` despliega `model-api-dev`.
- Push a `prod` despliega `model-api-prod`.

El workflow reutilizable ejecuta:

1. `test`: descarga artefactos y datos desde GCS, instala con `uv`, ejecuta `pytest`.
2. `build-and-deploy`: construye Docker, sube la imagen a Artifact Registry y actualiza Cloud Run.
3. `smoke-test`: consulta `/health` del endpoint desplegado.

## Variables de GitHub

Repository variables sugeridas:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `ARTIFACT_REPOSITORY`
- `MODEL_BUCKET`
- `MODEL_PREFIX`
- `TEST_DATA_BUCKET`
- `TEST_DATA_BLOB`
- `PREDICTIONS_BUCKET`
- `PROB_THRESHOLD`
- `METRIC_THRESHOLD`

Repository secrets:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_DEPLOYER_SERVICE_ACCOUNT`

## Docker

El build espera que CI haya descargado previamente los 4 artefactos en `model_artifacts/`.

```bash
docker build -t model-api .
docker run -p 8080:8080 --env-file .env model-api
```
