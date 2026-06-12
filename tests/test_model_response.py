def test_model_responds_with_valid_scores(classifier):
    scores = classifier.predict_scores("I love this helpful solution.")

    assert len(scores) == 28
    assert "joy" in scores
    assert all(isinstance(score, float) for score in scores.values())
    assert all(0.0 <= score <= 1.0 for score in scores.values())
