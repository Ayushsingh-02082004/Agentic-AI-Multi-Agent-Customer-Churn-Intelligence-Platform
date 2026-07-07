from backend.crews.validation_crew import ValidationCrew


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

recommendation = {
    "customer_id": 10,
    "retention_actions": [
        "Convert month-to-month customer to a longer-term contract"
    ],
    "upsell_opportunities": [
        "Offer long-term plan incentives"
    ],
    "service_improvements": [
        "Resolve high volume of support tickets"
    ],
    "priority": "High Risk",
    "confidence": 94
}

result = ValidationCrew().crew().kickoff(
    inputs={
        "analysis": analysis,
        "prediction": prediction,
        "recommendation": recommendation
    }
)

print(result.pydantic)