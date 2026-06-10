# Doodle & Quiz AI Server MVP

FastAPI 기반 독립 AI API 서버입니다. 텍스트, 정적 웹페이지 본문, YouTube 자막을 한국어 4지선다 3문항으로 변환하고, 업로드 이미지 moderation API를 제공합니다.

현재 구현은 MVP 검증용입니다. 문제 생성은 OpenAI structured output과 Pydantic 검증을 사용하고, 이미지 moderation은 OpenAI Moderation API 호출부로 분리되어 있습니다. 자동 테스트는 비용 방지를 위해 mock/stub으로 검증합니다.

## 기능

| 기능 | Endpoint | 상태 |
|---|---|---|
| Health Check | `GET /health` | 구현 |
| 직접 입력 문제 생성 | `POST /ai/quiz/generate/text` | OpenAI structured output 연동 |
| 웹사이트 문제 생성 | `POST /ai/quiz/generate/web` | 정적 HTML 기반 구현 |
| YouTube 자막 문제 생성 | `POST /ai/quiz/generate/youtube` | 자막 추출 구조 구현 |
| 이미지 유해성 검사 | `POST /ai/image/moderate` | OpenAI moderation 연동 |

## 기술 스택

- Python 3.11+
- FastAPI
- Pydantic / pydantic-settings
- httpx
- youtube-transcript-api
- pytest
- Docker

## 환경변수

`.env.example`을 복사해 `.env`를 만들고 placeholder를 실제 값으로 교체합니다. `.env`는 커밋하지 않습니다.

| 변수 | 설명 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API 호출용 Key |
| `AI_SERVER_API_KEY` | 내부 API 인증용 Key |
| `AI_TEXT_MODEL` | 퀴즈 생성 모델명 |
| `IMAGE_MODERATION_MODEL` | 이미지 moderation 모델명 |
| `MAX_SOURCE_CHARS` | 입력 최대 글자 수, 기본 12000 |
| `MAX_IMAGE_SIZE_MB` | 이미지 최대 크기 MB, 기본 5 |
| `REQUEST_TIMEOUT_SECONDS` | 외부 요청 timeout 초, 기본 15 |
| `AI_DAILY_REQUEST_LIMIT` | AI 서버 전체 in-memory 일일 요청 제한, 기본 1000 |
| `AI_RATE_LIMIT_PER_MINUTE` | endpoint별 in-memory 분당 요청 제한, 기본 120 |
| `LOG_LEVEL` | 로그 레벨 |

## 로컬 실행

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Docker 실행

```bash
docker build -t ai-server:0.1.0 .
docker run --env-file .env -p 8000:8000 ai-server:0.1.0
```

## curl 예시

더 많은 예시는 `docs/development/CURL_EXAMPLES.md`를 참고합니다.

```bash
curl http://localhost:8000/health
```

PowerShell에서 JSON body가 복잡하면 `ConvertTo-Json`을 사용합니다.

```powershell
$BASE_URL = "http://localhost:8000"
$AI_SERVER_API_KEY = "your-internal-api-key"
$body = @{
  content = "FastAPI는 Python 기반 API 서버를 빠르게 만들 수 있는 프레임워크입니다. Pydantic을 사용해 요청과 응답 데이터를 검증하고 자동 문서를 제공합니다."
  difficulty = "beginner"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "$BASE_URL/ai/quiz/generate/text" `
  -Method Post `
  -ContentType "application/json" `
  -Headers @{ "X-Internal-Api-Key" = $AI_SERVER_API_KEY } `
  -Body $body
```

```bash
curl -X POST http://localhost:8000/ai/quiz/generate/text \
  -H "Content-Type: application/json" \
  -H "X-Internal-Api-Key: $AI_SERVER_API_KEY" \
  -d "{\"content\":\"100자 이상의 학습 본문을 입력합니다. FastAPI는 Python 기반 API 서버를 빠르게 만들 수 있는 프레임워크입니다. Pydantic을 사용해 요청과 응답 데이터를 검증하고 자동 문서를 제공합니다.\",\"difficulty\":\"beginner\"}"
```

```bash
curl -X POST http://localhost:8000/ai/image/moderate \
  -H "X-Internal-Api-Key: $AI_SERVER_API_KEY" \
  -F "image=@sample.png"
```

## 테스트

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest
```

현재 테스트는 실제 OpenAI API, 외부 웹사이트, 실제 YouTube API를 호출하지 않고 mock/stub으로 API 계약과 validation을 검증합니다.

## 운영 안정화 정책

- 퀴즈 입력은 공백/중복 줄을 정리한 최종 학습 텍스트 기준으로 12,000자 제한을 적용합니다.
- 웹 추출 warning은 `CONTENT_TRUNCATED`, `NO_MAIN_CONTENT_FOUND`, `DYNAMIC_PAGE_LIKELY` 같은 코드로 반환합니다.
- YouTube 자막은 한국어 수동, 한국어 자동, 영어 수동/자동 순으로 시도하며 영어/자동 자막 사용 시 warning을 반환합니다.
- 이미지 moderation은 `action=allow/review/block`을 반환합니다. `medium` risk는 `review`로 처리합니다.
- AI 서버 보호용 사용량 제한은 in-memory 방식이며 프로세스 재시작 시 초기화됩니다. 사용자별 quota와 결제 정책은 백엔드 서버 책임입니다.

## 오류 응답 형식

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자 메시지"
  }
}
```

주요 error code는 `docs/API_SPECIFICATION.md`를 참고합니다.

## MVP 제외 범위

- 프론트엔드
- DB 저장
- 로그인/회원가입
- Redis, Queue/Celery/RQ
- LangGraph, RAG, Vector DB
- Whisper 음성 인식
- 동적 렌더링 웹페이지 처리
- 실제 서비스 연동
- 실제 배포

## 보안

- `.env` 실제 값은 작성하더라도 커밋하지 않습니다.
- API Key, token, credential은 출력하지 않습니다.
- `/health`를 제외한 AI API는 `X-Internal-Api-Key`를 요구합니다.
- 업로드 이미지는 요청 처리 중 bytes로만 사용하며 서버에 저장하지 않습니다.
