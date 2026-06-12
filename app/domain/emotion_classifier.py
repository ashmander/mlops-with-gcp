import logging
import numpy as np
from scipy.special import expit as sigmoid

from app.domain.schemas import EmotionScore

logger = logging.getLogger(__name__)


class EmotionClassifier:
    def __init__(self, onnx_session, tokenizer, labels: list, prob_threshold: float):
        self.session = onnx_session
        self.tokenizer = tokenizer
        self.labels = labels
        self.prob_threshold = prob_threshold

    def classify(self, text: str) -> list[EmotionScore]:
        encoded = self.tokenizer.encode(text)
        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)

        inputs = {
            self.session.get_inputs()[0].name: input_ids,
            self.session.get_inputs()[1].name: attention_mask,
        }

        logits = self.session.run(None, inputs)[0]
        scores = sigmoid(logits[0])

        emotions = []
        for label, score in zip(self.labels, scores):
            if score >= self.prob_threshold:
                emotions.append(EmotionScore(label=label, score=float(score)))

        emotions.sort(key=lambda x: x.score, reverse=True)
        return emotions
