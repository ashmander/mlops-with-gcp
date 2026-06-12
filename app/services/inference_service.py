import asyncio
import logging

from app.domain.emotion_classifier import EmotionClassifier
from app.domain.schemas import PredictRequest, PredictResponse
from app.services.prediction_logger import PredictionLogger
from app.core.config import settings

logger = logging.getLogger(__name__)


class InferenceService:
    def __init__(self, classifier: EmotionClassifier, logger_service: PredictionLogger):
        self.classifier = classifier
        self.logger_service = logger_service

    async def predict(self, request: PredictRequest) -> PredictResponse:
        emotions = self.classifier.classify(request.text)

        asyncio.create_task(self.logger_service.log_prediction(request.text, emotions))

        return PredictResponse(emotions=emotions, env=settings.app_env)
