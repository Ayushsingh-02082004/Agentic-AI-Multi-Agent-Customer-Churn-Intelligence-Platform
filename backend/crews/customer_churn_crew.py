from crewai import Agent, Crew, Process, Task
from backend.crews.config.llm import llm
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from backend.schemas.query_plan import QueryPlan


@CrewBase
class CustomerChurnCrew():
    """CustomerChurnCrew crew"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def query_understanding_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['query_understanding_agent'], # type: ignore[index]
            llm=llm,
            verbose=True
        )
    

    @task
    def understand_query(self) -> Task:
        return Task(
            config=self.tasks_config["understand_query"],
            output_pydantic=QueryPlan
        )

    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=[
                self.query_understanding_agent()
            ],

            tasks=[
                self.understand_query()
            ],

            process=Process.sequential,

            verbose=True
        )
