import json
import os
import sys
import subprocess
import logging
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.gcs_client import GCSClient
from app.infrastructure.model_loader import ModelLoader
from app.domain.emotion_classifier import EmotionClassifier
from app.core.config import settings

logger = logging.getLogger(__name__)


def pytest_configure(config):
    """Fetch artifacts from GCS before running tests."""
    artifacts_dir = Path("model_artifacts")

    if not artifacts_dir.exists() or not (artifacts_dir / "model_quantized.onnx").exists():
        logger.info("Artifacts not found locally. Fetching from GCS...")
        try:
            script_path = Path(__file__).parent.parent / "scripts" / "fetch_artifacts.py"
            subprocess.run(
                ["python", str(script_path)],
                check=True,
                cwd=Path(__file__).parent.parent,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to fetch artifacts: {e}")
            raise

    if not Path("goemotions_test.jsonl").exists():
        logger.warning("goemotions_test.jsonl not found. Tests may fail.")


@pytest.fixture
def emotion_classifier():
    """Create an EmotionClassifier instance for testing."""
    gcs_client = GCSClient(project_id=settings.gcp_project_id)

    session, tokenizer, labels, config_dict = ModelLoader.load_model(
        gcs_client=gcs_client,
        model_bucket=settings.model_bucket,
        model_prefix=settings.model_prefix,
        model_onnx_blob=settings.model_onnx_blob,
    )

    classifier = EmotionClassifier(
        onnx_session=session,
        tokenizer=tokenizer,
        labels=labels,
        prob_threshold=settings.prob_threshold,
    )

    return classifier


@pytest.fixture
def test_data():
    """Load test data from goemotions_test.jsonl."""
    test_file = Path("goemotions_test.jsonl")
    if not test_file.exists():
        pytest.skip("goemotions_test.jsonl not found")

    data = []
    with open(test_file, "r") as f:
        for line in f:
            data.append(json.loads(line))

    return data
