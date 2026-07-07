from backend.crews.reporting_crew import ReportingCrew


analysis = {
    "summary": "High churn among month-to-month customers.",
    "statistics": {
        "churn_rate": 50.2,
        "total_customers": 1000,
        "churned_customers": 502
    }
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
        "Resolve high volume of support tickets",
        "Improve onboarding for short tenure customers"
    ],
    "priority": "High Risk",
    "confidence": 94
}

validation = {
    "is_valid": True,
    "hallucination_detected": False,
    "confidence_verified": True,
    "numerical_validation": True,
    "evidence_available": True,
    "remarks": (
        "The analysis, prediction and recommendation are "
        "consistent and supported by the supplied evidence."
    )
}

result = ReportingCrew().crew().kickoff(
    inputs={
        "analysis": analysis,
        "prediction": prediction,
        "recommendation": recommendation,
        "validation": validation
    }
)

print("\n========== REPORT ==========\n")

print(result.pydantic)