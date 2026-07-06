from backend.vectorstore.chroma_service import ChromaService
from backend.vectorstore.retriever import Retriever


class DataAnalyst:

    def analyze(self, question: str):

        db = ChromaService()
        metadatas = db.get_all_metadata()

        total_customers = len(metadatas)
        if total_customers > 0:
            churned_customers = sum(1 for m in metadatas if m.get("churn") == 1)
            churn_rate = round((churned_customers / total_customers) * 100, 2)
            average_age = round(sum(m.get("age", 0) for m in metadatas) / total_customers, 2)
            average_tenure = round(sum(m.get("tenure", 0) for m in metadatas) / total_customers, 2)
        else:
            churned_customers = 0
            churn_rate = 0.0
            average_age = 0.0
            average_tenure = 0.0

        retrieved = Retriever().retrieve(
            question,
            k=5
        )

        customer_ids = []
        if retrieved and "metadatas" in retrieved and len(retrieved["metadatas"]) > 0:
            customer_ids = [int(m.get("customer_id")) for m in retrieved["metadatas"][0] if m.get("customer_id") is not None]

        return {

            "question": question,

            "statistics": {

                "total_customers": total_customers,

                "churned_customers": churned_customers,

                "churn_rate": churn_rate,

                "average_age": average_age,

                "average_tenure": average_tenure
            },

            "retrieved_customers":

                retrieved["documents"][0] if retrieved and "documents" in retrieved and len(retrieved["documents"]) > 0 else [],

            "customer_ids": customer_ids
        }