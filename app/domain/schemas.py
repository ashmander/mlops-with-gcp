from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class EmotionScore(BaseModel):
    label: str
    score: float


class PredictResponse(BaseModel):
    emotions: list[EmotionScore]
    env: str


class HealthResponse(BaseModel):
    status: str
    env: str
    model: str
    labels: int
