from pathlib import Path

from google.api_core.exceptions import NotFound
from google.cloud import storage


class GcsClient:
    def __init__(self) -> None:
        self.client = storage.Client()

    def download(self, bucket_name: str, blob_name: str, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        bucket = self.client.bucket(bucket_name)
        bucket.blob(blob_name).download_to_filename(destination)
        return destination

    def append_line(self, bucket_name: str, blob_name: str, line: str) -> None:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        try:
            current = blob.download_as_text(encoding="utf-8")
        except NotFound:
            current = ""
        blob.upload_from_string(f"{current}{line}\n", content_type="text/plain; charset=utf-8")
