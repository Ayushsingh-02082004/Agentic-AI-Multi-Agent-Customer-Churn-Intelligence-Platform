import chromadb


class ChromaService:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="database/chroma"
        )

        self.collection = self.client.get_or_create_collection(
            name="customer_churn"
        )

    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas
    ):

        existing = self.collection.get()

        if len(existing["ids"]) > 0:

            self.collection.delete(
                ids=existing["ids"]
            )

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(
        self,
        embedding,
        k=5
    ):

        return self.collection.query(
            query_embeddings=[embedding],
            n_results=k
        )

    def get_all_metadata(self):
        result = self.collection.get(include=["metadatas"])
        return result["metadatas"]

    def get_customer_by_id(self, customer_id: int):
        result = self.collection.get(
            ids=[str(customer_id)],
            include=["documents", "metadatas"]
        )
        if result and result["ids"] and len(result["ids"]) > 0:
            return {
                "id": result["ids"][0],
                "document": result["documents"][0] if result["documents"] else None,
                "metadata": result["metadatas"][0] if result["metadatas"] else None
            }
        return None