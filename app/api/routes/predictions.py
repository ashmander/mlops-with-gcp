from fastapi import APIRouter, BackgroundTasks, Request

from app.domain.schemas import EmotionScore, PredictRequest, PredictResponse

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, background_tasks: BackgroundTasks, request: Request) -> PredictResponse:
    service = request.app.state.inference_service
    settings = request.app.state.settings
    emotions = service.predict(payload.text)
    background_tasks.add_task(service.log_prediction, payload.text, emotions)
    return PredictResponse(
        emotions=[EmotionScore(**emotion) for emotion in emotions],
        env=settings.app_env,
    )
