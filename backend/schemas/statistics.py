from pydantic import BaseModel

class Statistics(BaseModel):
    total_customers: int
    churned_customers: int
    churn_rate: float
    avg_age: float