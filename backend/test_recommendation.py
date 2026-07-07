from backend.crews.recommendation_crew import RecommendationCrew

analysis = {
    "summary": "High churn among month-to-month customers."
}

prediction = {
    "customer_id": 10,
    "risk_level": "High Risk",
    "confidence": 94,
    "reasons": [
        "Short tenure",
        "Many support tickets"
    ]
}

result = RecommendationCrew().crew().kickoff(
    inputs={
        "analysis": analysis,
        "prediction": prediction
    }
)

print(result.pydantic)