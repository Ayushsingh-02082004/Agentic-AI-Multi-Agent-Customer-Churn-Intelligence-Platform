from backend.vectorstore.embedding_service import EmbeddingService
from backend.vectorstore.chroma_service import ChromaService


class Retriever:

    def __init__(self):

        self.embedder = EmbeddingService()

        self.db = ChromaService()

    def retrieve(
        self,
        query: str,
        k: int = 5
    ):

        embedding = self.embedder.embed(
            query
        )

        return self.db.search(
            embedding,
            k
        )