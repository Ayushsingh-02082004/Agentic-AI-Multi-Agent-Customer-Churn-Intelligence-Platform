from pydantic import BaseModel


class ValidationResult(BaseModel):

    is_valid: bool

    hallucination_detected: bool

    confidence_verified: bool

    numerical_validation: bool

    evidence_available: bool

    remarks: str

    confidence: float

    evidence: list[str]

    reasoning: str