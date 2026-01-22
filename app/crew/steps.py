"""
Step-by-step crew execution for incremental processing.
"""
import dotenv
dotenv.load_dotenv()

from typing import Optional
from crewai import Crew, Agent, Task
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

from app.crew.tools import create_web_search_tool
from app.crew.schemas import JobList, RankedJobList, ChosenJob

import yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).parent / "config"


def load_config(filename: str) -> dict:
    with open(CONFIG_DIR / filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class JobSearchStep:
    """Step 1: Search for job postings."""

    def __init__(self, job_sites: Optional[list[str]] = None):
        self.agents_config = load_config("agents.yaml")
        self.tasks_config = load_config("tasks.yaml")
        self.web_search_tool = create_web_search_tool(domains=job_sites)

    def run(self, level: str, position: str, location: str) -> JobList:
        agent = Agent(
            config=self.agents_config["job_search_agent"],
            tools=[self.web_search_tool]
        )

        task = Task(
            config=self.tasks_config["job_extraction_task"],
            agent=agent,
            output_pydantic=JobList
        )

        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        result = crew.kickoff(inputs={
            "level": level,
            "position": position,
            "location": location,
        })

        return result.pydantic


class JobMatchStep:
    """Step 2: Match and rank jobs against resume, then select best one."""

    def __init__(self, resume_text: str):
        self.agents_config = load_config("agents.yaml")
        self.tasks_config = load_config("tasks.yaml")
        self.resume_knowledge = StringKnowledgeSource(content=resume_text)

    def run(self, jobs: JobList) -> tuple[RankedJobList, ChosenJob]:
        agent = Agent(
            config=self.agents_config["job_matching_agent"],
            knowledge_sources=[self.resume_knowledge]
        )

        matching_task = Task(
            config=self.tasks_config["job_matching_task"],
            agent=agent,
            output_pydantic=RankedJobList
        )

        selection_task = Task(
            config=self.tasks_config["job_selection_task"],
            agent=agent,
            output_pydantic=ChosenJob,
            context=[matching_task]
        )

        crew = Crew(agents=[agent], tasks=[matching_task, selection_task], verbose=True)
        result = crew.kickoff(inputs={"jobs": jobs.model_dump_json()})

        ranked_jobs = result.tasks_output[0].pydantic
        chosen_job = result.tasks_output[1].pydantic

        return ranked_jobs, chosen_job


class ResumeOptimizeStep:
    """Step 3: Optimize resume for the chosen job."""

    def __init__(self, resume_text: str):
        self.agents_config = load_config("agents.yaml")
        self.tasks_config = load_config("tasks.yaml")
        self.resume_knowledge = StringKnowledgeSource(content=resume_text)

    def run(self, chosen_job: ChosenJob) -> str:
        agent = Agent(
            config=self.agents_config["resume_optimization_agent"],
            knowledge_sources=[self.resume_knowledge]
        )

        task = Task(
            config=self.tasks_config["resume_rewriting_task"],
            agent=agent,
        )

        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        result = crew.kickoff(inputs={"chosen_job": chosen_job.model_dump_json()})

        return result.raw


class CompanyResearchStep:
    """Step 4: Research the company."""

    def __init__(self, resume_text: str):
        self.agents_config = load_config("agents.yaml")
        self.tasks_config = load_config("tasks.yaml")
        self.resume_knowledge = StringKnowledgeSource(content=resume_text)
        self.web_search_tool = create_web_search_tool()

    def run(self, chosen_job: ChosenJob) -> str:
        agent = Agent(
            config=self.agents_config["company_research_agent"],
            tools=[self.web_search_tool],
            knowledge_sources=[self.resume_knowledge]
        )

        task = Task(
            config=self.tasks_config["company_research_task"],
            agent=agent,
        )

        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        result = crew.kickoff(inputs={"chosen_job": chosen_job.model_dump_json()})

        return result.raw


class InterviewPrepStep:
    """Step 5: Prepare for interview."""

    def __init__(self, resume_text: str):
        self.agents_config = load_config("agents.yaml")
        self.tasks_config = load_config("tasks.yaml")
        self.resume_knowledge = StringKnowledgeSource(content=resume_text)

    def run(self, chosen_job: ChosenJob, rewritten_resume: str, company_research: str) -> str:
        agent = Agent(
            config=self.agents_config["interview_prep_agent"],
            knowledge_sources=[self.resume_knowledge]
        )

        task = Task(
            config=self.tasks_config["interview_prep_task"],
            agent=agent,
        )

        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        result = crew.kickoff(inputs={
            "chosen_job": chosen_job.model_dump_json(),
            "rewritten_resume": rewritten_resume,
            "company_research": company_research,
        })

        return result.raw
