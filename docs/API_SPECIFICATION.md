# API 명세서

## 1. 공통 계약

| 항목 | 내용 |
|---|---|
| Base URL | 로컬 예시: `http://localhost:8000` |
| Content-Type | JSON API는 `application/json`, 이미지 API는 `multipart/form-data` |
| Auth Header | `X-Internal-Api-Key: <AI_SERVER_API_KEY>` |
| 성공 형식 | `{ "success": true, "data": ... }` |
| 실패 형식 | `{ "success": false, "error": { "code": string, "message": string } }` |
| Request ID | 모든 응답은 `X-Request-Id` header를 포함한다. 요청 header에 있으면 같은 값을 반환한다. |
| 문제 생성 고정값 | 한국어, 4지선다, 3문항, 정답 1번, `answer_index=0` |

## 2. API 목록

| Method | Endpoint | Auth | 역할 |
|---|---|---|---|
| GET | `/health` | 없음 | 서버 상태 확인 |
| GET | `/ready` | 없음 | 필수 환경변수 readiness 확인 |
| POST | `/ai/quiz/generate/text` | 필요 | 직접 입력 기반 3문항 생성 |
| POST | `/ai/quiz/generate/web` | 필요 | 웹사이트 본문 기반 3문항 생성 |
| POST | `/ai/quiz/generate/youtube` | 필요 | YouTube 자막 기반 3문항 생성 |
| POST | `/ai/image/moderate` | 필요 | 이미지 유해성 검사 |

## 3. `GET /health`

서버가 실행 중인지 확인한다. 인증이 필요 없다.

Response 200:

```json
{
  "status": "ok",
  "service": "ai-server",
  "version": "0.1.0"
}
```

## 4. `GET /ready`

배포 환경에서 필수 설정값이 준비되었는지 확인한다. 인증이 필요 없다. secret 값은 반환하지 않는다.

Response 200:

```json
{
  "status": "ready",
  "service": "ai-server",
  "version": "0.1.0"
}
```

Response 503:

```json
{
  "success": false,
  "error": {
    "code": "SERVICE_NOT_READY",
    "message": "필수 환경변수 설정이 완료되지 않았습니다."
  }
}
```

## 5. `POST /ai/quiz/generate/text`

직접 입력 설명 또는 본문을 기반으로 3문항을 생성한다.

Request:

```json
{
  "content": "React의 useState는 컴포넌트 상태를 관리하기 위한 Hook입니다...",
  "difficulty": "beginner"
}
```

Response 200:

```json
{
  "success": true,
  "data": {
    "source": {
      "type": "text",
      "title": null,
      "url": null,
      "warning": null
    },
    "questions": [
      {
        "question": "useState의 주요 목적은 무엇인가?",
        "options": ["상태 관리", "라우팅 처리", "스타일 적용", "서버 배포"],
        "answer_index": 0,
        "explanation": "useState는 React 컴포넌트 내부 상태를 관리하는 Hook입니다."
      }
    ],
    "usage": {
      "question_count": 3,
      "input_chars": 1200
    }
  }
}
```

검증 규칙:

| 필드 | 타입 | 필수 | 규칙 |
|---|---|---:|---|
| `content` | string | 예 | trim 후 100자 이상 권장, 최대 12,000자 |
| `difficulty` | string | 예 | `beginner`/`intermediate`/`advanced` |

## 6. `POST /ai/quiz/generate/web`

웹사이트 URL에서 본문을 추출한 뒤 3문항을 생성한다.

Request:

```json
{
  "url": "https://example.com/article",
  "difficulty": "intermediate"
}
```

Response 200:

```json
{
  "success": true,
  "data": {
    "source": {
      "type": "web",
      "title": "페이지 제목",
      "url": "https://example.com/article",
      "warning": "CONTENT_TRUNCATED"
    },
    "questions": [],
    "usage": {
      "question_count": 3,
      "input_chars": 12000
    }
  }
}
```

규칙:

- URL은 `http` 또는 `https`만 허용한다.
- `localhost`, 사설 IP, link-local, metadata IP 등 SSRF 위험 URL은 차단한다.
- PDF, 로그인 필요 페이지, 동적 렌더링 페이지는 MVP 제외다.
- 본문 추출 실패 시 `WEB_CONTENT_EXTRACT_FAILED`를 반환한다.
- 전처리된 본문 12,000자 초과 시 `CONTENT_TRUNCATED` warning 포함 후 앞부분 12,000자만 사용한다.
- warning 예시는 `CONTENT_TRUNCATED`, `NO_MAIN_CONTENT_FOUND`, `DYNAMIC_PAGE_LIKELY`이다.

## 7. `POST /ai/quiz/generate/youtube`

YouTube 영상의 자막을 기반으로 3문항을 생성한다.

Request:

```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "difficulty": "advanced"
}
```

규칙:

- `youtube.com/watch` 또는 `youtu.be` URL을 허용한다.
- 자막이 있을 때만 처리한다.
- 자막이 없으면 `YOUTUBE_TRANSCRIPT_NOT_FOUND`를 반환한다.
- 음성 추출/Whisper는 MVP 제외다.
- ko 수동, ko 자동, en 수동/자동 순으로 자막을 시도한다.
- 영어 또는 자동 자막 사용 시 warning을 포함할 수 있다.
- 전처리된 자막 12,000자 초과 시 `CONTENT_TRUNCATED` warning 포함 후 앞부분 12,000자만 사용한다.

## 8. `POST /ai/image/moderate`

이미지 파일을 검사해 서비스 업로드 허용 여부를 반환한다. AI 서버는 이미지를 저장하지 않는다.

Request:

| Field | Type | 필수 | 기준 |
|---|---|---:|---|
| `image` | file | 예 | jpg/jpeg/png/webp, 5MB 이하 |

Response 200 - 허용:

```json
{
  "success": true,
  "data": {
    "allowed": true,
    "risk_level": "low",
    "action": "allow",
    "categories": [],
    "message": null
  }
}
```

Response 200 - 검토 필요:

```json
{
  "success": true,
  "data": {
    "allowed": false,
    "risk_level": "medium",
    "action": "review",
    "categories": ["violence"],
    "message": "검토가 필요한 이미지입니다."
  }
}
```

Response 200 - 차단:

```json
{
  "success": true,
  "data": {
    "allowed": false,
    "risk_level": "high",
    "action": "block",
    "categories": ["violence/graphic"],
    "message": "업로드할 수 없는 이미지입니다. 다른 이미지를 선택해 주세요."
  }
}
```

## 8. 공통 Error Code

| Code | HTTP | 상황 |
|---|---:|---|
| `INVALID_API_KEY` | 401 | 내부 API Key 누락 또는 불일치 |
| `SERVICE_NOT_READY` | 503 | readiness 필수 환경변수 누락 |
| `SOURCE_TEXT_TOO_SHORT` | 400 | 직접 입력 본문이 너무 짧음 |
| `SOURCE_TEXT_TOO_LONG` | 400 | 직접 입력 본문이 너무 김 |
| `DIFFICULTY_INVALID` | 400 | 난이도 값 오류 |
| `WEB_URL_INVALID` | 400 | 웹 URL 형식 오류 |
| `WEB_URL_BLOCKED` | 400 | SSRF 위험 또는 허용되지 않는 웹 URL |
| `WEB_CONTENT_EXTRACT_FAILED` | 422 | 웹 본문 추출 실패 |
| `YOUTUBE_URL_INVALID` | 400 | YouTube URL 형식 오류 |
| `YOUTUBE_TRANSCRIPT_NOT_FOUND` | 422 | 사용 가능한 자막 없음 |
| `IMAGE_FILE_MISSING` | 400 | 이미지 파일 누락 |
| `IMAGE_FILE_EMPTY` | 400 | 빈 이미지 파일 |
| `IMAGE_FILE_TOO_LARGE` | 413 | 이미지 크기 초과 |
| `IMAGE_TYPE_NOT_ALLOWED` | 415 | 지원하지 않는 이미지 형식 |
| `IMAGE_MODERATION_FAILED` | 502 | 이미지 검사 실패 |
| `QUIZ_GENERATION_FAILED` | 502 | 문제 생성 실패 |
| `OUTPUT_SCHEMA_INVALID` | 502 | AI 응답 구조 불일치 |
| `AI_DAILY_USAGE_LIMIT_EXCEEDED` | 429 | Quiz generation daily protection limit exceeded. Image moderation is excluded from the daily count. |
| `AI_RATE_LIMIT_EXCEEDED` | 429 | AI 서버 분당 보호 한도 초과 |

## 9. Warning / Action Code

| Code | 의미 |
|---|---|
| `CONTENT_TRUNCATED` | 전처리된 학습 텍스트가 길어 앞부분만 사용 |
| `NO_MAIN_CONTENT_FOUND` | 웹페이지에서 `main`/`article` 중심 본문 구조를 찾지 못함 |
| `DYNAMIC_PAGE_LIKELY` | 정적 HTML만으로 본문 확보가 어려운 페이지로 의심 |
| `YOUTUBE_AUTO_TRANSCRIPT_USED` | YouTube 자동 자막을 사용 |
| `YOUTUBE_EN_TRANSCRIPT_USED` | 영어 자막을 사용해 한국어 문제를 생성 |
| `allow` | 이미지 자동 허용 |
| `review` | 이미지 검토 필요 |
| `block` | 이미지 자동 차단 |

## 10. 문제 생성 결과 검증 규칙

| 대상 | 규칙 |
|---|---|
| `questions` | 배열 길이는 반드시 3 |
| `question` | 비어 있지 않은 한국어 문자열 |
| `options` | 배열 길이는 반드시 4 |
| `options[0]` | 정답 보기 |
| `answer_index` | 항상 0 |
| `explanation` | 비어 있지 않은 한국어 문자열 |
