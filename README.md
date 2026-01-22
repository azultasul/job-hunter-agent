# Job Hunter Agent

AI 기반 멀티 에이전트 취업 지원 시스템. 채용공고 검색부터 이력서 최적화, 면접 준비까지 자동화합니다.

## 핵심 기능

- **채용공고 검색** - 사람인, 잡코리아, LinkedIn 등 지정한 사이트에서 검색
- **이력서 매칭** - 이력서와 채용공고 적합도 분석 (1-5점)
- **이력서 최적화** - 선택한 채용공고에 맞춰 이력서 재작성
- **기업 리서치** - 지원 기업 분석 및 인사이트 제공
- **면접 준비** - 예상 질문, 답변 전략, 질문 리스트 생성

## Tech Stack

| 구분        | 기술             |
| ----------- | ---------------- |
| Runtime     | Python 3.13+     |
| Framework   | FastAPI, uvicorn |
| AI Agent    | CrewAI           |
| LLM         | OpenAI (o4-mini) |
| Web Search  | Firecrawl        |
| PDF Parsing | pypdf            |

## Architecture

### 멀티 에이전트 파이프라인

```
[Tab 1] 채용공고 검색 (job_search_agent)
           ↓
[Tab 2] 매칭 & 선택 (job_matching_agent)
           ↓
    ┌──────┴──────┐
    ↓             ↓
[Tab 3]       [Tab 4]
이력서 최적화   기업 리서치
    ↓             ↓
    └──────┬──────┘
           ↓
[Tab 5] 면접 준비 (interview_prep_agent)
```

### 디렉토리 구조

```
app/
├── main.py                 # FastAPI 앱 초기화
├── routers/
│   ├── crew.py             # 일괄 실행 API (deprecated)
│   └── steps.py            # 단계별 실행 API (권장)
├── crew/
│   ├── config/
│   │   ├── agents.yaml     # 에이전트 정의
│   │   └── tasks.yaml      # 태스크 정의
│   ├── crew.py             # JobHunterCrew 클래스
│   ├── steps.py            # 단계별 Crew 클래스
│   ├── schemas.py          # Pydantic 모델
│   └── tools.py            # web_search_tool
└── utils/
    └── pdf.py              # PDF 텍스트 추출
```

## Quickstart

### 요구사항

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) 패키지 매니저

### 설치 및 실행

```bash
# 의존성 설치
uv sync

# 환경변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 서버 실행
uv run uvicorn app.main:app --reload
```

### 샘플 요청

```bash
# 채용공고 검색
curl -X POST http://localhost:8000/crew/step/search \
  -F "level=mid level" \
  -F "position=frontend developer" \
  -F "location=korea" \
  -F 'job_sites=["saramin.co.kr"]'
```

## Configuration

### 환경변수

| 변수                | 필수 | 설명                         |
| ------------------- | ---- | ---------------------------- |
| `OPENAI_API_KEY`    | Yes  | OpenAI API 키                |
| `FIRECRAWL_API_KEY` | Yes  | Firecrawl API 키 (웹 검색용) |

### 설정 파일

- `app/crew/config/agents.yaml` - 에이전트 역할, 목표, 백스토리, LLM 모델 설정
- `app/crew/config/tasks.yaml` - 태스크 설명 및 출력 형식 정의

## API Reference

Base URL: `http://localhost:8000`

### 단계별 API (권장)

| Method | Endpoint               | 설명          |
| ------ | ---------------------- | ------------- |
| POST   | `/crew/step/search`    | 채용공고 검색 |
| POST   | `/crew/step/match`     | 매칭 & 선택   |
| POST   | `/crew/step/resume`    | 이력서 최적화 |
| POST   | `/crew/step/research`  | 기업 리서치   |
| POST   | `/crew/step/interview` | 면접 준비     |

### 지원 채용 사이트

| 사이트   | 도메인           |
| -------- | ---------------- |
| 사람인   | `saramin.co.kr`  |
| 잡코리아 | `jobkorea.co.kr` |
| LinkedIn | `linkedin.com`   |
| Wanted   | `wanted.co.kr`   |

> 상세 API 문서: [docs/API.md](docs/API.md)

## Development

```bash
# 개발 서버 실행 (핫리로드)
uv run uvicorn app.main:app --reload

# API 문서 확인
open http://localhost:8000/docs
```
