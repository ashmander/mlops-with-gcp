import json
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.infrastructure.model_loader import load_classifier


@pytest.fixture(scope="session")
def settings():
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture(scope="session")
def classifier(settings):
    return load_classifier(settings)


@pytest.fixture(scope="session")
def test_examples(settings):
    path: Path = settings.test_data_path
    if not path.exists():
        raise FileNotFoundError(
            f"Test data not found at {path}. Run scripts/fetch_artifacts.py before pytest."
        )
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
