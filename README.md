# Doodle & Quiz AI Server MVP

FastAPI 기반 독립 AI API 서버입니다. P0 단계에서는 health check, 내부 API Key 인증, 텍스트 기반 퀴즈 생성 기본 구조, 이미지 moderation 기본 구조를 제공합니다.

## P0 구현 범위

| 기능 | Endpoint | 상태 |
|---|---|---|
| Health Check | `GET /health` | 구현 |
| 직접 입력 문제 생성 | `POST /ai/quiz/generate/text` | stub 기반 구현 |
| 이미지 유해성 검사 | `POST /ai/image/moderate` | stub 기반 구현 |

웹사이트 문제 생성, YouTube 자막 문제 생성, Dockerfile, 실제 OpenAI 호출은 P1/P2 이후 범위입니다.

## 실행 준비

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

환경변수는 `.env.example`을 참고해 사용자가 직접 `.env`에 작성합니다. 실제 API Key는 저장소에 커밋하지 않습니다.

## 주요 환경변수

| 변수 | 설명 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API 호출용 Key |
| `AI_SERVER_API_KEY` | 내부 API 인증용 Key |
| `AI_TEXT_MODEL` | 퀴즈 생성 모델명 |
| `IMAGE_MODERATION_MODEL` | 이미지 moderation 모델명 |
| `MAX_SOURCE_CHARS` | 직접 입력 최대 글자 수, 기본 12000 |
| `MAX_IMAGE_SIZE_MB` | 이미지 최대 크기 MB, 기본 5 |

## API 예시

```bash
curl http://localhost:8000/health
```

```bash
curl -X POST http://localhost:8000/ai/quiz/generate/text \
  -H "Content-Type: application/json" \
  -H "X-Internal-Api-Key: $AI_SERVER_API_KEY" \
  -d "{\"content\":\"100자 이상의 학습 본문을 입력합니다...\", \"difficulty\":\"beginner\"}"
```

```bash
curl -X POST http://localhost:8000/ai/image/moderate \
  -H "X-Internal-Api-Key: $AI_SERVER_API_KEY" \
  -F "image=@sample.png"
```

## 테스트

```bash
python -m pytest
```

현재 P0 테스트는 실제 OpenAI API를 호출하지 않고 stub 서비스로 API 계약과 validation을 검증합니다.

## 보안

- `.env` 실제 값은 작성하거나 커밋하지 않습니다.
- API Key, token, credential은 출력하지 않습니다.
- `/health`를 제외한 AI API는 `X-Internal-Api-Key`를 요구합니다.
- 업로드 이미지는 요청 처리 중 bytes로만 사용하며 서버에 저장하지 않습니다.
