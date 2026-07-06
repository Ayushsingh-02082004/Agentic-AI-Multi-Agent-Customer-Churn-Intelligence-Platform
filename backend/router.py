from backend.schemas.query_plan import QueryPlan


class WorkflowRouter:

    def route(self, plan: QueryPlan):

        dag = {}

        if plan.needs_memory:
            dag["memory"] = []

        if plan.needs_data_analysis:
            dag["analysis"] = []

        if plan.needs_prediction:
            dag["prediction"] = ["analysis"]

        if plan.needs_recommendation:
            dag["recommendation"] = [
                "analysis",
                "prediction"
            ]

        if plan.needs_validation:
            dag["validation"] = [
                "analysis",
                "prediction",
                "recommendation"
            ]

        if plan.needs_report:
            dag["report"] = [
                "analysis",
                "prediction",
                "recommendation",
                "validation"
            ]

        return dag