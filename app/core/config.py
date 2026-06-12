from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="dev", pattern="^(dev|prod)$")
    gcp_project_id: str | None = None

    model_bucket: str = "model"
    model_prefix: str = ""
    model_onnx_blob: str = "model_quantized.onnx"
    tokenizer_blob: str = "tokenizer.json"
    tokenizer_config_blob: str = "tokenizer_config.json"
    config_blob: str = "config.json"

    test_data_bucket: str = "data-test"
    test_data_blob: str = "goemotions_test.jsonl"
    predictions_bucket: str = "predictions"

    artifacts_dir: Path = Path("model_artifacts")
    test_data_path: Path = Path("test_artifacts/goemotions_test.jsonl")

    prob_threshold: float = 0.5
    metric_threshold: float = 0.40
    max_length: int = 128
    top_k: int = 5

    @property
    def prediction_blob(self) -> str:
        return f"predicciones_{self.app_env}.txt"

    def model_blob_path(self, blob_name: str) -> str:
        return f"{self.model_prefix.strip('/')}/{blob_name}".strip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
