from enum import Enum
from pydantic import BaseModel, Field


class Intent(str, Enum):
    CHURN_ANALYSIS = "churn_analysis"
    CUSTOMER_SEGMENTATION = "customer_segmentation"
    CHURN_PREDICTION = "churn_prediction"
    RETENTION_RECOMMENDATION = "retention_recommendation"
    REPORT_GENERATION = "report_generation"
    UNKNOWN = "unknown"


class QueryPlan(BaseModel):

    user_query: str

    intent: Intent = Field(
        description="Detected user intent"
    )

    business_goal: str

    needs_memory: bool

    needs_data_analysis: bool

    needs_prediction: bool

    needs_recommendation: bool

    needs_validation: bool

    needs_report: bool

    customer_id: int | None = Field(
        default=None,
        description="Specific customer ID target if mentioned in the query"
    )