# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Job Search Agent is a multi-agent AI system built with CrewAI and FastAPI that automates job searching, matching, resume optimization, and interview preparation. It uses a pipeline of specialized agents to process job searches end-to-end.

## Commands

```bash
# Install dependencies (requires uv package manager)
uv sync

# Run the FastAPI server
uv run uvicorn app.main:app --reload
```

## Architecture

### Folder Structure

```
app/
├── main.py              # FastAPI 앱 초기화
├── routers/
│   └── crew.py          # /crew/* API 엔드포인트
├── crew/
│   ├── config/
│   │   ├── agents.yaml  # 에이전트 정의
│   │   └── tasks.yaml   # 태스크 정의
│   ├── crew.py          # JobSearchCrew 클래스
│   ├── schemas.py       # Pydantic 모델
│   └── tools.py         # CrewAI 툴 (web_search_tool)
└── utils/
    └── pdf.py           # PDF 텍스트 추출
```

### Multi-Agent Pipeline (CrewAI)

The system uses 5 specialized agents that execute sequentially in `app/crew/crew.py`:

1. **job_search_agent** - Searches for job postings using Firecrawl web search
2. **job_matching_agent** - Scores jobs against user's resume (1-5 scale)
3. **resume_optimization_agent** - Rewrites resume for the selected job
4. **company_research_agent** - Researches the target company
5. **interview_prep_agent** - Creates interview preparation materials

### Task Flow

```
job_extraction_task → job_matching_task → job_selection_task
                                                ↓
                      ┌─────────────────────────┼─────────────────────────┐
                      ↓                         ↓                         ↓
            resume_rewriting_task    company_research_task    interview_prep_task
                      ↓                         ↓                         ↓
            output/rewritten_resume.md  output/company_research.md  output/interview_prep.md
```

## API

API 문서는 `docs/API.md` 참조. 주요 엔드포인트:

- `POST /crew/kickoff` - 비동기 실행 (task_id 반환)
- `POST /crew/kickoff/sync` - 동기 실행 (결과 직접 반환)
- `GET /crew/status/{task_id}` - 작업 상태 조회
- `GET /crew/tasks` - 전체 작업 목록

이력서는 PDF 파일 업로드 또는 텍스트로 전달 가능.

## Environment Variables

Required in `.env`:
- `OPENAI_API_KEY` - For LLM calls (agents use `openai/o4-mini-2025-04-16`)
- `FIRECRAWL_API_KEY` - For web search tool in `app/crew/tools.py`

## Key Patterns

- Agents are decorated with `@agent`, tasks with `@task`, crew with `@crew` (CrewAI decorators)
- Task outputs use Pydantic models via `output_pydantic` parameter
- Tasks can reference other tasks via `context` parameter for dependencies
- Resume content is passed dynamically via `StringKnowledgeSource`
- Output files are written to `output/` directory
