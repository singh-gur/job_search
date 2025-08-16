from typing import List

from crewai import Agent, Crew, Process, Task
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

    @agent
    def job_searcher(self) -> Agent:
        return Agent(
            config=self.agents_config["job_searcher"],  # type: ignore[index]
            tools=[JobSpyTool()],
            verbose=True,
        )

    @agent
    def skills_analyzer(self) -> Agent:
        return Agent(config=self.agents_config["skills_analyzer"], verbose=True)  # type: ignore[index]

    @agent
    def resume_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["resume_writer"],  # type: ignore[index]
            tools=[ResumeGeneratorTool()],
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
    def generate_resume(self) -> Task:
        return Task(
            config=self.tasks_config["generate_resume"],  # type: ignore[index]
            agent=self.resume_writer(),
            context=[self.search_jobs(), self.analyze_skills_gap()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Job Search Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
