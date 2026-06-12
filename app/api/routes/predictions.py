from fastapi import APIRouter, Depends

from app.domain.schemas import PredictRequest, PredictResponse
from app.services.inference_service import InferenceService

router = APIRouter()


@router.post("/predict")
async def predict(
    request: PredictRequest,
    service: InferenceService = Depends(),
) -> PredictResponse:
    return await service.predict(request)
