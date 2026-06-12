from fastapi import APIRouter, Request

from app.domain.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    classifier = request.app.state.inference_service.classifier
    return HealthResponse(
        status="ok",
        env=settings.app_env,
        model=settings.model_onnx_blob,
        labels=len(classifier.labels),
    )
