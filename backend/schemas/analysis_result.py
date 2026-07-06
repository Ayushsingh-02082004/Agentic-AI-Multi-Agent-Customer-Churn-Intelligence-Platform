from pydantic import BaseModel

from backend.schemas.statistics import Statistics

class AnalysisResult(BaseModel):

    question: str

    summary: str

    statistics: dict

    evidence: list[str]

    reasoning: str

    customer_ids: list[int]

    confidence: float

    requires_prediction: bool

    requires_recommendation: bool