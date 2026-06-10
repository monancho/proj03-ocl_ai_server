# Test Report

## 2026-06-10 - Final Verification

| 명령 | 결과 | 비고 |
|---|---|---|
| `.\.venv\Scripts\python.exe -m pytest` | 성공 | 20 passed, 47 warnings |
| `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title)"` | 성공 | FastAPI 앱 import 확인 |
| `uvicorn app.main:app --host 127.0.0.1 --port 8000` | 성공 | `.venv` Python으로 로컬 서버 실행 |
| `curl /health` | 성공 | HTTP 200 |
| `curl /docs` | 성공 | HTTP 200 |
| invalid API key curl | 성공 | HTTP 401 |
| text quiz curl | 성공 | HTTP 200 |
| image moderation curl | 성공 | HTTP 200 |
| `docker info --format '{{.ServerVersion}}'` | 성공 | Docker engine 29.5.2 |
| `docker build -t ai-server:0.1.0 .` | 성공 | Docker image build 완료 |

## 검증 내용

- `.venv` 기준 전체 pytest가 통과했습니다.
- FastAPI 앱 import와 실제 uvicorn 서버 실행을 확인했습니다.
- `/health`와 Swagger UI `/docs`가 HTTP 200을 반환했습니다.
- 잘못된 `X-Internal-Api-Key`가 HTTP 401을 반환하는지 확인했습니다.
- 올바른 내부 API Key로 text quiz API가 HTTP 200을 반환하는지 확인했습니다.
- 올바른 내부 API Key와 유효한 1x1 PNG로 image moderation API가 HTTP 200을 반환하는지 확인했습니다.
- Docker Desktop engine이 실행 중인 상태에서 Docker image build가 성공했습니다.

## 주의 사항

- 첫 curl 검증 중 JSON shell quoting 오류로 HTTP 422가 한 번 발생했으나, payload 파일 방식으로 재검증해 정상 결과를 확인했습니다.
- API Key 값과 `.env` 실제 값은 출력하지 않았습니다.
- 실제 유해 이미지 차단 케이스와 대량 OpenAI 호출은 수행하지 않았습니다.

## 2026-06-10 - P2.5 운영 안정화 / 입력 품질 강화

| 명령 | 결과 | 비고 |
|---|---|---|
| `.\.venv\Scripts\python.exe -m pytest` | 성공 | 25 passed, 50 warnings |
| `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title)"` | 성공 | FastAPI 앱 import 확인 |
| local `/health` 확인 | 부분 성공 | HTTP 200 응답 확인. 8000 포트에 기존 프로세스가 있어 새 uvicorn 프로세스는 즉시 종료됨 |

## P2.5 검증 내용

- 직접 입력 텍스트가 공백 정규화 후 퀴즈 생성기에 전달되는지 검증했습니다.
- 웹 HTML에서 `nav`, `footer`, `script`, `style` 등 비본문 요소가 제거되는지 검증했습니다.
- 웹 본문 12,000자 초과 시 `CONTENT_TRUNCATED` warning이 반환되는지 검증했습니다.
- YouTube 영어/자동 자막 warning이 응답에 유지되는지 검증했습니다.
- 이미지 moderation의 `action=allow/review/block` 정책 중 low와 medium/high 매핑을 mock으로 검증했습니다.
- in-memory 일일 보호 제한 초과 시 429와 `AI_DAILY_USAGE_LIMIT_EXCEEDED`가 반환되는지 검증했습니다.

## P2.5 미실행 / 대체 검증

- 실제 OpenAI 호출: 비용 발생 가능성이 있어 수행하지 않고 fake OpenAI client와 monkeypatch 테스트로 대체했습니다.
- 실제 외부 웹사이트/YouTube 호출: 네트워크와 외부 콘텐츠 상태에 의존하므로 mock 테스트로 대체했습니다.
- 실제 medium/high 유해 이미지 샘플 검증: 안전성과 테스트 데이터 취급 문제로 수행하지 않았습니다.
- Swagger 수동 검증: 이번 단계에서는 pytest와 `/health` 확인으로 대체했습니다.

## 2026-06-10 - Pre-Deployment Local Stabilization

| 명령 | 결과 | 비고 |
|---|---|---|
| `git status --short` | 성공 | 변경 파일 확인 |
| `.\.venv\Scripts\python.exe -m pytest` | 성공 | 25 passed, 50 warnings |
| `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title); print(len(app.openapi().get('paths', {})))"` | 성공 | FastAPI app import와 OpenAPI schema 생성 확인, path 5개 |
| local server smoke test on port 8010 | 성공 | `/health` 200, `/docs` 200, auth failure 401 |
| `docker info --format '{{.ServerVersion}}'` | 성공 | Docker engine 29.5.2 |
| `docker build -t ai-server:0.1.0 .` | 성공 | Docker image build 완료 |
| secret pattern scan | 성공 | 실제 secret 패턴 미검출, placeholder만 확인 |

## Pre-Deployment 검증 내용

- `.venv` 기준 전체 pytest를 재실행했습니다.
- 임시 로컬 서버를 8010 포트로 실행해 `/health`, `/docs`, 인증 실패 케이스를 확인했습니다.
- Pydantic schema 설명과 예시를 추가한 뒤 OpenAPI schema 생성이 정상인지 확인했습니다.
- Docker Desktop engine이 실행 중인 상태에서 Docker image build를 재검증했습니다.
- `.gitignore`와 `.dockerignore`가 `.env`, `.env.*`, `.venv`, cache 파일을 제외하는지 확인했습니다.
- README와 curl 예시에 PowerShell 친화적인 `Invoke-RestMethod` 예시를 보강했습니다.

## Pre-Deployment 미실행 / 대체 검증

- 실제 OpenAI 호출: 비용 발생 가능성이 있어 이번 단계에서는 수행하지 않고 기존 mock/fake client 테스트로 대체했습니다.
- 실제 유해 이미지 샘플: 안전성과 테스트 데이터 취급 문제로 사용하지 않았습니다.
- Docker run: 실제 `.env`를 컨테이너에 주입해야 하므로 build 검증으로 대체했습니다.

## 2026-06-10 - Pre-Deployment Hardening

| 명령 | 결과 | 비고 |
|---|---|---|
| `.\.venv\Scripts\python.exe -m pytest` | 성공 | 30 passed, 57 warnings |
| `.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title); print(len(app.openapi().get('paths', {})))"` | 성공 | FastAPI app import와 OpenAPI schema 생성 확인, path 6개 |
| local server smoke test on port 8011 | 성공 | `/health` 200, `/ready` 200, `/docs` 200, auth failure 401, request id echo 확인 |
| `docker build -t ai-server:0.1.0 .` | 성공 | Docker HEALTHCHECK 포함 image build 완료 |
| secret pattern scan | 성공 | 실제 secret 패턴 미검출. 테스트용 placeholder만 확인 |

## Pre-Deployment Hardening 검증 내용

- `/ready` endpoint가 필수 환경변수 readiness를 확인하는지 테스트했습니다.
- 모든 응답에 `X-Request-Id`가 포함되고, 요청 header 값이 유지되는지 테스트했습니다.
- 웹 URL의 localhost/private IP 차단이 `WEB_URL_BLOCKED`로 동작하는지 테스트했습니다.
- 이미지 확장자, MIME type, 파일 header signature 불일치가 `IMAGE_TYPE_NOT_ALLOWED`로 차단되는지 테스트했습니다.
- Dockerfile에 healthcheck를 추가하고 build가 성공하는지 확인했습니다.
- API 응답 샘플, 백엔드 client 예시, 품질 샘플 케이스 문서를 추가했습니다.

## Pre-Deployment Hardening 미실행 / 대체 검증

- 실제 OpenAI 호출: 비용 발생 가능성이 있어 mock/fake client 테스트로 대체했습니다.
- 실제 유해 이미지 샘플: 안전성과 데이터 취급 문제로 사용하지 않았습니다.
- Docker run: 실제 `.env` 주입이 필요하므로 build와 로컬 uvicorn smoke test로 대체했습니다.
## 2026-06-10 - Daily Limit Policy Adjustment

| 명령 | 결과 | 비고 |
|---|---|---|
| `.\.venv\Scripts\python.exe -m pytest` | 성공 | 31 passed, 57 warnings |

## 검증 내용

- `AI_DAILY_REQUEST_LIMIT` 기본값을 100으로 낮췄습니다.
- Quiz generation endpoint는 daily limit 초과 시 `AI_DAILY_USAGE_LIMIT_EXCEEDED`를 반환해야 합니다.
- `/ai/image/moderate`는 daily limit count에서 제외되어야 합니다.
- `/ai/image/moderate`는 endpoint별 `AI_RATE_LIMIT_PER_MINUTE` 보호는 계속 적용받습니다.
- OpenAI 실제 호출은 비용/외부 의존성을 피하기 위해 mock/fake client 테스트로 대체합니다.
