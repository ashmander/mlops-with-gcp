import json
import logging
import io
import tempfile
import onnxruntime as ort
from tokenizers import Tokenizer

from app.infrastructure.gcs_client import GCSClient

logger = logging.getLogger(__name__)


class ModelLoader:
    @staticmethod
    def load_model(
        gcs_client: GCSClient,
        model_bucket: str,
        model_prefix: str,
        model_onnx_blob: str,
    ) -> tuple:
        """
        Load ONNX model, tokenizer, and config from GCS.
        Returns: (onnx_session, tokenizer, labels, config_dict)
        """
        prefix = f"{model_prefix}/" if model_prefix else ""

        logger.info("Loading model components from GCS...")

        onnx_path = f"{prefix}{model_onnx_blob}"
        config_path = f"{prefix}config.json"
        tokenizer_path = f"{prefix}tokenizer.json"

        onnx_data = gcs_client.download_blob(model_bucket, onnx_path)
        config_data = gcs_client.download_blob(model_bucket, config_path)
        tokenizer_data = gcs_client.download_blob(model_bucket, tokenizer_path)

        config_dict = json.loads(config_data)
        labels = list(config_dict.get("id2label", {}).values())

        with tempfile.NamedTemporaryFile(delete=False, suffix=".onnx") as tmp_onnx:
            tmp_onnx.write(onnx_data)
            tmp_onnx.flush()
            session = ort.InferenceSession(tmp_onnx.name)

        tokenizer = Tokenizer.from_buffer(tokenizer_data)

        logger.info(f"Model loaded successfully with {len(labels)} labels")
        return session, tokenizer, labels, config_dict
