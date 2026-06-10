# 시스템 아키텍처 명세서

## 1. 전체 구조

```text
[Swagger / curl / Postman]
          ↓ HTTP
[FastAPI AI Server]
  ├─ Quiz Generation API
  │   ├─ Text Source
  │   ├─ Web Source Extractor
  │   └─ YouTube Transcript Extractor
  │        ↓
  │   OpenAI SDK Structured Output
  │        ↓
  │   OpenAI Text Model
  │
  └─ Image Moderation API
          ↓
      OpenAI Moderation API
```

MVP에서는 Quiz Service, Doodle Service와 실제 연동하지 않는다. AI 서버는 독립 실행 가능한 API 서버로 구현하고, API 문서와 수동 테스트로 동작을 검증한다.

## 2. 기술별 책임

| 기술 | 책임 | 저장 여부 |
|---|---|---|
| FastAPI | REST API, Swagger, 요청 라우팅 | 없음 |
| Pydantic | Request/Response schema 검증 | 없음 |
| OpenAI SDK Structured Output | 문제 생성 structured output 처리 | 없음 |
| OpenAI Text Model | 문제 생성 | 외부 API |
| OpenAI Moderation API | 이미지 유해성 분류 | 외부 API |
| httpx | 웹페이지 fetch, 외부 API 호출 | 없음 |
| YouTube Transcript Library | 자막 추출 | 없음 |
| Docker | 서버 실행 환경 패키징 | 이미지 |

## 3. 내부 모듈 구조

```text
app/
├─ main.py
├─ api/
│  ├─ health.py
│  ├─ quiz.py
│  └─ image.py
├─ schemas/
│  ├─ quiz.py
│  ├─ image.py
│  └─ error.py
├─ services/
│  ├─ quiz_generation_service.py
│  ├─ text_processing_service.py
│  ├─ web_extract_service.py
│  ├─ youtube_extract_service.py
│  └─ image_moderation_service.py
└─ core/
   ├─ config.py
   ├─ auth.py
   ├─ errors.py
   ├─ request_context.py
   └─ rate_limit.py
```

## 4. 문제 생성 처리 구조

| 단계 | 처리 | 실패 시 |
|---:|---|---|
| 1 | 입력 방식별 request 수신 | schema validation 오류 반환 |
| 2 | 입력 검증 및 원문 텍스트 확보 | source별 오류 코드 반환 |
| 3 | 규칙 기반 전처리 후 12,000자 제한 적용 | 직접 입력은 오류, web/youtube는 warning 후 절단 |
| 4 | OpenAI structured output 호출 | 1회 재생성 시도 |
| 5 | Pydantic 구조 검증 | schema 오류 시 1회 재생성 |
| 6 | 3문항/4보기/정답 1번 검증 | 실패 시 `QUIZ_GENERATION_FAILED` |

## 5. 이미지 유해성 검사 처리 구조

| 단계 | 처리 |
|---:|---|
| 1 | multipart/form-data에서 image 파일 수신 |
| 2 | 파일 존재, 크기, MIME type, 확장자 검증 |
| 3 | base64 data URL 또는 image_url 방식으로 moderation 호출 |
| 4 | flagged, category score 기반 `risk_level` 산출 |
| 5 | low는 `action=allow`, medium은 `action=review`, high는 `action=block` 반환 |

## 6. 보안 경계

- AI 서버는 클라이언트 직접 호출을 전제로 하지 않는다.
- 모든 AI 처리 API는 `X-Internal-Api-Key` 헤더를 요구한다.
- `OPENAI_API_KEY`, `AI_SERVER_API_KEY`는 환경변수로만 관리한다.
- 요청 본문, 파일명, URL은 로그에 최소한으로 기록한다.
- 응답에는 `X-Request-Id`를 포함해 요청 추적이 가능하게 한다.
- 이미지 파일은 AI 서버에 영구 저장하지 않는다.

## 7. 모델 선택 기준

| 용도 | 모델 기준 |
|---|---|
| 문제 생성 | `AI_TEXT_MODEL` 환경변수로 분리. 기본 문서값은 `gpt-5.4-mini` |
| 이미지 유해성 검사 | `IMAGE_MODERATION_MODEL` 환경변수로 분리. 기본 문서값은 `omni-moderation-latest` |

실제 구현 시점의 API 사용 가능 여부에 따라 환경변수 값으로 교체 가능하게 설계한다.

## 8. 확장 가능 구조

| 확장 항목 | 도입 시점 | 비고 |
|---|---|---|
| 서비스 백엔드 연동 | AI 서버 단독 검증 후 | Quiz/Doodle Backend에서 AI API 호출 |
| 사용자별 생성 횟수 제한 | 서비스 사용자 인증 도입 후 | 백엔드 서버 책임 |
| AI 서버 보호 제한 | MVP 운영 안정화 | in-memory 전체/endpoint 보호 제한, 재시작 시 초기화 |
| LangGraph | 검증/재시도/분기 workflow가 복잡해질 때 | MVP 제외 |
| RAG | 문서 검색 기반 문제 생성이 필요할 때 | MVP 제외 |
| Queue | 긴 URL/대량 작업이 필요할 때 | Celery/RQ 등 후순위 |
