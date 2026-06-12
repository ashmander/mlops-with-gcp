import uuid
from pathlib import Path

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
        main_blob = bucket.blob(blob_name)

        temp_blob = bucket.blob(f"{blob_name}.tmp.{uuid.uuid4().hex}")
        temp_blob.upload_from_string(f"{line}\n", content_type="text/plain; charset=utf-8")

        try:
            if main_blob.exists():
                main_blob.compose([main_blob, temp_blob])
            else:
                bucket.copy_blob(temp_blob, bucket, blob_name)
        finally:
            temp_blob.delete()
