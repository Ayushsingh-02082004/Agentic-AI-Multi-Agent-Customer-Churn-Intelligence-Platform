from enum import Enum
from pydantic import BaseModel


class RiskLevel(str, Enum):
    LOW = "Low Risk"
    MEDIUM = "Medium Risk"
    HIGH = "High Risk"


class PredictionResult(BaseModel):

    customer_id: int

    risk_level: RiskLevel

    confidence: float

    reasons: list[str]

    evidence: list[str]

    reasoning: str

    requires_recommendation: bool