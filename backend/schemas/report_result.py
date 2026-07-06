from pydantic import BaseModel


class ReportResult(BaseModel):

    executive_summary: str

    key_findings: list[str]

    risk_assessment: str

    recommendations: list[str]

    validation_summary: str

    overall_confidence: float

    evidence: list[str]

    reasoning: str