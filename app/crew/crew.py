import dotenv

dotenv.load_dotenv()

from typing import Optional
from crewai import Crew, Agent, Task
from crewai.project import CrewBase, task, agent, crew
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from app.crew.schemas import JobList, RankedJobList, ChosenJob
from app.crew.tools import create_web_search_tool


@CrewBase
class JobSearchCrew:

    def __init__(self, resume_text: str, job_sites: Optional[list[str]] = None):
        self.resume_knowledge = StringKnowledgeSource(content=resume_text)
        self.web_search_tool = create_web_search_tool(domains=job_sites)

    @agent
    def job_search_agent(self):
        return Agent(
            config=self.agents_config["job_search_agent"],
            tools=[self.web_search_tool]
        )

    @agent
    def job_matching_agent(self):
        return Agent(
            config=self.agents_config["job_matching_agent"],
            knowledge_sources=[self.resume_knowledge]
        )

    @agent
    def resume_optimization_agent(self):
        return Agent(
            config=self.agents_config["resume_optimization_agent"],
            knowledge_sources=[self.resume_knowledge]
        )

    @agent
    def company_research_agent(self):
        return Agent(
            config=self.agents_config["company_research_agent"],
            tools=[self.web_search_tool],
            knowledge_sources=[self.resume_knowledge]
        )

    @agent
    def interview_prep_agent(self):
        return Agent(
            config=self.agents_config["interview_prep_agent"],
            knowledge_sources=[self.resume_knowledge]
        )

    @task
    def job_extraction_task(self):
        return Task(
            config=self.tasks_config["job_extraction_task"],
            output_pydantic=JobList
        )

    @task
    def job_matching_task(self):
        return Task(
            config=self.tasks_config["job_matching_task"],
            output_pydantic=RankedJobList
        )

    @task
    def job_selection_task(self):
        return Task(
            config=self.tasks_config["job_selection_task"],
            output_pydantic=ChosenJob
        )

    @task
    def resume_rewriting_task(self):
        return Task(
            config=self.tasks_config["resume_rewriting_task"]
        )

    @task
    def company_research_task(self):
        return Task(
            config=self.tasks_config["company_research_task"],
            context=[
                self.job_selection_task()
            ]
        )

    @task
    def interview_prep_task(self):
        return Task(
            config=self.tasks_config["interview_prep_task"],
            context=[
                self.job_selection_task(),
                self.resume_rewriting_task(),
                self.company_research_task(),
            ]
        )

    @crew
    def crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True
        )
