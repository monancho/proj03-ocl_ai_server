# AI Assisted Development Log

## Bootstrap - Project Documentation

### 변경 요약

- Doodle & Quiz AI Server MVP 개발을 위한 기본 폴더 구조와 문서를 준비했습니다.
- `AGENTS.md`, README, `.env.example`, `.gitignore`, P0 작업 프롬프트를 준비했습니다.

### 검증 결과

- FastAPI 구현 전 단계였으므로 API 테스트는 실행하지 않았습니다.
- secret 값은 작성하지 않았습니다.

## 2026-06-10 - P0 AI Server Foundation

### 변경 요약

- FastAPI 앱 초기 구조를 구현했습니다.
- `GET /health`, `POST /ai/quiz/generate/text`, `POST /ai/image/moderate`를 구현했습니다.
- `X-Internal-Api-Key` 기반 내부 API Key 인증을 추가했습니다.
- 공통 실패 응답 형식과 P0 error code 처리를 추가했습니다.
- 텍스트 퀴즈 생성과 이미지 moderation은 실제 OpenAI 호출 없이 테스트 가능한 stub 서비스로 분리했습니다.
- 최소 pytest 테스트를 추가했습니다.

### 변경 파일

- `app/main.py`
- `app/api/health.py`
- `app/api/quiz.py`
- `app/api/image.py`
- `app/core/config.py`
- `app/core/auth.py`
- `app/core/errors.py`
- `app/schemas/error.py`
- `app/schemas/quiz.py`
- `app/schemas/image.py`
- `app/services/quiz_generation_service.py`
- `app/services/image_moderation_service.py`
- `tests/test_health.py`
- `tests/test_auth.py`
- `tests/test_quiz_text.py`
- `tests/test_image_moderation.py`
- `requirements.txt`
- `README.md`
- `docs/development/TEST_REPORT.md`

### 검증 명령

- `python -m pip install -r requirements.txt`
- `python -m pytest`
- `python -c "from app.main import app; print(app.title)"`

### 검증 결과

- `python -m pytest`: 11 passed, 32 warnings
- FastAPI 앱 import 확인 성공

### 미실행 / 실패 사유

- `uvicorn app.main:app --reload --port 8000`: 장기 실행 서버 대신 import 확인으로 대체했습니다.
- `docker build -t ai-server:0.1.0 .`: Dockerfile은 P2 범위라 이번 P0에서는 실행하지 않았습니다.
- 실제 OpenAI API 호출: 실제 API Key가 없어 stub 테스트로 대체했습니다.

### 리스크 / 후속 작업

- 퀴즈 생성과 이미지 moderation은 P0 stub이며, P1/P2에서 실제 OpenAI 호출과 1회 재시도 처리가 필요합니다.
- 현재 작업 디렉터리는 `.git`이 없어 git status와 commit을 수행할 수 없습니다.

## 2026-06-10 - P1 Web and YouTube Quiz Foundation

### 변경 요약

- `POST /ai/quiz/generate/web` endpoint를 추가했습니다.
- `POST /ai/quiz/generate/youtube` endpoint를 추가했습니다.
- 정적 HTML 본문 추출 service를 추가했습니다.
- YouTube URL 검증과 자막 추출 service 구조를 추가했습니다.
- web/youtube 입력은 12,000자 초과 시 앞부분만 사용하고 warning을 반환하도록 구현했습니다.
- 문제 생성 결과 schema, 문항 수, 보기 수, `answer_index=0` 검증 실패 시 1회 재시도하도록 구현했습니다.
- P1 pytest 테스트를 추가했습니다.

### 변경 파일

- `app/api/quiz.py`
- `app/schemas/quiz.py`
- `app/services/quiz_generation_service.py`
- `app/services/web_extract_service.py`
- `app/services/youtube_extract_service.py`
- `tests/test_quiz_web.py`
- `tests/test_quiz_youtube.py`
- `tests/test_quiz_retry.py`
- `requirements.txt`
- `docs/development/TEST_REPORT.md`
- `docs/development/AI_ASSISTED_DEVELOPMENT_LOG.md`

### 검증 명령

- `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
- `.\.venv\Scripts\python.exe -m pytest`
- `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title)"`

### 검증 결과

- `.venv` 내부 의존성 설치 성공
- `python -m pytest`: 18 passed, 47 warnings
- FastAPI 앱 import 확인 성공

### 미실행 / 실패 사유

- 실제 OpenAI API 호출: 현재 P1은 stub 구조이며 실제 OpenAI 호출을 수행하지 않았습니다.
- 실제 외부 웹사이트 fetch: 테스트 안정성을 위해 mock으로 대체했습니다.
- 실제 YouTube 자막 호출: 네트워크와 영상 상태에 의존하므로 mock으로 대체했습니다.
- `uvicorn app.main:app --reload --port 8000`: 장기 실행 서버라 pytest/TestClient 검증으로 대체했습니다.
- `docker build -t ai-server:0.1.0 .`: Dockerfile은 P2 범위라 실행하지 않았습니다.

### 리스크 / 후속 작업

- 실제 OpenAI structured output 연동은 아직 stub입니다.
- YouTube 자막 추출은 `youtube-transcript-api` 기반 구조를 추가했지만 실제 영상 검증은 사용자 API/네트워크 환경에서 별도 확인이 필요합니다.
- Dockerfile, curl/Postman 예시 보강, 테스트 결과 요약 정리는 P2에서 진행해야 합니다.

## 2026-06-10 - P2 Docker and API Test Docs

### 변경 요약

- Dockerfile을 추가했습니다.
- `.dockerignore`를 추가해 실제 `.env`, 로컬 캐시, 가상환경이 Docker build context에 포함되지 않도록 했습니다.
- `.env.example`을 placeholder와 주석 중심으로 보강했습니다.
- README에 `.venv` 기반 로컬 실행, Docker 실행, 환경변수, curl 예시, MVP 제외 범위, 보안 주의사항을 정리했습니다.
- `docs/development/CURL_EXAMPLES.md`에 health, text, web, youtube, image moderation, invalid API key curl 예시를 추가했습니다.
- 테스트 결과 요약을 갱신했습니다.

### 변경 파일

- `Dockerfile`
- `.dockerignore`
- `.env.example`
- `README.md`
- `docs/development/CURL_EXAMPLES.md`
- `docs/development/TEST_REPORT.md`
- `docs/development/AI_ASSISTED_DEVELOPMENT_LOG.md`

### 검증 명령

- `.\.venv\Scripts\python.exe -m pytest`
- `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title)"`
- `docker build -t ai-server:0.1.0 .`
- `git status --short`

### 검증 결과

- `python -m pytest`: 18 passed, 47 warnings
- FastAPI 앱 import 확인 성공
- `git status --short`: 변경 파일 확인 성공

### 미실행/실패 사유

- `docker build -t ai-server:0.1.0 .`: Docker Desktop/Linux engine이 실행 중이 아니어서 Docker API 연결에 실패했습니다.
- 실제 OpenAI API 호출: 현재 구현은 stub 구조이며 실제 API Key가 있어도 OpenAI 호출 코드는 아직 연결되어 있지 않습니다.

### 리스크/후속 작업

- Docker Desktop 실행 후 Docker build를 재검증해야 합니다.
- 실제 OpenAI structured output과 OpenAI image moderation 연동은 별도 후속 작업이 필요합니다.
- 실제 배포, GitHub push, 외부 서비스 생성은 수행하지 않았습니다.

## 2026-06-10 - OpenAI Actual Integration

### 변경 요약

- 퀴즈 생성 service의 stub 생성기를 OpenAI structured output 호출로 교체했습니다.
- OpenAI Python SDK의 `chat.completions.parse`와 Pydantic response model을 사용하도록 구성했습니다.
- schema 오류, 문항 수 오류, 보기 수 오류, `answer_index=0` 검증 실패 시 1회 재시도하는 구조를 유지했습니다.
- 이미지 moderation service의 stub을 OpenAI moderation 호출로 교체했습니다.
- 이미지 파일은 base64 data URL로만 요청 중 처리하고 저장하지 않습니다.
- pytest에서는 fake OpenAI client와 monkeypatch로 실제 OpenAI 호출 없이 검증하도록 보강했습니다.
- 최소 실제 OpenAI 호출로 퀴즈 생성 1회, 이미지 moderation 1회를 확인했습니다.

### 변경 파일

- `app/services/quiz_generation_service.py`
- `app/services/image_moderation_service.py`
- `tests/test_quiz_text.py`
- `tests/test_quiz_web.py`
- `tests/test_quiz_youtube.py`
- `tests/test_image_moderation.py`
- `tests/test_openai_integration_clients.py`
- `requirements.txt`
- `docs/development/TEST_REPORT.md`
- `docs/development/AI_ASSISTED_DEVELOPMENT_LOG.md`

### 검증 명령

- `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
- `.\.venv\Scripts\python.exe -m pytest`
- `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title)"`
- 최소 실제 OpenAI 퀴즈 생성 호출
- 최소 실제 OpenAI 이미지 moderation 호출

### 검증 결과

- `python -m pytest`: 20 passed, 47 warnings
- FastAPI 앱 import 확인 성공
- 실제 OpenAI 퀴즈 생성 호출 성공: 3문항 반환
- 실제 OpenAI 이미지 moderation 호출 성공: 유효한 1x1 PNG 기준 low risk 반환

### 미실행 / 실패 사유

- 대량 실제 OpenAI 호출: 비용 발생 가능성이 있어 수행하지 않았습니다.
- 실제 유해 이미지 차단 케이스: 안전성과 테스트 데이터 문제로 수행하지 않았습니다.
- 실제 배포와 GitHub push: 명시 제외 범위라 수행하지 않았습니다.

### 리스크 / 후속 작업

- 실제 생성 품질은 다양한 긴 입력, 웹페이지, YouTube 자막으로 추가 수동 검증이 필요합니다.
- 현재 Python 3.14 환경에서 FastAPI/Starlette deprecation warning이 표시됩니다.
- 운영 공개 전 Swagger 접근 제한과 로그 정책을 점검해야 합니다.

## 2026-06-10 - Final Verification and Submission Prep

### 변경 요약

- `.venv` 기준 pytest를 재실행했습니다.
- FastAPI 서버를 로컬에서 실행하고 `/health`, `/docs`, auth 실패, text quiz, image moderation curl 흐름을 검증했습니다.
- Docker Desktop engine이 실행 중임을 확인하고 Docker image build를 재검증했습니다.
- 최종 테스트 리포트를 갱신했습니다.

### 변경 파일

- `docs/development/TEST_REPORT.md`
- `docs/development/AI_ASSISTED_DEVELOPMENT_LOG.md`

### 검증 명령

- `.\.venv\Scripts\python.exe -m pytest`
- `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title)"`
- `uvicorn app.main:app --host 127.0.0.1 --port 8000`
- `/health`, `/docs`, auth 실패, text quiz, image moderation curl 검증
- `docker info --format '{{.ServerVersion}}'`
- `docker build -t ai-server:0.1.0 .`
- `git status --short`

### 검증 결과

- `python -m pytest`: 20 passed, 47 warnings
- `/health`: HTTP 200
- `/docs`: HTTP 200
- invalid API key: HTTP 401
- text quiz: HTTP 200
- image moderation: HTTP 200
- Docker engine: 29.5.2
- Docker build: 성공

### 미실행 / 실패 사유

- 실제 유해 이미지 차단 케이스: 안전성과 테스트 데이터 문제로 수행하지 않았습니다.
- 대량 OpenAI 호출: 비용 발생 가능성이 있어 수행하지 않았습니다.
- GitHub push: 명시 제외 범위라 수행하지 않았습니다.

### 리스크 / 후속 작업

- 운영 전 Swagger 접근 제한과 로그 정책을 점검해야 합니다.
- 실제 서비스 연동 전 다양한 웹페이지/YouTube 자막으로 수동 품질 검증이 필요합니다.

## 2026-06-10 - P2.5 운영 안정화 / 입력 품질 강화

### 변경 요약

- 직접 입력, 웹, YouTube 학습 텍스트에 공통 규칙 기반 전처리를 추가했습니다.
- OpenAI에 전달되는 최종 학습 텍스트 기준으로 12,000자 제한이 적용되도록 정리했습니다.
- 웹 정적 HTML 추출에서 `nav`, `footer`, `header`, `aside`, `script`, `style` 등 비본문 요소 제거를 강화했습니다.
- 웹 추출 warning code로 `CONTENT_TRUNCATED`, `NO_MAIN_CONTENT_FOUND`, `DYNAMIC_PAGE_LIKELY`를 반환하도록 했습니다.
- YouTube 자막 선택을 ko 수동, ko 자동, en 수동/자동 순서로 시도하도록 구성했습니다.
- YouTube warning code로 `YOUTUBE_AUTO_TRANSCRIPT_USED`, `YOUTUBE_EN_TRANSCRIPT_USED`, `CONTENT_TRUNCATED`를 반환하도록 했습니다.
- 이미지 moderation 응답에 `action` 필드를 추가하고 low=allow, medium=review, high=block 정책으로 정리했습니다.
- DB/Redis 없이 전체 일일 in-memory 보호 제한과 endpoint별 분당 보호 제한을 추가했습니다.
- P2.5 정책에 맞춰 README, API/기능/아키텍처/운영/테스트 문서를 갱신했습니다.
- 관련 pytest를 추가하고 기존 테스트를 유지했습니다.

### 변경 파일

- `app/api/quiz.py`
- `app/api/image.py`
- `app/core/config.py`
- `app/core/rate_limit.py`
- `app/schemas/image.py`
- `app/services/text_processing_service.py`
- `app/services/quiz_generation_service.py`
- `app/services/web_extract_service.py`
- `app/services/youtube_extract_service.py`
- `app/services/image_moderation_service.py`
- `tests/test_quiz_text.py`
- `tests/test_quiz_web.py`
- `tests/test_quiz_youtube.py`
- `tests/test_image_moderation.py`
- `tests/test_openai_integration_clients.py`
- `tests/test_rate_limit.py`
- `.env.example`
- `README.md`
- `docs/DOCUMENT_INDEX.md`
- `docs/FUNCTIONAL_SPECIFICATION.md`
- `docs/API_SPECIFICATION.md`
- `docs/ARCHITECTURE.md`
- `docs/DEPLOYMENT_OPERATION.md`
- `docs/TESTING.md`
- `docs/development/CURL_EXAMPLES.md`
- `docs/development/TEST_REPORT.md`
- `docs/development/NEXT_TASK_PROMPT.md`

### 검증 명령

- `.\.venv\Scripts\python.exe -m pytest`
- `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title)"`
- local `/health` 확인

### 검증 결과

- `python -m pytest`: 25 passed, 50 warnings
- FastAPI 앱 import 확인 성공
- `/health`: HTTP 200 응답 확인

### 미실행 / 실패 사유

- 실제 OpenAI 호출: 비용 발생 가능성이 있어 mock/fake client 테스트로 대체했습니다.
- 실제 외부 웹사이트/YouTube 호출: 외부 상태와 네트워크에 의존하므로 mock 테스트로 대체했습니다.
- 실제 유해 이미지 medium/high 샘플 검증: 안전성과 데이터 취급 문제로 수행하지 않았습니다.
- 새 uvicorn 프로세스 실행: 8000 포트에 기존 서버 프로세스가 있어 새 프로세스는 즉시 종료되었고, 기존 서버의 `/health` 응답만 확인했습니다.

### 리스크 / 후속 작업

- in-memory 보호 제한은 프로세스 재시작 시 초기화되며 멀티 프로세스/멀티 인스턴스 환경에서는 공유되지 않습니다.
- 웹 동적 렌더링은 여전히 MVP 제외 범위이며 warning으로만 표현합니다.
- medium risk 이미지는 `review`로 반환하지만 실제 검토 큐/관리자 화면은 백엔드 또는 후속 서비스 범위입니다.
- 운영 전 실제 샘플 웹페이지, YouTube 자막, 이미지 정책 샘플로 수동 품질 검증이 필요합니다.

## 2026-06-10 - Pre-Deployment Local Stabilization

### 변경 요약

- 배포 전 로컬 안정화 점검을 수행했습니다.
- Swagger/OpenAPI에서 request/response 의미가 더 잘 보이도록 Pydantic schema 설명과 예시를 보강했습니다.
- README와 curl 예시에 PowerShell 친화적인 `Invoke-RestMethod` 예시를 추가했습니다.
- 기능/API/아키텍처/테스트 문서의 전처리 기준, `action=allow/review/block`, 모듈 구조 표현을 정리했습니다.
- `.gitignore`와 `.dockerignore`의 secret/로컬 산출물 제외 상태를 확인했습니다.
- Docker image build를 재검증했습니다.

### 변경 파일

- `app/schemas/quiz.py`
- `app/schemas/image.py`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/FUNCTIONAL_SPECIFICATION.md`
- `docs/DEVELOPMENT_PLAN_CHECKLIST.md`
- `docs/TESTING.md`
- `docs/development/CURL_EXAMPLES.md`
- `docs/development/TEST_REPORT.md`
- `docs/development/AI_ASSISTED_DEVELOPMENT_LOG.md`
- `docs/development/NEXT_TASK_PROMPT.md`

### 검증 명령

- `.\.venv\Scripts\python.exe -m pytest`
- `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title); print(len(app.openapi().get('paths', {})))"`
- 임시 로컬 서버 8010 포트 smoke test
- `docker info --format '{{.ServerVersion}}'`
- `docker build -t ai-server:0.1.0 .`
- secret pattern scan

### 검증 결과

- `python -m pytest`: 25 passed, 50 warnings
- FastAPI app import와 OpenAPI schema 생성 성공
- `/health`: HTTP 200
- `/docs`: HTTP 200
- 인증 실패 케이스: HTTP 401
- Docker engine: 29.5.2
- Docker build: 성공
- secret pattern scan: 실제 secret 패턴 미검출, placeholder만 확인

### 미실행 / 실패 사유

- 실제 OpenAI 호출: 비용 발생 가능성이 있어 이번 단계에서는 mock/fake client 테스트로 대체했습니다.
- 실제 유해 이미지 샘플: 안전성과 데이터 취급 문제로 사용하지 않았습니다.
- Docker run: 실제 `.env` 주입이 필요하므로 build 검증으로 대체했습니다.

### 리스크 / 후속 작업

- Python 3.14 환경에서 FastAPI/Starlette deprecation warning이 계속 표시됩니다.
- 실제 운영 전에는 Python 3.11 컨테이너 기준 실행과 실제 서비스 백엔드 연동 smoke test가 필요합니다.
- GitHub push는 수행하지 않았습니다.

## 2026-06-10 - Pre-Deployment Hardening

### 변경 요약

- `/ready` endpoint를 추가해 필수 환경변수 readiness를 확인할 수 있게 했습니다.
- 모든 응답에 `X-Request-Id` header를 포함하고, 요청에서 전달된 request id를 유지하도록 middleware를 추가했습니다.
- 웹 URL fetch 전에 SSRF 위험이 있는 localhost, 사설 IP, link-local, metadata IP를 차단하도록 했습니다.
- 이미지 업로드 검증에 파일 header signature 검사를 추가했습니다.
- Dockerfile에 `HEALTHCHECK`를 추가했습니다.
- API 응답 샘플, 백엔드 client 예시, 품질 샘플 케이스 문서를 추가했습니다.
- README, API/아키텍처/운영/테스트/백엔드 연동 문서를 보강했습니다.

### 변경 파일

- `app/main.py`
- `app/api/health.py`
- `app/core/request_context.py`
- `app/services/web_extract_service.py`
- `app/services/image_moderation_service.py`
- `tests/test_health.py`
- `tests/test_quiz_web.py`
- `tests/test_image_moderation.py`
- `tests/test_openai_integration_clients.py`
- `Dockerfile`
- `README.md`
- `docs/API_SPECIFICATION.md`
- `docs/ARCHITECTURE.md`
- `docs/DEPLOYMENT_OPERATION.md`
- `docs/DOCUMENT_INDEX.md`
- `docs/TESTING.md`
- `docs/BACKEND_INTEGRATION_GUIDE.md`
- `docs/development/API_RESPONSE_SAMPLES.md`
- `docs/development/BACKEND_CLIENT_EXAMPLES.md`
- `docs/development/QUALITY_SAMPLE_CASES.md`
- `docs/development/TEST_REPORT.md`

### 검증 명령

- `.\.venv\Scripts\python.exe -m pytest`
- `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title); print(len(app.openapi().get('paths', {})))"`
- 임시 로컬 서버 8011 포트 smoke test
- `docker build -t ai-server:0.1.0 .`
- secret pattern scan

### 검증 결과

- `python -m pytest`: 30 passed, 57 warnings
- FastAPI app import와 OpenAPI schema 생성 성공, path 6개
- `/health`: HTTP 200
- `/ready`: HTTP 200
- `/docs`: HTTP 200
- 인증 실패 케이스: HTTP 401
- `X-Request-Id` echo 확인 성공
- Docker build: 성공
- secret pattern scan: 실제 secret 패턴 미검출

### 미실행 / 실패 사유

- 실제 OpenAI 호출: 비용 발생 가능성이 있어 mock/fake client 테스트로 대체했습니다.
- 실제 유해 이미지 샘플: 안전성과 데이터 취급 문제로 사용하지 않았습니다.
- Docker run: 실제 `.env` 주입이 필요하므로 build와 로컬 uvicorn smoke test로 대체했습니다.

### 리스크 / 후속 작업

- SSRF 방어는 기본적인 URL/IP 차단이며, 운영 환경에서는 네트워크 레벨 egress 제한도 함께 적용해야 합니다.
- `X-Request-Id`는 기본 로깅만 제공하므로 운영 로그 포맷/수집기는 배포 환경에서 별도 설정해야 합니다.
- 이미지 header signature 검사는 기본 위장 방어이며, 실제 이미지 디코딩/재인코딩 검증은 후속 고도화 대상입니다.
## 2026-06-10 - Daily Limit Policy Adjustment

### 변경 요약

- OpenAI 공식 Moderation 문서에서 `omni-moderation-latest`가 text/image input을 지원하고 moderation endpoint가 free to use임을 확인했습니다.
- `AI_DAILY_REQUEST_LIMIT` 기본값을 100으로 낮췄습니다.
- `/ai/image/moderate`는 daily request count에서 제외했습니다.
- 이미지 moderation은 abuse 방어를 위해 endpoint별 `AI_RATE_LIMIT_PER_MINUTE` 보호는 계속 적용합니다.

### 변경 파일

- `app/core/config.py`
- `app/core/rate_limit.py`
- `tests/test_rate_limit.py`
- `.env.example`
- `README.md`
- `docs/API_SPECIFICATION.md`
- `docs/DEPLOYMENT_OPERATION.md`
- `docs/TESTING.md`

### 보안 확인

- `.env` 실제 값은 읽거나 출력하지 않았습니다.
- API Key, token, credential은 출력하지 않았습니다.
- GitHub push는 수행하지 않았습니다.
