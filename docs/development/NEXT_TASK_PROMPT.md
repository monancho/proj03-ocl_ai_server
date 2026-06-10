# P0 구현 시작 프롬프트

너는 이 저장소의 개발 에이전트다.

이번 작업은 **Doodle & Quiz AI Server MVP의 P0 구현**이다.

작업 전 반드시 다음 문서를 읽어라.

1. `AGENTS.md`
2. `docs/DOCUMENT_INDEX.md`
3. `docs/REQUIREMENTS.md`
4. `docs/FUNCTIONAL_SPECIFICATION.md`
5. `docs/API_SPECIFICATION.md`
6. `docs/ARCHITECTURE.md`
7. `docs/DEVELOPMENT_PLAN_CHECKLIST.md`
8. `docs/TESTING.md`
9. `docs/development/AI_ASSISTED_DEVELOPMENT.md`

## 작업 전 확인

먼저 현재 상태를 확인해라.

```bash
pwd
ls
git status --short
find . -maxdepth 3 -type f | sort
```

사용자 변경으로 보이는 파일은 임의로 삭제하거나 되돌리지 마라.

## 이번 P0 목표

다음만 구현해라.

1. FastAPI 프로젝트 초기 세팅
2. `GET /health`
3. 환경변수 config
4. 내부 API Key 인증
5. 공통 error response
6. 기본 Pydantic schema 틀
7. 직접 입력 문제 생성 API의 기본 구조
8. 이미지 moderation API의 기본 구조
9. 최소 pytest 테스트
10. 작업 로그 갱신

## 이번 P0에서 구현할 endpoint

```text
GET  /health
POST /ai/quiz/generate/text
POST /ai/image/moderate
```

웹사이트 문제 생성과 YouTube 문제 생성은 이번 P0에서 완성하지 말고, 라우터/스키마 확장 가능성만 고려해라.

## 구현 기준

### `/health`

인증 없이 접근 가능해야 한다.

응답:

```json
{
  "status": "ok",
  "service": "ai-server",
  "version": "0.1.0"
}
```

### 인증

`/health`를 제외한 AI API는 다음 header를 검증해야 한다.

```text
X-Internal-Api-Key: <AI_SERVER_API_KEY>
```

누락 또는 불일치 시:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_API_KEY",
    "message": "허용되지 않은 요청입니다."
  }
}
```

### 공통 응답

성공:

```json
{
  "success": true,
  "data": {}
}
```

실패:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자 메시지"
  }
}
```

### 직접 입력 문제 생성

이번 P0에서는 전체 LLM 품질 구현보다 구조를 우선한다.

- request validation
- difficulty validation
- 12,000자 제한
- 문제 생성 service 인터페이스
- LLM 호출부는 실제 API Key가 없을 때 테스트 가능하도록 mock/stub 가능하게 설계
- 결과 schema는 한국어 4지선다 3문항, `answer_index=0` 검증 구조를 준비

### 이미지 moderation

이번 P0에서는 다음을 우선 구현한다.

- multipart/form-data 수신
- image field 필수 검증
- 빈 파일 검증
- jpg/jpeg/png/webp 허용
- 5MB 제한
- moderation service 인터페이스
- 실제 OpenAI 호출부는 mock/stub 가능하게 분리

## 보안 규칙

절대 하지 마라.

- `.env` 실제 값 작성
- API Key 생성
- secret 출력
- secret 커밋
- OpenAI API Key 노출
- 내부 API Key 노출
- 외부 서비스 생성
- 실제 배포
- GitHub push

`.env.example`에는 placeholder만 유지한다.

## 생성/수정 가능 파일

필요한 범위에서 다음 파일을 생성/수정할 수 있다.

```text
app/main.py
app/api/health.py
app/api/quiz.py
app/api/image.py
app/core/config.py
app/core/auth.py
app/core/errors.py
app/schemas/error.py
app/schemas/quiz.py
app/schemas/image.py
app/services/quiz_generation_service.py
app/services/image_moderation_service.py
tests/test_health.py
tests/test_auth.py
tests/test_quiz_text.py
tests/test_image_moderation.py
requirements.txt
README.md
docs/development/AI_ASSISTED_DEVELOPMENT_LOG.md
docs/development/TEST_REPORT.md
```

## 검증

가능하면 다음을 실행해라.

```bash
python -m pytest
```

서버 import 확인이 필요하면 다음도 실행해라.

```bash
uvicorn app.main:app --reload --port 8000
```

실제 OpenAI API Key가 없어 외부 모델 호출 검증이 불가능하면 mock 테스트로 대체하고 미실행 사유를 기록해라.

## Git 규칙

작업 전후로 다음을 실행해라.

```bash
git status --short
```

가능하면 적절한 단위로 commit해라.

commit message 예시:

```text
feat: implement p0 ai server foundation
```

단, push는 하지 마라.

금지:

- push
- force push
- hard reset
- rebase
- amend
- 사용자 변경 파일 되돌리기

## 작업 로그

작업 후 다음 파일을 갱신해라.

```text
docs/development/AI_ASSISTED_DEVELOPMENT_LOG.md
docs/development/TEST_REPORT.md
```

## 완료 보고

작업이 끝나면 한국어로 다음 형식으로 보고해라.

```md
## 작업 완료 보고

### 1. 변경 요약
- 

### 2. 생성/수정 파일
- 

### 3. 실행한 명령
- 

### 4. 검증 결과
- 

### 5. 미실행/실패 사유
- 

### 6. 보안 확인
- `.env` 실제 값 작성 여부:
- secret 출력 여부:
- secret 커밋 가능성:
- push 수행 여부:

### 7. 리스크 / 누락
- 

### 8. 다음 작업
- P1 구현: 웹사이트 본문 추출, YouTube 자막 추출, 문제 생성 1회 재시도, 공통 오류 코드 정리

### 9. 다음 작업 추천 프롬프트
```text
바로 이어서 붙여넣을 수 있는 P1 작업 프롬프트
```
```

이제 P0 범위만 구현하고, P1/P2 작업은 시작하지 마라.
