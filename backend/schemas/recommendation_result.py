from pydantic import BaseModel


class RecommendationResult(BaseModel):

    customer_id: int

    retention_actions: list[str]

    upsell_opportunities: list[str]

    service_improvements: list[str]

    priority: str

    confidence: float

    evidence: list[str]

    reasoning: str