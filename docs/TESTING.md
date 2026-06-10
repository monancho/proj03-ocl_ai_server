# 테스트 기준

## 1. 기본 원칙

- 실제 API Key가 없어도 실행 가능한 테스트를 우선 작성한다.
- 외부 모델 호출은 mock으로 대체할 수 있게 설계한다.
- API 계약, schema, error response, 인증을 우선 검증한다.
- 실제 OpenAI API 호출 검증은 사용자가 `.env`를 준비한 뒤 별도로 수행한다.

## 2. 권장 자동 테스트

```bash
python -m pytest
```

선택 검증:

```bash
python -m ruff check .
python -m mypy app
```

## 3. Health 테스트

- `GET /health`가 200을 반환한다.
- 응답 body에 `status=ok`, `service=ai-server`, `version=0.1.0`이 포함된다.

## 4. Auth 테스트

- `/health`는 인증 없이 접근 가능하다.
- `/ai/*` API는 `X-Internal-Api-Key`가 없으면 401을 반환한다.
- 잘못된 key는 401을 반환한다.
- 올바른 key는 다음 처리 단계로 넘어간다.

## 5. Quiz 테스트

### 직접 입력

- 100자 이상 본문으로 정확히 3문항을 반환한다.
- 각 문항은 보기 4개를 가진다.
- `answer_index`는 항상 0이다.
- 잘못된 difficulty는 `DIFFICULTY_INVALID`를 반환한다.
- 12,000자 초과 직접 입력은 `SOURCE_TEXT_TOO_LONG`을 반환한다.

### 웹사이트

- 정적 HTML 본문을 추출한다.
- 12,000자 초과 시 warning을 포함하고 앞부분만 사용한다.
- 본문 추출 실패 시 `WEB_CONTENT_EXTRACT_FAILED`를 반환한다.

### YouTube

- 유효한 YouTube URL만 허용한다.
- 자막 없는 영상은 `YOUTUBE_TRANSCRIPT_NOT_FOUND`를 반환한다.
- 자막 12,000자 초과 시 warning을 포함한다.

## 6. 이미지 moderation 테스트

- jpg/jpeg/png/webp만 허용한다.
- 빈 파일은 `IMAGE_FILE_EMPTY`를 반환한다.
- 5MB 초과 파일은 `IMAGE_FILE_TOO_LARGE`를 반환한다.
- 허용되지 않는 MIME/확장자는 `IMAGE_TYPE_NOT_ALLOWED`를 반환한다.
- low는 `allowed=true`, medium/high는 `allowed=false`를 반환한다.

## 7. 수동 테스트 기준

Swagger:

```text
http://localhost:8000/docs
```

curl 예시 형식:

```bash
curl http://localhost:8000/health
```

인증이 필요한 API는 다음 header를 포함한다.

```bash
-H "X-Internal-Api-Key: $AI_SERVER_API_KEY"
```

## 8. 실제 API Key가 없을 때의 대체 방식

| 상황 | 대체 검증 |
|---|---|
| OpenAI API Key 없음 | LLM/Moderation service를 mock 처리 |
| YouTube 네트워크 검증 어려움 | transcript extractor를 stub/mock 처리 |
| 웹페이지 fetch 불안정 | 로컬 fixture HTML 사용 |
| Docker 실행 불가 | Docker build 미실행 사유 기록 |

미실행 항목은 완료 보고와 `docs/development/TEST_REPORT.md`에 사유를 남긴다.
