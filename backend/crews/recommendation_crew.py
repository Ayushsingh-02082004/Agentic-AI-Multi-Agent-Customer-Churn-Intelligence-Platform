from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task

from backend.crews.config.llm import llm
from backend.schemas.recommendation_result import RecommendationResult


@CrewBase
class RecommendationCrew:

    agents_config = "config/recommendation_agents.yaml"
    tasks_config = "config/recommendation_tasks.yaml"

    @agent
    def recommendation_agent(self):

        return Agent(
            config=self.agents_config["recommendation_agent"],
            llm=llm,
            verbose=True
        )

    @task
    def generate_recommendation(self):

        return Task(
            config=self.tasks_config["generate_recommendation"],
            output_pydantic=RecommendationResult
        )

    @crew
    def crew(self):

        return Crew(
            agents=[self.recommendation_agent()],
            tasks=[self.generate_recommendation()],
            process=Process.sequential,
            verbose=True
        )