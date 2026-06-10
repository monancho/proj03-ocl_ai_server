# 문서 인덱스

## 프로젝트

- 프로젝트명: Doodle & Quiz AI Server MVP
- 문서 기준: MVP 개발 준비용 Markdown 문서
- 현재 상태: Bootstrap / Documentation Phase

## 문서 목록

| 문서 | 목적 | 주 사용 대상 |
|---|---|---|
| `DOCUMENT_INDEX.md` | 문서 목록, 읽는 순서, 문서 간 관계 | 제출자, 검토자, 개발자 |
| `REQUIREMENTS.md` | 목적, 범위, 기능/비기능 요구사항 | 기획자, 개발자, 평가자 |
| `FUNCTIONAL_SPECIFICATION.md` | 문제 생성, 이미지 필터, 예외 처리, 품질 기준 | 백엔드/AI 개발자 |
| `ARCHITECTURE.md` | FastAPI, LangChain, 외부 모델 API, Docker 구조 | 백엔드 개발자, 배포 담당자 |
| `API_SPECIFICATION.md` | Endpoint, Request, Response, Error Code | 개발자, API 테스터 |
| `DEPLOYMENT_OPERATION.md` | Docker 실행, 환경변수, 보안/운영 주의사항 | 배포 담당자 |
| `DEVELOPMENT_PLAN_CHECKLIST.md` | 구현 순서, 우선순위, 테스트 항목 | 개발자, 제출자 |
| `TESTING.md` | 자동/수동/API 검증 기준 | 개발자, 테스터 |

## 읽는 순서

1. `REQUIREMENTS.md`에서 범위와 제외 범위를 확인한다.
2. `FUNCTIONAL_SPECIFICATION.md`에서 문제 생성/이미지 필터 동작 기준을 확인한다.
3. `API_SPECIFICATION.md`에서 endpoint와 payload를 확정한다.
4. `ARCHITECTURE.md`와 `DEPLOYMENT_OPERATION.md`로 서버 구조와 실행 방식을 맞춘다.
5. `DEVELOPMENT_PLAN_CHECKLIST.md`로 구현 단계와 테스트 완료 기준을 관리한다.
6. `docs/development/AI_ASSISTED_DEVELOPMENT.md`로 AI 작업 규칙을 확인한다.

## 문서 작성 원칙

- AI 서버는 클라이언트와 직접 소통하지 않는 독립 API 서버로 정의한다.
- DB, Socket, Room, Chat, Drawing, Result 관련 계약은 본 패키지에서 제외한다.
- 문서는 구현자가 바로 API를 만들 수 있도록 표와 예시 중심으로 작성한다.
