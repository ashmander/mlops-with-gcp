import logging
from datetime import datetime, timezone

from app.infrastructure.gcs_client import GCSClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class PredictionLogger:
    def __init__(self, gcs_client: GCSClient):
        self.gcs_client = gcs_client

    async def log_prediction(self, text: str, emotions: list) -> None:
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            emotion_labels = ",".join([e.label for e in emotions])
            line = f"{timestamp}\t{text}\t{emotion_labels}"

            bucket_name = settings.predictions_bucket
            blob_name = f"predicciones_{settings.app_env}.txt"

            self.gcs_client.append_to_blob(bucket_name, blob_name, line)
            logger.debug(f"Logged prediction for text: {text[:50]}...")
        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")
