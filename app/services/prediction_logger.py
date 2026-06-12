import json
from datetime import UTC, datetime

from app.core.config import Settings
from app.infrastructure.gcs_client import GcsClient


class PredictionLogger:
    def __init__(self, settings: Settings, gcs_client: GcsClient | None = None) -> None:
        self.settings = settings
        self.gcs_client = gcs_client

    def log(self, text: str, emotions: list[dict[str, float | str]]) -> None:
        payload = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "env": self.settings.app_env,
            "text": text,
            "emotions": emotions,
        }
        gcs_client = self.gcs_client or GcsClient()
        gcs_client.append_line(
            self.settings.predictions_bucket,
            self.settings.prediction_blob,
            json.dumps(payload, ensure_ascii=True),
        )
