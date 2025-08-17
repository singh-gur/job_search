from os import getenv
from typing import List

from crewai import LLM, Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from job_search.tools.jobspy_tool import JobSpyTool
from job_search.tools.resume_generator_tool import ResumeGeneratorTool


@CrewBase
class JobSearchCrew:
    """Job Search Crew for finding jobs and generating personalized resumes"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self) -> None:
        self.llm = LLM(
            model=getenv("OPENAI_MODEL_NAME"),  # type: ignore[index]
            api_key=getenv("OPENAI_API_KEY"),  # type: ignore[index]
            api_base=getenv("OPENAI_API_BASE"),  # type: ignore[index]
        )

    @agent
    def job_searcher(self) -> Agent:
        return Agent(
            config=self.agents_config["job_searcher"],  # type: ignore[index]
            tools=[JobSpyTool()],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def skills_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config["skills_analyzer"],  # type: ignore[index]
            llm=self.llm,
            verbose=True,
        )

    @agent
    def resume_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["resume_writer"],  # type: ignore[index]
            tools=[ResumeGeneratorTool()],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def job_filter(self) -> Agent:
        return Agent(
            config=self.agents_config["job_filter"],  # type: ignore[index]
            llm=self.llm,
            verbose=True,
        )

    @task
    def search_jobs(self) -> Task:
        return Task(
            config=self.tasks_config["search_jobs"],  # type: ignore[index]
            agent=self.job_searcher(),
        )

    @task
    def analyze_skills_gap(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_skills_gap"],  # type: ignore[index]
            agent=self.skills_analyzer(),
            context=[self.search_jobs()],
        )

    @task
    def filter_jobs(self) -> Task:
        return Task(
            config=self.tasks_config["filter_jobs"],  # type: ignore[index]
            agent=self.job_filter(),
            context=[self.search_jobs()],
        )

    @task
    def generate_resume(self) -> Task:
        return Task(
            config=self.tasks_config["generate_resume"],  # type: ignore[index]
            agent=self.resume_writer(),
            context=[self.filter_jobs(), self.analyze_skills_gap()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Job Search Crew"""
        for a in self.agents:
            a.llm = self.llm
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
