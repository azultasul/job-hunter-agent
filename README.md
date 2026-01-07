## 1. **Project Overview**

    - 한 문장 설명(무엇을/누구를 위해/어떤 문제 해결)
    - 핵심 기능 3~5개 bullets
    - 데모/스크린샷/간단 시퀀스(선택)

## 2. **Tech Stack**

    - 런타임/프레임워크(FastAPI 등), LLM provider(OpenAI 등), 벡터DB/DB, 큐/캐시, 관측도구

## 3. **Architecture**

    - 요청 흐름(클라이언트 → API → LLM/툴/DB)
    - 주요 디렉토리 구조(예: app/crew, main.py, .yaml)
    - (있다면) 멀티에이전트/워크플로우 개요

## 4. **Quickstart**

    - 요구사항(Python 버전, Poetry/uv 등)
    - 설치/실행 명령
    - 가장 작은 성공 기준: “헬스체크”와 “샘플 요청” 1개(curl)

## 5. **Configuration**

    - 필수/선택 환경변수 표(OPENAI_API_KEY, 모델명, 로그 레벨 등)
    - 설정 파일(tasks.yaml, agents.yaml) 역할과 수정 방법
    - 비밀 관리 원칙(.env, vault, 로테이션)

## 6. **API Reference**

    - Base URL / Auth 방식
    - 주요 엔드포인트 요약 표(메서드, 경로, 설명)
    - 대표 요청/응답 예시 1~2개
    - 에러 코드/에러 응답 스키마
    - 레이트 리밋/타임아웃/리트라이 정책

## 7. **Development**

    - 로컬 개발 팁(핫리로드, 프리커밋/린트, 포매터)
    - 테스트 실행 방법 + 테스트 범위(유닛/통합/계약)
    - (LLM이면 특히) 프롬프트/워크플로우 변경 시 검증 방법

## 8. **Observability**

    - 로깅 포맷(구조화 로그 권장), 트레이싱, 메트릭
    - LLM 특화 지표: 토큰 사용량, 비용, 지연, 실패율, fallback 비율

## 9. **Security & Safety**

    - 입력 검증, PII 처리, 프롬프트 인젝션 대응(툴 화이트리스트 등)
    - 권한/키 보호, 감사로그
    - 모델/툴 사용 제한(allowlist, sandbox)

## 10. **Deployment**

    - Docker/Compose 또는 배포 방식(K8s 등)
    - 환경별 설정(dev/stage/prod)
    - 스케일링/워커/큐(있다면)

## 11. **Roadmap**

    - 가까운 계획(3~6개), 알려진 이슈

## 12. **Contributing**

    - 브랜치/PR 규칙, 코드 스타일, 이슈 템플릿(선택)

## 13. **License**

    - 라이선스 + Third-party notices(선택)
