import pytest


def test_model_response(emotion_classifier):
    """T1: Model responds to text input with valid emotion scores."""
    text = "I love this!"
    emotions = emotion_classifier.classify(text)

    assert len(emotions) > 0, "Model should return at least one emotion"
    assert len(emotions) <= len(emotion_classifier.labels), \
        "Model should return at most number of labels"

    for emotion in emotions:
        assert hasattr(emotion, "label"), "Each emotion should have a label"
        assert hasattr(emotion, "score"), "Each emotion should have a score"
        assert 0 <= emotion.score <= 1, "Score should be between 0 and 1"
        assert emotion.label in emotion_classifier.labels, \
            f"Label {emotion.label} should be in the label list"

    scores = [e.score for e in emotions]
    assert scores == sorted(scores, reverse=True), "Emotions should be sorted by score descending"
