from app.domain.emotion_classifier import EmotionClassifier
from app.services.prediction_logger import PredictionLogger


class InferenceService:
    def __init__(self, classifier: EmotionClassifier, prediction_logger: PredictionLogger) -> None:
        self.classifier = classifier
        self.prediction_logger = prediction_logger

    def predict(self, text: str) -> list[dict[str, float | str]]:
        return self.classifier.predict(text)

    def log_prediction(self, text: str, emotions: list[dict[str, float | str]]) -> None:
        self.prediction_logger.log(text, emotions)
