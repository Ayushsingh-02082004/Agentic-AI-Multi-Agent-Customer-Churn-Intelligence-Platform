from backend.services.prediction_service import PredictionService
from backend.crews.prediction_crew import PredictionCrew

service = PredictionService()

customer = service.predict(10)

print("Prediction Service Output")
print(customer)

print("\n=====================\n")

result = PredictionCrew().crew().kickoff(
    inputs={
        "customer_data": customer
    }
)

print(result)

print("\n=====================\n")

print(result.pydantic)