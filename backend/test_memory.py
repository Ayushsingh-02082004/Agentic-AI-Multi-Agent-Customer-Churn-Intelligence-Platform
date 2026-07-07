import uuid
from datetime import datetime

from backend.memory.memory_service import MemoryService
from backend.schemas.memory_record import MemoryRecord

record = MemoryRecord(

    session_id=str(uuid.uuid4()),

    user_query="Why are customers churning?",

    query_plan={

        "intent":"churn_analysis"

    },

    analysis={

        "churn_rate":50.2

    },

    prediction=None,

    recommendation=None,

    created_at=datetime.now()

)

memory = MemoryService()

memory.save(record)

print("Saved Successfully")

print(memory.history(record.session_id))