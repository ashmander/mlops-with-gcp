import logging
from datetime import datetime
from google.cloud import storage

logger = logging.getLogger(__name__)


class GCSClient:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = storage.Client(project=project_id)

    def download_blob(self, bucket_name: str, blob_name: str) -> bytes:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        logger.info(f"Downloading {blob_name} from {bucket_name}")
        return blob.download_as_bytes()

    def upload_blob(self, bucket_name: str, blob_name: str, data: bytes) -> None:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        logger.info(f"Uploading {blob_name} to {bucket_name}")
        blob.upload_from_string(data)

    def append_to_blob(self, bucket_name: str, blob_name: str, line: str) -> None:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        try:
            existing_content = blob.download_as_text()
        except Exception:
            existing_content = ""

        new_content = existing_content + line + "\n"
        blob.upload_from_string(new_content)
        logger.info(f"Appended line to {blob_name} in {bucket_name}")
