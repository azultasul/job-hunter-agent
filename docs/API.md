# API Reference

Base URL: `http://localhost:8000`

## Overview

| 방식 | 엔드포인트 | 상태 |
|------|-----------|------|
| **단계별 실행** | `/crew/step/*` | **권장** |
| ~~일괄 실행~~ | `/crew/kickoff`, `/crew/kickoff/sync` | Deprecated |

---

## 일괄 실행 API (Deprecated)

> ⚠️ **Deprecated**: 단계별 API (`/crew/step/*`) 사용을 권장합니다.

### POST /crew/kickoff

~~비동기로 전체 파이프라인을 실행합니다.~~

**Content-Type:** `multipart/form-data`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| level | string | Yes | 경력 수준 (예: "junior", "mid level", "senior") |
| position | string | Yes | 희망 직무 (예: "frontend developer", "backend developer") |
| location | string | Yes | 희망 근무지 (예: "korea", "seoul", "remote") |
| resume_text | string | No* | 이력서 텍스트 (resume_file과 둘 중 하나 필수) |
| resume_file | file | No* | 이력서 PDF 파일 (resume_text와 둘 중 하나 필수) |
| job_sites | string | No | 검색할 사이트 도메인 JSON 배열 |

**Response:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/crew/kickoff \
  -F "level=mid level" \
  -F "position=frontend developer" \
  -F "location=korea" \
  -F "resume_file=@resume.pdf" \
  -F 'job_sites=["saramin.co.kr", "jobkorea.co.kr"]'
```

---

### POST /crew/kickoff/sync

동기적으로 전체 파이프라인을 실행하고 결과를 직접 반환합니다.

**주의:** 전체 파이프라인 실행에 수 분이 소요될 수 있습니다.

**Content-Type:** `multipart/form-data`

**Parameters:** `/crew/kickoff`와 동일

**Response:**

```json
{
  "jobs": [...],
  "ranked_jobs": [...],
  "chosen_job": {...},
  "rewritten_resume": "# Optimized Resume...",
  "company_research": "## Company Overview...",
  "interview_prep": "## Interview Prep..."
}
```

---

### GET /crew/status/{task_id}

비동기 작업의 상태와 결과를 조회합니다.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| task_id | string | kickoff 요청 시 반환받은 task_id |

**Response:**

```json
// running
{"task_id": "...", "status": "running"}

// completed
{"task_id": "...", "status": "completed", "result": {...}}

// failed
{"task_id": "...", "status": "failed", "error": "Error message"}
```

---

### GET /crew/tasks

모든 작업 목록과 상태를 조회합니다.

**Response:**

```json
{
  "550e8400-...": {"status": "completed"},
  "660e8400-...": {"status": "running"}
}
```

---

## 단계별 실행 API

탭 UI에서 각 단계를 개별적으로 호출할 때 사용합니다.

### 실행 흐름

```
[Tab 1] POST /crew/step/search
           ↓ jobs
[Tab 2] POST /crew/step/match
           ↓ chosen_job
    ┌──────┴──────┐
    ↓             ↓
[Tab 3]       [Tab 4]
/step/resume  /step/research   ← 병렬 실행 가능
    ↓             ↓
    └──────┬──────┘
           ↓
[Tab 5] POST /crew/step/interview
```

---

### POST /crew/step/search

**Tab 1:** 채용공고를 검색합니다.

**Content-Type:** `multipart/form-data`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| level | string | Yes | 경력 수준 |
| position | string | Yes | 희망 직무 |
| location | string | Yes | 희망 근무지 |
| job_sites | string | No | 검색할 사이트 도메인 JSON 배열 |

**Example:**

```bash
curl -X POST http://localhost:8000/crew/step/search \
  -F "level=mid level" \
  -F "position=frontend developer" \
  -F "location=korea" \
  -F 'job_sites=["saramin.co.kr"]'
```

**Response:**

```json
{
  "jobs": {
    "jobs": [
      {
        "job_title": "Frontend Developer",
        "company_name": "ABC Corp",
        "job_location": "Seoul",
        "job_posting_url": "https://...",
        "job_summary": "..."
      }
    ]
  }
}
```

---

### POST /crew/step/match

**Tab 2:** 이력서와 채용공고를 매칭하고 최적의 공고를 선택합니다.

**Content-Type:** `multipart/form-data`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| jobs | string | Yes | Step 1 응답의 `jobs` 전체 JSON 문자열 |
| resume_text | string | No* | 이력서 텍스트 |
| resume_file | file | No* | 이력서 PDF 파일 |

**Example:**

```bash
curl -X POST http://localhost:8000/crew/step/match \
  -F 'jobs={"jobs":[{"job_title":"...","company_name":"..."}]}' \
  -F "resume_file=@resume.pdf"
```

**Response:**

```json
{
  "ranked_jobs": {
    "ranked_jobs": [
      {"job": {...}, "match_score": 5, "reason": "..."},
      {"job": {...}, "match_score": 3, "reason": "..."}
    ]
  },
  "chosen_job": {
    "job": {...},
    "selected": true,
    "reason": "..."
  }
}
```

---

### POST /crew/step/resume

**Tab 3:** 선택된 채용공고에 맞춰 이력서를 최적화합니다.

**Content-Type:** `multipart/form-data`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| chosen_job | string | Yes | Step 2 응답의 `chosen_job` JSON 문자열 |
| resume_text | string | No* | 이력서 텍스트 |
| resume_file | file | No* | 이력서 PDF 파일 |

**Example:**

```bash
curl -X POST http://localhost:8000/crew/step/resume \
  -F 'chosen_job={"job":{...},"selected":true,"reason":"..."}' \
  -F "resume_file=@resume.pdf"
```

**Response:**

```json
{
  "rewritten_resume": "# Optimized Resume\n\n## Summary\n..."
}
```

---

### POST /crew/step/research

**Tab 4:** 선택된 채용공고의 회사를 리서치합니다.

**Content-Type:** `multipart/form-data`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| chosen_job | string | Yes | Step 2 응답의 `chosen_job` JSON 문자열 |
| resume_text | string | No* | 이력서 텍스트 |
| resume_file | file | No* | 이력서 PDF 파일 |

**Example:**

```bash
curl -X POST http://localhost:8000/crew/step/research \
  -F 'chosen_job={"job":{...},"selected":true,"reason":"..."}' \
  -F "resume_file=@resume.pdf"
```

**Response:**

```json
{
  "company_research": "## Company Overview\n\n..."
}
```

---

### POST /crew/step/interview

**Tab 5:** 면접 준비 자료를 생성합니다.

**Content-Type:** `multipart/form-data`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| chosen_job | string | Yes | Step 2 응답의 `chosen_job` JSON 문자열 |
| rewritten_resume | string | Yes | Step 3 응답의 `rewritten_resume` |
| company_research | string | Yes | Step 4 응답의 `company_research` |
| resume_text | string | No* | 이력서 텍스트 |
| resume_file | file | No* | 이력서 PDF 파일 |

**Example:**

```bash
curl -X POST http://localhost:8000/crew/step/interview \
  -F 'chosen_job={"job":{...},"selected":true,"reason":"..."}' \
  -F "rewritten_resume=# Optimized Resume..." \
  -F "company_research=## Company Overview..." \
  -F "resume_file=@resume.pdf"
```

**Response:**

```json
{
  "interview_prep": "## Interview Prep\n\n..."
}
```

---

## Schemas

### Job

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| job_title | string | Yes | 직무명 |
| company_name | string | Yes | 회사명 |
| job_location | string | Yes | 근무지 |
| job_posting_url | string | Yes | 채용 공고 URL |
| job_summary | string | Yes | 직무 요약 |
| is_remote_friendly | boolean | No | 원격 근무 가능 여부 |
| employment_type | string | No | 고용 형태 |
| compensation | string | No | 급여 정보 |
| required_technologies | string[] | No | 필수 기술 스택 |

### RankedJob

| Field | Type | Description |
|-------|------|-------------|
| job | Job | 채용 공고 정보 |
| match_score | int | 매칭 점수 (1-5) |
| reason | string | 점수 부여 이유 |

### ChosenJob

| Field | Type | Description |
|-------|------|-------------|
| job | Job | 채용 공고 정보 |
| selected | boolean | 선택 여부 |
| reason | string | 선택 이유 |

---

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | 잘못된 요청 (이력서 미제공, 잘못된 파일 형식, 잘못된 JSON 등) |
| 404 | 존재하지 않는 task_id |
| 500 | 서버 내부 오류 |

```json
{
  "detail": "Either resume_text or resume_file must be provided"
}
```

---

## job_sites 지원 도메인 예시

| 사이트 | 도메인 |
|--------|--------|
| 사람인 | `saramin.co.kr` |
| 잡코리아 | `jobkorea.co.kr` |
| LinkedIn | `linkedin.com` |
| Indeed | `indeed.com` |
| Wanted | `wanted.co.kr` |
