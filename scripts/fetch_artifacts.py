import argparse
from pathlib import Path

from app.core.config import get_settings
from app.infrastructure.gcs_client import GcsClient
from app.infrastructure.model_loader import MODEL_FILES


def fetch_model(client: GcsClient, artifacts_dir: Path) -> None:
    settings = get_settings()
    for file_name in MODEL_FILES:
        client.download(
            settings.model_bucket,
            settings.model_blob_path(file_name),
            artifacts_dir / file_name,
        )


def fetch_test_data(client: GcsClient, destination: Path) -> None:
    settings = get_settings()
    client.download(settings.test_data_bucket, settings.test_data_blob, destination)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download model and test artifacts from GCS.")
    parser.add_argument("--skip-model", action="store_true")
    parser.add_argument("--skip-test-data", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    client = GcsClient()
    if not args.skip_model:
        fetch_model(client, settings.artifacts_dir)
    if not args.skip_test_data:
        fetch_test_data(client, settings.test_data_path)


if __name__ == "__main__":
    main()
