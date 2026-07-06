from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from backend.crews.config.llm import llm
from backend.schemas.analysis_result import AnalysisResult


@CrewBase
class DataAnalysisCrew():

    agents_config = "config/data_agents.yaml"
    tasks_config = "config/data_tasks.yaml"

    @agent
    def data_analyst(self):

        return Agent(
            config=self.agents_config["data_analyst"],
            llm=llm,
            verbose=True
        )

    @task
    def analyze_data(self):

        return Task(
            config=self.tasks_config["analyze_data"],
            output_pydantic=AnalysisResult
        )

    @crew
    def crew(self):

        return Crew(
            agents=[self.data_analyst()],
            tasks=[self.analyze_data()],
            process=Process.sequential,
            verbose=True
        )