import logging
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.infrastructure.gcs_client import GCSClient
from app.infrastructure.model_loader import ModelLoader
from app.domain.emotion_classifier import EmotionClassifier
from app.services.inference_service import InferenceService
from app.services.prediction_logger import PredictionLogger
from app.api.routes import health, predictions

setup_logging()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="ONNX Emotion Classifier API",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    try:
        gcs_client = GCSClient(project_id=settings.gcp_project_id)
        session, tokenizer, labels, config_dict = ModelLoader.load_model(
            gcs_client=gcs_client,
            model_bucket=settings.model_bucket,
            model_prefix=settings.model_prefix,
            model_onnx_blob=settings.model_onnx_blob,
        )

        classifier = EmotionClassifier(
            onnx_session=session,
            tokenizer=tokenizer,
            labels=labels,
            prob_threshold=settings.prob_threshold,
        )

        logger_service = PredictionLogger(gcs_client=gcs_client)
        inference_service = InferenceService(
            classifier=classifier,
            logger_service=logger_service,
        )

        app.dependency_overrides[EmotionClassifier] = lambda: classifier
        app.dependency_overrides[InferenceService] = lambda: inference_service

        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        raise

    app.include_router(health.router)
    app.include_router(predictions.router)

    return app


app = create_app()
