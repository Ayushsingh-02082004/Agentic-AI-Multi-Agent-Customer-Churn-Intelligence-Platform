from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from backend.crews.config.llm import llm
from backend.schemas.validation_result import ValidationResult


@CrewBase
class ValidationCrew:

    agents_config = "config/validation_agents.yaml"
    tasks_config = "config/validation_tasks.yaml"

    @agent
    def validation_agent(self):

        return Agent(
            config=self.agents_config["validation_agent"],
            llm=llm,
            verbose=True
        )

    @task
    def validate_output(self):

        return Task(
            config=self.tasks_config["validate_output"],
            output_pydantic=ValidationResult
        )

    @crew
    def crew(self):

        return Crew(
            agents=[
                self.validation_agent()
            ],

            tasks=[
                self.validate_output()
            ],

            process=Process.sequential,

            verbose=True
        )