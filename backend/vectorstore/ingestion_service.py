import pandas as pd

from backend.vectorstore.embedding_service import EmbeddingService
from backend.vectorstore.chroma_service import ChromaService


class IngestionService:

    def __init__(self):

        self.embedder = EmbeddingService()

        self.db = ChromaService()

    def ingest(self):

        df = pd.read_csv(
            "datasets/BNPParibas_Data.csv"
        )

        ids = []
        docs = []
        embeddings = []
        metadata = []

        for _, row in df.iterrows():

            business_features = []

            if row.support_tickets >= 4:
                business_features.append(
                    "High customer support usage"
                )

            if row.tenure_months < 12:
                business_features.append(
                    "Short customer tenure"
                )

            if row.contract_type == "Month-to-Month":
                business_features.append(
                    "Flexible monthly contract"
                )

            if row.monthly_charges > 80:
                business_features.append(
                    "High monthly billing"
                )

            if row.churn == 1:
                business_features.append(
                    "Customer already churned"
                )
            else:
                business_features.append(
                    "Customer retained"
                )

            document = f"""
            Customer Profile

            Customer ID: {row.customer_id}

            Age: {row.age}

            Tenure: {row.tenure_months} months

            Monthly Charges: {row.monthly_charges}

            Total Charges: {row.total_charges}

            Contract Type: {row.contract_type}

            Internet Service: {row.internet_service}

            Support Tickets: {row.support_tickets}

            Payment Method: {row.payment_method}

            Churn Status: {"Yes" if row.churn else "No"}

            Business Features:

            {chr(10).join("- " + f for f in business_features)}
            """
            

            ids.append(
                str(row.customer_id)
            )

            docs.append(
                document
            )

            embeddings.append(
                self.embedder.embed(
                    document
                )
            )

            metadata.append(
                {
                    "customer_id": int(row.customer_id),
                    "age": int(row.age),
                    "tenure": int(row.tenure_months),
                    "support_tickets": int(row.support_tickets),
                    "contract": str(row.contract_type),
                    "internet_service": str(row.internet_service),
                    "monthly_charges": float(row.monthly_charges),
                    "churn": int(row.churn)
                }
            )

        self.db.add_documents(
            ids,
            docs,
            embeddings,
            metadata
        )

        print("Vector Database Created Successfully")