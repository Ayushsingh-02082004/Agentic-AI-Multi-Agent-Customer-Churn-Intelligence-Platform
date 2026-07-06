#!/usr/bin/env python
import sys
import warnings
from backend.crews.customer_churn_crew import CustomerChurnCrew
from langsmith.integrations.otel import OtelSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from openinference.instrumentation.crewai import CrewAIInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor
import dotenv
from backend.orchestrator import WorkflowOrchestrator

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

dotenv.load_dotenv(".env")


# Configure OpenTelemetry
tracer_provider = trace.get_tracer_provider()
if not isinstance(tracer_provider, TracerProvider):
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)

# Add OtelSpanProcessor to the tracer provider
tracer_provider.add_span_processor(OtelSpanProcessor())

# Instrument CrewAI and OpenAI
CrewAIInstrumentor().instrument()
OpenAIInstrumentor().instrument()

def run():

    query = input("Ask your question: ")

    inputs = {
        "user_query": query
    }

    result = CustomerChurnCrew().crew().kickoff(
        inputs=inputs
    )

    plan = result.pydantic

    print("\n==============================")
    print("Query Plan")
    print("==============================\n")

    print(plan)

    orchestrator = WorkflowOrchestrator()

    results = orchestrator.run(plan)

    print("\n==============================")
    print("Workflow Results")
    print("==============================")

    for node, output in results.items():

        print(f"\n{node.upper()}")

        print("-" * 60)

        print(output)



if __name__ == "__main__":
    run()