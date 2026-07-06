from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from backend.crews.config.llm import llm
from backend.schemas.report_result import ReportResult


@CrewBase
class ReportingCrew:

    agents_config = "config/reporting_agents.yaml"
    tasks_config = "config/reporting_tasks.yaml"

    @agent
    def reporting_agent(self):

        return Agent(
            config=self.agents_config["reporting_agent"],
            llm=llm,
            verbose=True
        )

    @task
    def generate_report(self):

        return Task(
            config=self.tasks_config["generate_report"],
            output_pydantic=ReportResult
        )

    @crew
    def crew(self):

        return Crew(
            agents=[self.reporting_agent()],
            tasks=[self.generate_report()],
            process=Process.sequential,
            verbose=True
        )