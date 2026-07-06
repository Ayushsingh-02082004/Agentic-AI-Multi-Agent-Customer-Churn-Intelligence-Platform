import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from backend.router import WorkflowRouter
from backend.memory.memory_service import MemoryService
from backend.services.data_analysis_service import DataAnalyst
from backend.services.prediction_service import PredictionService
from backend.services.guardrail_service import GuardrailService

from backend.crews.data_analysis_crew import DataAnalysisCrew
from backend.crews.prediction_crew import PredictionCrew
from backend.crews.recommendation_crew import RecommendationCrew
from backend.crews.validation_crew import ValidationCrew
from backend.crews.reporting_crew import ReportingCrew


class WorkflowOrchestrator:

    def __init__(self):

        self.handlers = {
            "memory": self.run_memory,
            "analysis": self.run_analysis,
            "prediction": self.run_prediction,
            "recommendation": self.run_recommendation,
            "validation": self.run_validation,
            "report": self.run_reporting
        }

    def run(self, plan, session_id=None):

        dag = WorkflowRouter().route(plan)

        completed = {}

        while not all(node in completed for node in dag):

            executable = []

            for node, deps in dag.items():

                if node in completed:
                    continue

                if all(dep in completed for dep in deps):
                    executable.append(node)

            if not executable:
                raise RuntimeError(
                    "Workflow contains circular dependencies."
                )


            parallel = [
                node
                for node in executable
                if node in ("memory", "analysis")
            ]

            sequential = [
                node
                for node in executable
                if node not in ("memory", "analysis")
            ]

            if parallel:

                with ThreadPoolExecutor(
                    max_workers=len(parallel)
                ) as executor:

                    futures = {}

                    for node in parallel:

                        futures[node] = executor.submit(
                            self.handlers[node],
                            completed,
                            plan
                        )

                    for node, future in futures.items():

                        completed[node] = future.result()

            for node in sequential:

                completed[node] = self.handlers[node](
                    completed,
                    plan
                )

        # Post-execution: save memory to database if session_id is provided
        if session_id:
            try:
                from backend.schemas.memory_record import MemoryRecord
                
                record = MemoryRecord(
                    session_id=session_id if isinstance(session_id, uuid.UUID) else uuid.UUID(str(session_id)),
                    user_query=plan.user_query,
                    query_plan=plan.model_dump(),
                    retrieval_context=completed.get("retrieval_context"),
                    analysis=completed["analysis"].model_dump() if "analysis" in completed else None,
                    prediction=completed["prediction"].model_dump() if "prediction" in completed else None,
                    recommendation=completed["recommendation"].model_dump() if "recommendation" in completed else None,
                    validation=completed["validation"].model_dump() if "validation" in completed else None,
                    report=completed["report"].model_dump() if "report" in completed else None,
                    created_at=datetime.utcnow()
                )
                
                memory_service = MemoryService()
                memory_service.save(record)
                print(f"Workflow execution saved to database for session {session_id}")
            except Exception as e:
                print(f"Warning: Failed to save execution trace to memory: {e}")

        return completed

    # =========================================================

    def run_memory(self, completed, plan):

        return MemoryService()

    # =========================================================

    def run_analysis(self, completed, plan):

        analysis = DataAnalyst().analyze(
            plan.user_query
        )

        # Store in retrieval context
        completed["retrieval_context"] = {
            "question": analysis["question"],
            "statistics": analysis["statistics"],
            "retrieved_customers": analysis["retrieved_customers"],
            "customer_ids": analysis["customer_ids"]
        }

        result = DataAnalysisCrew().crew().kickoff(
            inputs={
                "question": analysis["question"],
                "statistics": analysis["statistics"],
                "retrieved_customers": analysis["retrieved_customers"]
            }
        )

        res_pydantic = result.pydantic
        GuardrailService.validate_output("analysis", res_pydantic)
        return res_pydantic

    # =========================================================

    def run_prediction(self, completed, plan):

        # Extract target customer ID dynamically
        customer_id = None
        if plan.customer_id is not None:
            customer_id = plan.customer_id
        elif "retrieval_context" in completed and completed["retrieval_context"].get("customer_ids"):
            customer_id = completed["retrieval_context"]["customer_ids"][0]
        else:
            customer_id = 10 # Default fallback

        customer = PredictionService().predict(
            customer_id=customer_id
        )

        if not customer:
            customer = {
                "customer_id": customer_id,
                "risk": "Unknown",
                "score": 0,
                "support_tickets": 0,
                "contract_type": "Unknown",
                "tenure": 0
            }

        result = PredictionCrew().crew().kickoff(
            inputs={
                "customer_data": customer
            }
        )

        res_pydantic = result.pydantic
        GuardrailService.validate_output("prediction", res_pydantic)
        return res_pydantic

    # =========================================================

    def run_recommendation(self, completed, plan):

        result = RecommendationCrew().crew().kickoff(
            inputs={
                "analysis": completed["analysis"].model_dump(),
                "prediction": completed["prediction"].model_dump()
            }
        )

        res_pydantic = result.pydantic
        GuardrailService.validate_output("recommendation", res_pydantic)
        return res_pydantic

    # =========================================================

    def run_validation(self, completed, plan):

        result = ValidationCrew().crew().kickoff(
            inputs={
                "analysis": completed["analysis"].model_dump(),
                "prediction": completed["prediction"].model_dump(),
                "recommendation": completed["recommendation"].model_dump()
            }
        )

        res_pydantic = result.pydantic
        GuardrailService.validate_output("validation", res_pydantic)
        return res_pydantic

    # =========================================================

    def run_reporting(self, completed, plan):

        result = ReportingCrew().crew().kickoff(
            inputs={
                "analysis": completed["analysis"].model_dump(),
                "prediction": completed["prediction"].model_dump(),
                "recommendation": completed["recommendation"].model_dump(),
                "validation": completed["validation"].model_dump()
            }
        )

        res_pydantic = result.pydantic
        GuardrailService.validate_output("report", res_pydantic)
        return res_pydantic