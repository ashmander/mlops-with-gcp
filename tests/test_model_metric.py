def _micro_f1(y_true: list[set[str]], y_pred: list[set[str]]) -> float:
    true_positive = false_positive = false_negative = 0
    for true_labels, predicted_labels in zip(y_true, y_pred, strict=True):
        true_positive += len(true_labels & predicted_labels)
        false_positive += len(predicted_labels - true_labels)
        false_negative += len(true_labels - predicted_labels)

    denominator = (2 * true_positive) + false_positive + false_negative
    if denominator == 0:
        return 0.0
    return (2 * true_positive) / denominator


def test_model_micro_f1_above_threshold(classifier, test_examples, settings):
    expected = []
    predicted = []

    for example in test_examples:
        scores = classifier.predict_scores(example["text"])
        labels = {label for label, score in scores.items() if score >= settings.prob_threshold}
        if not labels:
            labels = {max(scores.items(), key=lambda item: item[1])[0]}
        expected.append(set(example["expected_labels"]))
        predicted.append(labels)

    f1 = _micro_f1(expected, predicted)
    assert f1 >= settings.metric_threshold, f"micro F1 {f1:.3f} < {settings.metric_threshold:.3f}"
