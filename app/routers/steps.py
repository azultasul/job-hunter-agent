"""
Step-by-step API endpoints for incremental crew execution.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import json

from app.crew.steps import (
    JobSearchStep,
    JobMatchStep,
    ResumeOptimizeStep,
    CompanyResearchStep,
    InterviewPrepStep,
)
from app.crew.schemas import JobList, RankedJobList, ChosenJob
from app.utils.pdf import extract_text_from_pdf

router = APIRouter(prefix="/crew/step", tags=["crew-steps"])


@router.post("/search")
async def step_search(
    level: str = Form(...),
    position: str = Form(...),
    location: str = Form(...),
    job_sites: Optional[str] = Form(None),
):
    """
    Step 1: Search for job postings.

    Returns a list of jobs matching the criteria.
    """
    sites_list = _parse_job_sites(job_sites)

    try:
        step = JobSearchStep(job_sites=sites_list)
        jobs = step.run(level=level, position=position, location=location)
        return {"jobs": jobs.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match")
async def step_match(
    jobs: str = Form(...),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
):
    """
    Step 2: Match jobs against resume and select the best one.

    Input: jobs (JSON from step 1)
    Returns: ranked_jobs and chosen_job
    """
    resume_content = await _get_resume_content(resume_text, resume_file)
    jobs_data = _parse_jobs(jobs)

    try:
        step = JobMatchStep(resume_text=resume_content)
        ranked_jobs, chosen_job = step.run(jobs=jobs_data)
        return {
            "ranked_jobs": ranked_jobs.model_dump(),
            "chosen_job": chosen_job.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume")
async def step_resume(
    chosen_job: str = Form(...),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
):
    """
    Step 3: Optimize resume for the chosen job.

    Input: chosen_job (JSON from step 2)
    Returns: rewritten_resume (markdown)
    """
    resume_content = await _get_resume_content(resume_text, resume_file)
    chosen_job_data = _parse_chosen_job(chosen_job)

    try:
        step = ResumeOptimizeStep(resume_text=resume_content)
        rewritten_resume = step.run(chosen_job=chosen_job_data)
        return {"rewritten_resume": rewritten_resume}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research")
async def step_research(
    chosen_job: str = Form(...),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
):
    """
    Step 4: Research the company.

    Input: chosen_job (JSON from step 2)
    Returns: company_research (markdown)
    """
    resume_content = await _get_resume_content(resume_text, resume_file)
    chosen_job_data = _parse_chosen_job(chosen_job)

    try:
        step = CompanyResearchStep(resume_text=resume_content)
        company_research = step.run(chosen_job=chosen_job_data)
        return {"company_research": company_research}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview")
async def step_interview(
    chosen_job: str = Form(...),
    rewritten_resume: str = Form(...),
    company_research: str = Form(...),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
):
    """
    Step 5: Prepare for interview.

    Input: chosen_job, rewritten_resume, company_research (from previous steps)
    Returns: interview_prep (markdown)
    """
    resume_content = await _get_resume_content(resume_text, resume_file)
    chosen_job_data = _parse_chosen_job(chosen_job)

    try:
        step = InterviewPrepStep(resume_text=resume_content)
        interview_prep = step.run(
            chosen_job=chosen_job_data,
            rewritten_resume=rewritten_resume,
            company_research=company_research,
        )
        return {"interview_prep": interview_prep}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions

def _parse_job_sites(job_sites: Optional[str]) -> Optional[list[str]]:
    if not job_sites:
        return None
    try:
        sites = json.loads(job_sites)
        return sites if isinstance(sites, list) else None
    except json.JSONDecodeError:
        return None


def _parse_jobs(jobs_json: str) -> JobList:
    try:
        data = json.loads(jobs_json)
        return JobList(**data)
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid jobs JSON: {e}")


def _parse_chosen_job(chosen_job_json: str) -> ChosenJob:
    try:
        data = json.loads(chosen_job_json)
        return ChosenJob(**data)
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid chosen_job JSON: {e}")


async def _get_resume_content(
    resume_text: Optional[str],
    resume_file: Optional[UploadFile],
) -> str:
    if resume_text:
        return resume_text

    if resume_file:
        if not resume_file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        pdf_bytes = await resume_file.read()
        return extract_text_from_pdf(pdf_bytes)

    raise HTTPException(status_code=400, detail="Either resume_text or resume_file must be provided")
