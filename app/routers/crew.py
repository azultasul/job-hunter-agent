from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from pathlib import Path
from typing import Optional
import uuid
import json

from app.crew.crew import JobSearchCrew
from app.crew.schemas import (
    CrewResult,
    JobList,
    RankedJobList,
    ChosenJob,
)
from app.utils.pdf import extract_text_from_pdf

router = APIRouter(prefix="/crew", tags=["crew (deprecated)"])

# In-memory storage for task results
tasks: dict[str, dict] = {}


@router.post("/kickoff", deprecated=True)
async def kickoff_crew(
    background_tasks: BackgroundTasks,
    level: str = Form(...),
    position: str = Form(...),
    location: str = Form(...),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    job_sites: Optional[str] = Form(None),
):
    """
    [DEPRECATED] 단계별 API (/crew/step/*) 사용을 권장합니다.

    비동기로 전체 파이프라인을 실행합니다. task_id를 반환하며, 이를 통해 진행 상태를 확인할 수 있습니다.
    """
    resume_content = await _get_resume_content(resume_text, resume_file)
    sites_list = _parse_job_sites(job_sites)

    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running", "result": None, "error": None}

    background_tasks.add_task(
        run_crew_task,
        task_id,
        level,
        position,
        location,
        resume_content,
        sites_list,
    )

    return {"task_id": task_id, "status": "running"}


@router.post("/kickoff/sync", response_model=CrewResult, deprecated=True)
async def kickoff_crew_sync(
    level: str = Form(...),
    position: str = Form(...),
    location: str = Form(...),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    job_sites: Optional[str] = Form(None),
):
    """
    [DEPRECATED] 단계별 API (/crew/step/*) 사용을 권장합니다.

    동기적으로 전체 파이프라인을 실행하고 결과를 직접 반환합니다. 수 분이 소요될 수 있습니다.
    """
    resume_content = await _get_resume_content(resume_text, resume_file)
    sites_list = _parse_job_sites(job_sites)

    try:
        crew_instance = JobSearchCrew(
            resume_text=resume_content,
            job_sites=sites_list,
        ).crew()
        result = crew_instance.kickoff(
            inputs={
                "level": level,
                "position": position,
                "location": location,
            }
        )
        return parse_crew_result(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", deprecated=True)
def get_task_status(task_id: str):
    """
    [DEPRECATED] /crew/kickoff의 작업 상태를 조회합니다.
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    response = {"task_id": task_id, "status": task["status"]}

    if task["status"] == "completed":
        response["result"] = task["result"]
    elif task["status"] == "failed":
        response["error"] = task["error"]

    return response


@router.get("/tasks", deprecated=True)
def list_tasks():
    """
    [DEPRECATED] /crew/kickoff의 모든 작업 목록을 조회합니다.
    """
    return {
        task_id: {"status": task["status"]}
        for task_id, task in tasks.items()
    }


def _parse_job_sites(job_sites: Optional[str]) -> Optional[list[str]]:
    """
    Parse job_sites JSON string to list.
    """
    if not job_sites:
        return None
    try:
        sites = json.loads(job_sites)
        if isinstance(sites, list):
            return sites
        return None
    except json.JSONDecodeError:
        return None


async def _get_resume_content(
    resume_text: Optional[str],
    resume_file: Optional[UploadFile],
) -> str:
    """
    Extract resume content from either text or PDF file.
    """
    if resume_text:
        return resume_text

    if resume_file:
        if not resume_file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        pdf_bytes = await resume_file.read()
        return extract_text_from_pdf(pdf_bytes)

    raise HTTPException(
        status_code=400,
        detail="Either resume_text or resume_file must be provided"
    )


def run_crew_task(
    task_id: str,
    level: str,
    position: str,
    location: str,
    resume_content: str,
    job_sites: Optional[list[str]],
):
    """
    Background task to run the crew.
    """
    try:
        crew_instance = JobSearchCrew(
            resume_text=resume_content,
            job_sites=job_sites,
        ).crew()
        result = crew_instance.kickoff(
            inputs={
                "level": level,
                "position": position,
                "location": location,
            }
        )
        tasks[task_id]["result"] = parse_crew_result(result).model_dump()
        tasks[task_id]["status"] = "completed"
    except Exception as e:
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["status"] = "failed"


def parse_crew_result(result) -> CrewResult:
    """
    Parse CrewAI result into structured response.
    """
    crew_result = CrewResult()

    for task_output in result.tasks_output:
        if task_output.pydantic:
            if isinstance(task_output.pydantic, JobList):
                crew_result.jobs = task_output.pydantic.jobs
            elif isinstance(task_output.pydantic, RankedJobList):
                crew_result.ranked_jobs = task_output.pydantic.ranked_jobs
            elif isinstance(task_output.pydantic, ChosenJob):
                crew_result.chosen_job = task_output.pydantic

    # Read output files if they exist
    output_dir = Path("output")

    resume_file = output_dir / "rewritten_resume.md"
    if resume_file.exists():
        crew_result.rewritten_resume = resume_file.read_text()

    research_file = output_dir / "company_research.md"
    if research_file.exists():
        crew_result.company_research = research_file.read_text()

    prep_file = output_dir / "interview_prep.md"
    if prep_file.exists():
        crew_result.interview_prep = prep_file.read_text()

    return crew_result
