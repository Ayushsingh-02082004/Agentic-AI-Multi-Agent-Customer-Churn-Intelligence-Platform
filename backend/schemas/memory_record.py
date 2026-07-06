from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class MemoryRecord(BaseModel):

    session_id: UUID

    user_query: str

    query_plan: dict

    retrieval_context: dict | None = None

    analysis: dict | None = None

    prediction: dict | None = None

    recommendation: dict | None = None

    validation: dict | None = None

    report: dict | None = None

    created_at: datetime

