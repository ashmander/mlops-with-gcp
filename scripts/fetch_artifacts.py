import os
import logging
from pathlib import Path

from app.core.config import settings
from app.infrastructure.gcs_client import GCSClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_artifacts():
    artifacts_dir = Path("model_artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    gcs_client = GCSClient(project_id=settings.gcp_project_id)

    prefix = f"{settings.model_prefix}/" if settings.model_prefix else ""

    artifacts = {
        "model_quantized.onnx": settings.model_onnx_blob,
        "config.json": "config.json",
        "tokenizer.json": "tokenizer.json",
        "tokenizer_config.json": "tokenizer_config.json",
    }

    for local_name, remote_name in artifacts.items():
        blob_name = f"{prefix}{remote_name}"
        try:
            logger.info(f"Downloading {blob_name} from {settings.model_bucket}...")
            data = gcs_client.download_blob(settings.model_bucket, blob_name)
            with open(artifacts_dir / local_name, "wb") as f:
                f.write(data)
            logger.info(f"Downloaded {local_name}")
        except Exception as e:
            logger.error(f"Failed to download {blob_name}: {e}")
            raise

    try:
        logger.info(
            f"Downloading {settings.test_data_blob} from {settings.test_data_bucket}..."
        )
        data = gcs_client.download_blob(
            settings.test_data_bucket, settings.test_data_blob
        )
        with open("goemotions_test.jsonl", "wb") as f:
            f.write(data)
        logger.info("Downloaded goemotions_test.jsonl")
    except Exception as e:
        logger.error(f"Failed to download test data: {e}")
        raise

    logger.info("All artifacts downloaded successfully")


if __name__ == "__main__":
    fetch_artifacts()
