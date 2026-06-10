# Backend Integration Guide

## 1. 목적

이 문서는 Quiz/Doodle 서비스 백엔드가 Doodle & Quiz AI Server를 호출하기 위해 필요한 연동 계약과 구현 지침을 정리한다.

AI Server는 최종 사용자와 직접 통신하지 않는다. 서비스 백엔드는 사용자 인증, 권한, 사용량 정책, DB 저장을 담당하고, AI Server는 내부 API로 문제 생성과 이미지 moderation 결과만 반환한다.

```text
Frontend
  -> Service Backend
      -> AI Server
          -> OpenAI API
```

## 2. 백엔드가 준비해야 하는 환경변수

서비스 백엔드는 AI Server 호출용 설정을 별도로 관리해야 한다.

| 변수 | 필수 | 설명 |
|---|---:|---|
| `AI_SERVER_BASE_URL` | 예 | AI Server base URL. 예: `http://ai-server:8000` |
| `AI_SERVER_API_KEY` | 예 | AI Server의 `AI_SERVER_API_KEY`와 동일한 내부 인증 key |
| `AI_SERVER_TIMEOUT_SECONDS` | 권장 | 백엔드에서 AI Server 호출 시 사용할 timeout |

보안 주의:

- `AI_SERVER_API_KEY`는 프론트엔드에 전달하지 않는다.
- request/response 로그에 API key를 남기지 않는다.
- 운영 환경에서는 secret manager 또는 배포 플랫폼 secret으로 관리한다.

## 3. 공통 호출 규칙

모든 AI API 호출에는 다음 header를 포함한다.

```text
X-Internal-Api-Key: <AI_SERVER_API_KEY>
```

모든 응답에는 추적용 `X-Request-Id` header가 포함된다. 백엔드는 장애 분석을 위해 이 값을 로그에 남길 수 있지만, API key나 사용자 원문 전체는 로그에 남기지 않는다.

JSON API는 다음 header를 함께 사용한다.

```text
Content-Type: application/json
```

권장 timeout:

| API | 권장 timeout |
|---|---:|
| text quiz | 30초 |
| web quiz | 45초 |
| youtube quiz | 45초 |
| image moderation | 20초 |

백엔드 retry 정책:

- 사용자 요청 단위에서 무제한 retry를 하지 않는다.
- 401, 400, 413, 415는 retry하지 않는다.
- 422는 입력/자료 문제이므로 기본적으로 retry하지 않는다.
- 429는 잠시 후 재시도 또는 사용자 안내로 처리한다.
- 502는 1회 정도만 재시도할 수 있으나, AI Server 내부에서도 quiz schema 오류에 대해 1회 재시도를 수행한다.

## 4. 응답 처리 기준

성공 응답:

```json
{
  "success": true,
  "data": {}
}
```

실패 응답:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자 메시지"
  }
}
```

백엔드는 `success=false`이면 `error.code` 기준으로 분기한다. `message`는 사용자 노출이 가능하지만, 서비스 톤에 맞게 백엔드에서 다시 매핑해도 된다.

## 5. Quiz Backend 연동

### 5.1 직접 입력 문제 생성

Endpoint:

```text
POST /ai/quiz/generate/text
```

Request:

```json
{
  "content": "100자 이상의 학습 텍스트",
  "difficulty": "beginner"
}
```

백엔드 처리 흐름:

```text
사용자 인증/권한 확인
-> 사용자별 생성 quota 확인
-> 입력 텍스트 길이와 금지 입력 사전 검증
-> AI Server 호출
-> success=true면 questions 검증
-> DB 저장 또는 사용자에게 반환
-> 사용자 사용량 차감/기록
```

주의:

- AI Server는 사용자별 quota를 관리하지 않는다.
- 백엔드가 사용자별 일일/월간 생성 횟수, 결제 플랜, 남은 횟수를 관리한다.
- AI Server의 `usage.input_chars`는 전처리 후 실제 사용된 글자 수다.

### 5.2 웹사이트 문제 생성

Endpoint:

```text
POST /ai/quiz/generate/web
```

Request:

```json
{
  "url": "https://example.com/article",
  "difficulty": "intermediate"
}
```

백엔드 처리 흐름:

```text
URL 형식 사전 검증
-> 금지 도메인/사설망 URL 차단 검토
-> AI Server 호출
-> source.warning 확인
-> questions 검증 후 저장/반환
```

`source.warning` 예시:

| Warning | 백엔드 권장 처리 |
|---|---|
| `CONTENT_TRUNCATED` | 사용자에게 긴 자료 일부만 사용됨을 안내 |
| `NO_MAIN_CONTENT_FOUND` | 결과 품질 낮을 수 있음을 안내 |
| `DYNAMIC_PAGE_LIKELY` | 동적 페이지라 본문 추출이 불완전할 수 있음을 안내 |

보안 권장:

- 백엔드에서 사설 IP, localhost, metadata URL 같은 SSRF 위험 URL 차단을 검토한다.
- AI Server MVP는 정적 HTML만 처리한다.

### 5.3 YouTube 문제 생성

Endpoint:

```text
POST /ai/quiz/generate/youtube
```

Request:

```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "difficulty": "advanced"
}
```

백엔드 처리 흐름:

```text
YouTube URL 사전 검증
-> 영상 정책/길이 정책 확인
-> AI Server 호출
-> source.warning 확인
-> questions 검증 후 저장/반환
```

`source.warning` 예시:

| Warning | 백엔드 권장 처리 |
|---|---|
| `CONTENT_TRUNCATED` | 긴 자막 일부만 사용됨을 안내 |
| `YOUTUBE_AUTO_TRANSCRIPT_USED` | 자동 자막 기반이라 품질이 낮을 수 있음을 안내 |
| `YOUTUBE_EN_TRANSCRIPT_USED` | 영어 자막 기반으로 한국어 문제가 생성됐음을 안내 |

MVP 제외:

- 음성 다운로드
- Whisper
- 자막 없는 영상 처리

## 6. Doodle Backend 이미지 moderation 연동

Endpoint:

```text
POST /ai/image/moderate
```

Request:

```text
multipart/form-data
image=<file>
```

백엔드 처리 흐름:

```text
사용자 인증/권한 확인
-> 이미지 확장자/크기 사전 검증
-> AI Server moderation 호출
-> action 기준 분기
-> allow면 업로드/저장 진행
-> review면 보류 상태 저장 또는 재업로드 안내
-> block이면 저장하지 않고 차단
```

Action 처리 정책:

| action | allowed | 권장 백엔드 처리 |
|---|---:|---|
| `allow` | true | 업로드 진행 |
| `review` | false | 검토 필요 상태로 보류하거나 재업로드 안내 |
| `block` | false | 업로드 차단 |

권장 DB 상태 예시:

| 상태 | 의미 |
|---|---|
| `APPROVED` | moderation 통과 |
| `PENDING_REVIEW` | medium risk 검토 필요 |
| `REJECTED` | high risk 차단 |

주의:

- AI Server는 이미지를 영구 저장하지 않는다.
- 실제 이미지 저장 여부와 저장 위치는 Doodle Backend가 결정한다.
- 실제 유해 이미지 원본을 로그에 남기지 않는다.

## 7. 공통 Error Code 처리

| Code | 백엔드 처리 |
|---|---|
| `INVALID_API_KEY` | 서버 설정 오류로 간주하고 운영 알림 |
| `SOURCE_TEXT_TOO_SHORT` | 사용자에게 더 긴 내용을 입력하도록 안내 |
| `SOURCE_TEXT_TOO_LONG` | 입력을 줄이도록 안내 |
| `DIFFICULTY_INVALID` | 백엔드 validation 버그로 간주 |
| `WEB_URL_INVALID` | 올바른 URL 입력 안내 |
| `WEB_CONTENT_EXTRACT_FAILED` | 다른 페이지 또는 직접 입력 사용 안내 |
| `YOUTUBE_URL_INVALID` | 올바른 YouTube URL 입력 안내 |
| `YOUTUBE_TRANSCRIPT_NOT_FOUND` | 자막 있는 영상 사용 안내 |
| `IMAGE_FILE_MISSING` | 업로드 파일 확인 안내 |
| `IMAGE_FILE_EMPTY` | 다른 이미지 선택 안내 |
| `IMAGE_FILE_TOO_LARGE` | 이미지 크기 축소 안내 |
| `IMAGE_TYPE_NOT_ALLOWED` | jpg/png/webp 사용 안내 |
| `AI_DAILY_USAGE_LIMIT_EXCEEDED` | 잠시 후 또는 다음날 재시도 안내, 운영 알림 검토 |
| `AI_RATE_LIMIT_EXCEEDED` | 잠시 후 재시도 안내 |
| `QUIZ_GENERATION_FAILED` | 1회 재시도 또는 사용자 안내 |
| `IMAGE_MODERATION_FAILED` | 업로드 일시 실패 안내 |

## 8. 백엔드 클라이언트 구현 권장 사항

AI Server 호출 코드는 백엔드 내부에 전용 client/service로 분리한다.

권장 인터페이스:

```text
AiServerClient.generateTextQuiz(content, difficulty)
AiServerClient.generateWebQuiz(url, difficulty)
AiServerClient.generateYoutubeQuiz(url, difficulty)
AiServerClient.moderateImage(file)
```

권장 처리:

- base URL과 API key는 환경변수에서 읽는다.
- API key는 로그에 남기지 않는다.
- timeout을 endpoint별로 설정한다.
- 공통 response wrapper를 검증한다.
- `success=false`면 error code로 예외를 매핑한다.
- OpenAI key는 서비스 백엔드가 알 필요 없다.

## 9. 로컬 연동 테스트 순서

1. AI Server 실행:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

2. 백엔드 `.env` 또는 local config 설정:

```text
AI_SERVER_BASE_URL=http://127.0.0.1:8000
AI_SERVER_API_KEY=<AI Server와 동일한 내부 key>
```

3. 백엔드에서 `/health` 확인:

```text
GET ${AI_SERVER_BASE_URL}/health
```

4. 잘못된 key로 401 확인.

5. 정상 key로 text quiz와 image moderation 최소 1회 확인.

6. 실패 케이스 확인:

- 짧은 text
- 잘못된 difficulty
- 잘못된 URL
- 빈 이미지
- 지원하지 않는 이미지 형식

## 10. 운영 전 체크리스트

- AI Server가 외부 공개망에 직접 노출되지 않는지 확인
- 백엔드만 AI Server에 접근 가능한 네트워크 구성 확인
- `AI_SERVER_API_KEY`가 프론트엔드 번들에 포함되지 않는지 확인
- 백엔드에서 사용자별 quota와 결제/권한 정책 구현
- 백엔드에서 AI Server timeout과 error code 매핑 구현
- 이미지 `review` 상태 처리 정책 확정
- warning code를 사용자에게 어떻게 안내할지 결정
- AI Server health check와 로그 수집 설정
- 운영 Swagger 접근 제한 검토
