# MLOps with GCP: ONNX GoEmotions API

Sistema de despliegue automatico para un modelo ONNX existente. El proyecto expone una API con FastAPI para clasificar emociones en texto y usa GitHub Actions para probar, construir y desplegar el contenedor en GCP.

La solucion esta pensada para dos ambientes:

- `dev`: endpoint de pruebas.
- `prod`: endpoint productivo.

Un push a `dev` o `prod` ejecuta el pipeline `test -> build-and-deploy -> smoke-test`.

## Caso de uso

El modelo recibe un texto libre y predice emociones usando GoEmotions, un clasificador multi-etiqueta basado en RoBERTa exportado a ONNX.

Ejemplo de entrada:

```json
{
  "text": "I am so happy this worked!"
}
```

Ejemplo de salida:

```json
{
  "emotions": [
    {
      "label": "joy",
      "score": 0.92
    }
  ],
  "env": "dev"
}
```

## Arquitectura

```text
app/
  api/              Rutas HTTP de FastAPI
  services/         Orquestacion de inferencia y logging
  domain/           Inferencia ONNX, tokenizer y schemas
  infrastructure/   GCS y carga de artefactos
  core/             Configuracion y logging
tests/              Pruebas usadas por CI/CD
scripts/            Utilidades de descarga de artefactos
.github/workflows/  Workflows de PR, ramas y despliegue
```

Separacion por capas:

- API: valida request/response y expone `/health` y `/predict`.
- Services: coordina el clasificador y el log de predicciones.
- Domain: contiene la logica pura de inferencia.
- Infrastructure: conoce GCS y descarga/sube archivos.
- Core: centraliza variables de entorno.

## Modelo y datos

El repositorio no debe contener el modelo ni los datos de prueba. Estos archivos se descargan desde GCS durante el pipeline.

Estructura esperada:

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

Modelo usado:

```text
SamLowe/roberta-base-go_emotions-onnx
onnx/model_quantized.onnx
```

El archivo `config.json` contiene el mapa `id2label`, por eso las etiquetas no estan hardcodeadas en el codigo.

## API

### `GET /health`

Retorna el estado del servicio, ambiente actual, modelo y cantidad de etiquetas.

```bash
curl http://localhost:8080/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "env": "dev",
  "model": "model_quantized.onnx",
  "labels": 28
}
```

### `POST /predict`

Clasifica emociones para un texto.

```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"I am so happy this worked!\"}"
```

Cada llamada exitosa intenta agregar una linea JSON a:

```text
gs://predictions/predicciones_{APP_ENV}.txt
```

En local, si no tienes credenciales de GCP, `/health` funciona normalmente y `/predict` calcula la prediccion, pero puede fallar al ejecutar el logging en background si no hay acceso a GCS.

## Uso local

### 1. Instalar `uv`

En Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
$env:Path = "C:\Users\$env:USERNAME\.local\bin;$env:Path"
```

En macOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Instalar dependencias

```bash
uv sync
```

### 3. Preparar variables locales

Copia el ejemplo:

```bash
cp .env.example .env
```

En PowerShell:

```powershell
Copy-Item .env.example .env
```

Para desarrollo local puedes usar estos valores:

```text
APP_ENV=dev
ARTIFACTS_DIR=model_artifacts
TEST_DATA_PATH=test_artifacts/goemotions_test.jsonl
PROB_THRESHOLD=0.5
METRIC_THRESHOLD=0.40
```

### 4. Agregar artefactos del modelo

Crea esta carpeta local:

```text
model_artifacts/
```

Debe contener:

```text
model_quantized.onnx
tokenizer.json
tokenizer_config.json
config.json
```

Estos archivos estan ignorados por Git y no se suben al repositorio.

Si ya tienes los archivos en otra carpeta, copialos a `model_artifacts/`.

### 5. Agregar datos de prueba

Crea esta carpeta local:

```text
test_artifacts/
```

Debe contener:

```text
goemotions_test.jsonl
```

Este archivo tambien esta ignorado por Git.

### 6. Ejecutar pruebas

```bash
uv run pytest
```

Las pruebas hacen dos validaciones:

- El modelo responde con scores validos entre `0` y `1`.
- El F1 micro sobre `goemotions_test.jsonl` es mayor o igual a `METRIC_THRESHOLD`.

### 7. Levantar la API localmente

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Luego abre:

```text
http://localhost:8080/docs
```

Tambien puedes probar:

```bash
curl http://localhost:8080/health
```

## Descargar artefactos desde GCS

Cuando ya existan los buckets y tengas credenciales de GCP configuradas, puedes descargar los artefactos con:

```bash
uv run python scripts/fetch_artifacts.py
```

Solo modelo:

```bash
uv run python scripts/fetch_artifacts.py --skip-test-data
```

Solo datos de prueba:

```bash
uv run python scripts/fetch_artifacts.py --skip-model
```

## Docker local

El build espera que los artefactos ya existan en `model_artifacts/`.

```bash
docker build -t model-api .
docker run -p 8080:8080 --env-file .env model-api
```

Probar:

```bash
curl http://localhost:8080/health
```

## CI/CD

Flujo de ramas:

```text
feature/** -> dev -> prod
```

Reglas:

- PR a `dev`: solo desde `feature/**`.
- PR a `prod`: solo desde `dev`.
- Push a `dev`: despliega `model-api-dev`.
- Push a `prod`: despliega `model-api-prod`.

Workflows:

- `branch-policy.yml`: valida el origen del PR.
- `pull-request-test.yml`: corre pruebas antes del merge.
- `dev.yml`: despliegue automatico al ambiente `dev`.
- `prod.yml`: despliegue automatico al ambiente `prod`.
- `reusable-deploy.yml`: workflow reutilizable con `test`, `build-and-deploy` y `smoke-test`.

## Variables de GitHub

Repository variables:

```text
GCP_PROJECT_ID
GCP_REGION
ARTIFACT_REPOSITORY
MODEL_BUCKET
MODEL_PREFIX
TEST_DATA_BUCKET
TEST_DATA_BLOB
PREDICTIONS_BUCKET
PROB_THRESHOLD
METRIC_THRESHOLD
```

Repository secrets:

```text
GCP_WORKLOAD_IDENTITY_PROVIDER
GCP_DEPLOYER_SERVICE_ACCOUNT
```

## Recursos esperados en GCP

- GCS bucket `model` para artefactos del modelo.
- GCS bucket `data-test` para `goemotions_test.jsonl`.
- GCS bucket `predictions` para logs de predicciones.
- Artifact Registry para imagenes Docker.
- Cloud Run con dos servicios:
  - `model-api-dev`
  - `model-api-prod`
- Workload Identity Federation para autenticar GitHub Actions sin llaves JSON.

## Archivos ignorados

Estos archivos/carpetas no se versionan:

```text
.env
.venv/
model_artifacts/
test_artifacts/
```

Esto cumple el requisito de no subir el modelo ONNX ni los datos de prueba al repositorio.

## Limitacion conocida

GCS no tiene append nativo. Para el curso se usa un patron simple read-modify-write sobre `predicciones_{env}.txt`. Es suficiente para baja concurrencia, pero en produccion convendria escribir un objeto por prediccion o usar Pub/Sub + BigQuery.
