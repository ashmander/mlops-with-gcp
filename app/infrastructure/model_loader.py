from pathlib import Path

from app.core.config import Settings
from app.domain.emotion_classifier import EmotionClassifier
from app.infrastructure.gcs_client import GcsClient


MODEL_FILES = ("model_quantized.onnx", "tokenizer.json", "tokenizer_config.json", "config.json")


def ensure_model_artifacts(settings: Settings, gcs_client: GcsClient | None = None) -> None:
    missing_files = [name for name in MODEL_FILES if not (settings.artifacts_dir / name).exists()]
    if not missing_files:
        return

    if gcs_client is None:
        gcs_client = GcsClient()

    for file_name in missing_files:
        blob_name = settings.model_blob_path(file_name)
        gcs_client.download(settings.model_bucket, blob_name, settings.artifacts_dir / file_name)


def load_classifier(settings: Settings) -> EmotionClassifier:
    ensure_model_artifacts(settings)
    artifacts_dir: Path = settings.artifacts_dir
    return EmotionClassifier(
        model_path=artifacts_dir / settings.model_onnx_blob,
        tokenizer_path=artifacts_dir / settings.tokenizer_blob,
        config_path=artifacts_dir / settings.config_blob,
        max_length=settings.max_length,
        prob_threshold=settings.prob_threshold,
        top_k=settings.top_k,
    )
