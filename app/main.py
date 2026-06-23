from fastapi import FastAPI

from app.api.routes import health, predictions
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.infrastructure.model_loader import load_classifier
from app.services.inference_service import InferenceService
from app.services.prediction_logger import PredictionLogger

configure_logging()


def create_app() -> FastAPI:
    settings = get_settings()
    classifier = load_classifier(settings)
    prediction_logger = PredictionLogger(settings)
    inference_service = InferenceService(classifier, prediction_logger)

    app = FastAPI(title="ONNX GoEmotions API V2", version="0.1.0")
    app.state.settings = settings
    app.state.inference_service = inference_service
    app.include_router(health.router)
    app.include_router(predictions.router)
    return app


app = create_app()
