from backend.vectorstore.chroma_service import ChromaService


class PredictionService:

    def predict(self, customer_id: int):

        db = ChromaService()
        res = db.get_customer_by_id(customer_id)

        if not res or not res.get("metadata"):
            return None

        metadata = res["metadata"]

        score = 0

        support_tickets = int(metadata.get("support_tickets", 0))
        contract = metadata.get("contract", "")
        tenure = int(metadata.get("tenure", 0))

        if support_tickets >= 4:
            score += 2

        if contract == "Month-to-Month":
            score += 2

        if tenure < 12:
            score += 2

        if score >= 5:

            risk = "High Risk"

        elif score >= 3:

            risk = "Medium Risk"

        else:

            risk = "Low Risk"

        return {

            "customer_id": customer_id,

            "risk": risk,

            "score": score,

            "support_tickets": support_tickets,

            "contract_type": contract,

            "tenure": tenure
        }