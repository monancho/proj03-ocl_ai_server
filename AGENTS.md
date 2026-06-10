# AGENTS.md

## 프로젝트 목적

**Doodle & Quiz AI Server MVP**는 FastAPI 기반 독립 AI API 서버다.  
텍스트, 웹사이트 본문, YouTube 자막을 한국어 4지선다 문제로 변환하고, 업로드 이미지의 유해성 여부를 검사한다.

MVP는 실제 서비스 연동 전 단계이며, Swagger, curl, Postman으로 단독 API 검증이 가능해야 한다.

## MVP 포함 범위

- `GET /health`
- `POST /ai/quiz/generate/text`
- `POST /ai/quiz/generate/web`
- `POST /ai/quiz/generate/youtube`
- `POST /ai/image/moderate`
- `X-Internal-Api-Key` 기반 내부 API Key 인증
- 공통 성공/실패 응답 형식
- Pydantic 기반 Request/Response schema
- LangChain 또는 동등한 구조화 출력 기반 문제 생성
- OpenAI Moderation 기반 이미지 유해성 검사
- Docker 실행 준비
- README, 테스트 문서, curl/Postman 예시 정리

## MVP 제외 범위

명시 요청 없이 구현하지 않는다.

- 프론트엔드
- DB 저장
- 사용자 로그인/회원가입
- 사용자별 생성 횟수 제한
- 관리자 페이지
- Socket.IO
- 실시간 스트리밍 응답
- YouTube 음성 다운로드
- Whisper 음성 인식
- PDF 추출
- 동적 렌더링 웹페이지 처리
- LangGraph
- RAG
- Vector DB
- Redis
- Queue/Celery/RQ
- 실제 Quiz/Doodle 서비스 연동
- 실제 배포

## 보안 규칙

- `.env` 실제 값을 작성하지 않는다.
- API Key, token, private key, credential을 생성하지 않는다.
- secret 값을 출력하지 않는다.
- secret 값을 커밋하지 않는다.
- `OPENAI_API_KEY`를 노출하지 않는다.
- `AI_SERVER_API_KEY`를 노출하지 않는다.
- 오류 메시지와 로그에 API Key, raw token, private key, 전체 사용자 입력을 포함하지 않는다.
- 외부 서비스 생성, 배포, GitHub push는 사용자 확인 없이 수행하지 않는다.
- 이미지 파일은 요청 처리 중에만 사용하고 서버에 영구 저장하지 않는다.

## 작업 전 문서 읽기 순서

1. `docs/DOCUMENT_INDEX.md`
2. `docs/REQUIREMENTS.md`
3. `docs/FUNCTIONAL_SPECIFICATION.md`
4. `docs/API_SPECIFICATION.md`
5. `docs/ARCHITECTURE.md`
6. `docs/DEPLOYMENT_OPERATION.md`
7. `docs/DEVELOPMENT_PLAN_CHECKLIST.md`
8. `docs/TESTING.md`
9. `docs/development/AI_ASSISTED_DEVELOPMENT.md`
10. `docs/development/AI_ASSISTED_DEVELOPMENT_LOG.md`

문서가 없으면 실패하지 말고 누락으로 보고한다.

## 구현 우선순위

### P0

- FastAPI 초기 세팅
- `/health`
- 환경변수 config
- 내부 API Key 인증
- 공통 error response
- 직접 입력 문제 생성
- 이미지 moderation
- 최소 테스트

### P1

- 웹사이트 본문 추출
- YouTube 자막 추출
- 문제 생성 1회 재시도
- 공통 오류 코드 정리

### P2

- Dockerfile
- `.env.example`
- README 보강
- curl/Postman 예시
- 테스트 결과 요약

### P3

- LangGraph
- RAG
- 서비스 백엔드 연동
- 생성 횟수 제한

## 핵심 API 규칙

- `/health`를 제외한 API는 `X-Internal-Api-Key`를 검증한다.
- 성공 응답은 `{ "success": true, "data": ... }` 형식을 사용한다.
- 실패 응답은 `{ "success": false, "error": { "code": string, "message": string } }` 형식을 사용한다.
- 문제 생성 결과는 항상 한국어 4지선다 3문항이다.
- 정답은 항상 1번 보기이며 `answer_index`는 항상 `0`이다.
- schema 오류, 문항 수 오류, 정답 위치 오류가 있으면 1회 재생성한다.

## 검증/보고 규칙

가능한 범위에서 다음을 실행한다.

```bash
python -m pytest
uvicorn app.main:app --reload --port 8000
docker build -t ai-server:0.1.0 .
```

실제 API Key가 없어서 외부 모델 호출 검증이 불가능하면 mock 테스트로 대체하고, 미실행 사유를 기록한다.

작업 후 보고에는 다음을 포함한다.

- 변경 요약
- 변경 파일
- 실행한 검증 명령
- 검증 결과
- 미실행/실패 사유
- 보안 확인
- 리스크/누락
- 다음 작업
- 다음 작업 추천 프롬프트

## Git 규칙

- 작업 전후 `git status --short`를 확인한다.
- commit message는 영어로 작성한다.
- push는 사용자 확인 없이 하지 않는다.
- force push, hard reset, rebase, amend는 명시 요청 없이 하지 않는다.
- 사용자 변경으로 보이는 파일은 임의로 되돌리지 않는다.

## User Action Required 기준

다음은 사용자가 직접 수행해야 한다.

- OpenAI API Key 발급
- `.env` 실제 값 작성
- 외부 서비스 계정 생성
- 배포 secret 등록
- 실제 배포 실행
- GitHub push 승인

사용자 작업이 필요하면 해야 할 일, 필요한 이유, 보안 주의사항, 완료 후 붙여넣을 프롬프트를 함께 제공한다.

## 다음 작업 프롬프트 작성 규칙

각 작업 종료 시 `docs/development/NEXT_TASK_PROMPT.md` 또는 완료 보고에 바로 붙여넣을 수 있는 다음 작업 프롬프트를 작성한다.
