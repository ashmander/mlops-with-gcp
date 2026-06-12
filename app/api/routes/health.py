from fastapi import APIRouter, Depends

from app.core.config import settings
from app.domain.emotion_classifier import EmotionClassifier

router = APIRouter()


@router.get("/health")
async def health(classifier: EmotionClassifier = Depends()):
    return {
        "status": "ok",
        "env": settings.app_env,
        "model": settings.model_onnx_blob,
        "labels": len(classifier.labels),
    }
