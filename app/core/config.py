from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "dev"
    gcp_project_id: str
    model_bucket: str = "model"
    model_prefix: str = ""
    model_onnx_blob: str = "model_quantized.onnx"
    test_data_bucket: str = "data-test"
    test_data_blob: str = "goemotions_test.jsonl"
    predictions_bucket: str = "predictions"
    prob_threshold: float = 0.5
    metric_threshold: float = 0.40

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
