import pytest
from sklearn.metrics import f1_score


def test_model_metric(emotion_classifier, test_data):
    """T2: Model achieves F1 micro >= METRIC_THRESHOLD on test data."""
    from app.core.config import settings

    y_true_all = []
    y_pred_all = []

    for sample in test_data:
        text = sample.get("text", "")
        true_labels = set(sample.get("labels", []))

        if not text:
            continue

        emotions = emotion_classifier.classify(text)
        predicted_labels = {e.label for e in emotions}

        for label in emotion_classifier.labels:
            y_true_all.append(1 if label in true_labels else 0)
            y_pred_all.append(1 if label in predicted_labels else 0)

    if not y_true_all:
        pytest.skip("No test data available")

    f1_micro = f1_score(y_true_all, y_pred_all, average="micro", zero_division=0)

    assert f1_micro >= settings.metric_threshold, \
        f"F1 micro {f1_micro:.4f} is below threshold {settings.metric_threshold}"
