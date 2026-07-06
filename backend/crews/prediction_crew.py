from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from backend.crews.config.llm import llm
from backend.schemas.prediction_result import PredictionResult


@CrewBase
class PredictionCrew():

    agents_config = "config/prediction_agents.yaml"
    tasks_config = "config/prediction_tasks.yaml"

    @agent
    def prediction_agent(self):

        return Agent(
            config=self.agents_config["prediction_agent"],
            llm=llm,
            verbose=True
        )

    @task
    def predict_customer(self):

        return Task(
            config=self.tasks_config["predict_customer"],
            output_pydantic=PredictionResult
        )

    @crew
    def crew(self):

        return Crew(
            agents=[self.prediction_agent()],
            tasks=[self.predict_customer()],
            process=Process.sequential,
            verbose=True
        )