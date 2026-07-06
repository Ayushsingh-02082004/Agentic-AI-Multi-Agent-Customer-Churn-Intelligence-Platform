from pydantic import BaseModel


class RetrievalContext(BaseModel):

    question: str

    context: str

    customer_ids: list[int]

    metadatas: list[dict]