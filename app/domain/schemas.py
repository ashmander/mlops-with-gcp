from pydantic import BaseModel


class PredictRequest(BaseModel):
    text: str


class EmotionScore(BaseModel):
    label: str
    score: float


class PredictResponse(BaseModel):
    emotions: list[EmotionScore]
    env: str
