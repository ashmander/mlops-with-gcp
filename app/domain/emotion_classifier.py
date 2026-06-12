import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer


class EmotionClassifier:
    def __init__(
        self,
        model_path: Path,
        tokenizer_path: Path,
        config_path: Path,
        max_length: int = 128,
        prob_threshold: float = 0.5,
        top_k: int = 5,
    ) -> None:
        self.model_path = model_path
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        self.max_length = max_length
        self.prob_threshold = prob_threshold
        self.top_k = top_k
        self.labels = self._load_labels(config_path)

    @staticmethod
    def _load_labels(config_path: Path) -> list[str]:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        id2label = config["id2label"]
        return [id2label[str(i)] for i in range(len(id2label))]

    def predict_scores(self, text: str) -> dict[str, float]:
        encoding = self.tokenizer.encode(text)
        ids = encoding.ids[: self.max_length]
        mask = encoding.attention_mask[: self.max_length]

        pad_id = self.tokenizer.token_to_id("<pad>")
        if pad_id is None:
            pad_id = 1

        padding = self.max_length - len(ids)
        if padding > 0:
            ids += [pad_id] * padding
            mask += [0] * padding

        inputs = {
            "input_ids": np.array([ids], dtype=np.int64),
            "attention_mask": np.array([mask], dtype=np.int64),
        }

        input_names = {item.name for item in self.session.get_inputs()}
        if "token_type_ids" in input_names:
            inputs["token_type_ids"] = np.zeros_like(inputs["input_ids"], dtype=np.int64)

        inputs = {key: value for key, value in inputs.items() if key in input_names}
        logits = self.session.run(None, inputs)[0][0]
        probabilities = 1.0 / (1.0 + np.exp(-logits))
        return {label: float(probabilities[index]) for index, label in enumerate(self.labels)}

    def predict(self, text: str) -> list[dict[str, float | str]]:
        scores = self.predict_scores(text)
        selected = [
            {"label": label, "score": score}
            for label, score in scores.items()
            if score >= self.prob_threshold
        ]
        if not selected:
            selected = [
                {"label": label, "score": score}
                for label, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)[: self.top_k]
            ]
        return sorted(selected, key=lambda item: item["score"], reverse=True)
