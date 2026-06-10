# Service Integration Prompts

이 문서는 다른 서비스 백엔드 저장소에서 바로 사용할 수 있는 AI Server 연동 작업 프롬프트를 정리한다.

AI Server image:

```text
ghcr.io/monancho/ocl-ai-server:0.1.0
```

로컬 AI Server 실행 예:

```powershell
docker run --rm `
  --env-file .env `
  -p 8000:8000 `
  ghcr.io/monancho/ocl-ai-server:0.1.0
```

다른 프로세스가 8000 포트를 사용 중이면:

```powershell
docker run --rm `
  --env-file .env `
  -p 8010:8000 `
  ghcr.io/monancho/ocl-ai-server:0.1.0
```

백엔드 공통 환경변수:

```text
AI_SERVER_BASE_URL=http://localhost:8000
AI_SERVER_API_KEY=<AI Server의 AI_SERVER_API_KEY와 동일한 값>
AI_SERVER_TIMEOUT_SECONDS=30
```

중요:

- 백엔드에는 `OPENAI_API_KEY`를 추가하지 않는다.
- `AI_SERVER_API_KEY`는 프론트엔드에 노출하지 않는다.
- secret, token, API key를 로그에 남기지 않는다.
- 실제 배포와 GitHub push는 사용자 승인 전까지 하지 않는다.
- 기존 인증/권한/DB 구조를 훼손하지 않는다.

## 1. 공통 AI Server Client 작업 프롬프트

```text
이 백엔드 저장소에 AI Server 공통 client/service 모듈을 추가해라.

AI Server는 로컬 Docker로 실행 중이라고 가정한다.

AI Server image:
ghcr.io/monancho/ocl-ai-server:0.1.0

백엔드 환경변수:
AI_SERVER_BASE_URL=http://localhost:8000
AI_SERVER_API_KEY=<AI Server의 AI_SERVER_API_KEY와 동일한 값>
AI_SERVER_TIMEOUT_SECONDS=30

중요:
- OPENAI_API_KEY는 백엔드에 추가하지 마라.
- AI_SERVER_API_KEY를 프론트엔드에 노출하지 마라.
- secret 값을 로그에 남기지 마라.
- 기존 백엔드 인증/권한/DB 구조를 훼손하지 마라.
- 실제 배포와 GitHub push는 하지 마라.

작업 범위:
1. AI Server client/service 모듈 추가
2. AI_SERVER_BASE_URL, AI_SERVER_API_KEY, AI_SERVER_TIMEOUT_SECONDS 설정 로딩
3. 공통 header X-Internal-Api-Key 적용
4. JSON API 공통 success/error response 파싱
5. multipart image API 호출 기반 구조 준비
6. timeout 설정 적용
7. network error, timeout, non-2xx 응답 처리
8. AI Server error code를 백엔드 예외 타입 또는 공통 오류로 매핑
9. secret이 로그에 남지 않도록 logging 정책 확인
10. 단위 테스트 추가

AI Server endpoint:
GET /health
GET /ready
POST /ai/quiz/generate/text
POST /ai/quiz/generate/web
POST /ai/quiz/generate/youtube
POST /ai/image/moderate

검증:
- AI Server /health 호출 성공
- AI Server /ready 호출 성공
- 잘못된 AI_SERVER_API_KEY 처리 확인
- timeout/error mapping 테스트 통과

참고 문서:
- AI Server docs/BACKEND_INTEGRATION_GUIDE.md
- AI Server docs/API_SPECIFICATION.md
- AI Server docs/development/API_RESPONSE_SAMPLES.md
- AI Server docs/development/BACKEND_CLIENT_EXAMPLES.md
```

## 2. Quiz Backend 연동 프롬프트

```text
이 Quiz 백엔드 저장소에 AI Server 기반 퀴즈 생성 연동을 추가해라.

전제:
- AI Server는 로컬 Docker로 실행 중이다.
- AI Server image는 ghcr.io/monancho/ocl-ai-server:0.1.0 이다.
- 백엔드는 AI_SERVER_BASE_URL, AI_SERVER_API_KEY, AI_SERVER_TIMEOUT_SECONDS 환경변수를 사용한다.

중요:
- OPENAI_API_KEY는 Quiz 백엔드에 추가하지 마라.
- AI_SERVER_API_KEY를 프론트엔드에 노출하지 마라.
- 사용자 원문 전체와 secret을 로그에 남기지 마라.
- 기존 사용자 인증/권한/DB 구조를 훼손하지 마라.
- 실제 배포와 GitHub push는 하지 마라.

작업 범위:
1. AI Server client/service가 없으면 먼저 추가한다.
2. text quiz 생성 호출을 연결한다.
   - POST /ai/quiz/generate/text
3. web quiz 생성 호출을 연결한다.
   - POST /ai/quiz/generate/web
4. youtube quiz 생성 호출을 연결한다.
   - POST /ai/quiz/generate/youtube
5. 백엔드 기존 quiz 생성 workflow와 연결한다.
6. 사용자 인증/권한 확인 후 AI Server를 호출한다.
7. 사용자별 quota/결제/권한 정책은 백엔드에서 처리한다.
8. AI Server 응답 questions를 검증한다.
   - questions length는 3
   - 각 question options length는 4
   - answer_index는 0
9. source.warning을 백엔드 응답 또는 내부 상태에 반영한다.
10. 생성 결과를 기존 DB schema에 맞게 저장하거나 반환한다.
11. AI Server error code를 사용자 메시지/백엔드 예외로 매핑한다.
12. 단위 테스트와 로컬 end-to-end 테스트를 추가한다.

AI Server quiz error code 처리:
- SOURCE_TEXT_TOO_SHORT: 사용자에게 더 긴 내용을 입력하도록 안내
- SOURCE_TEXT_TOO_LONG: 입력을 줄이도록 안내
- DIFFICULTY_INVALID: 백엔드 validation 버그로 간주
- WEB_URL_INVALID: 올바른 URL 입력 안내
- WEB_URL_BLOCKED: 허용되지 않는 URL 안내
- WEB_CONTENT_EXTRACT_FAILED: 직접 입력 또는 다른 페이지 사용 안내
- YOUTUBE_URL_INVALID: 올바른 YouTube URL 입력 안내
- YOUTUBE_TRANSCRIPT_NOT_FOUND: 자막 있는 영상 사용 안내
- AI_RATE_LIMIT_EXCEEDED: 잠시 후 재시도 안내
- AI_DAILY_USAGE_LIMIT_EXCEEDED: 서비스 일시 제한 안내 또는 운영 알림
- QUIZ_GENERATION_FAILED: 1회 재시도 또는 사용자 안내

검증:
1. AI Server /health, /ready 호출 성공
2. text quiz end-to-end 성공
3. web quiz 정적 HTML URL 테스트 성공 또는 실패 code 정상 처리
4. youtube quiz 자막 있는 영상 테스트 성공 또는 실패 code 정상 처리
5. 짧은 text가 SOURCE_TEXT_TOO_SHORT로 처리됨
6. 잘못된 difficulty가 백엔드 validation에서 차단되거나 DIFFICULTY_INVALID로 처리됨
7. 잘못된 AI_SERVER_API_KEY가 INVALID_API_KEY로 처리됨
8. 저장된 quiz 데이터가 기존 서비스 schema와 맞는지 확인

참고 문서:
- AI Server docs/BACKEND_INTEGRATION_GUIDE.md
- AI Server docs/API_SPECIFICATION.md
- AI Server docs/development/API_RESPONSE_SAMPLES.md
```

## 3. Doodle/Image Backend 연동 프롬프트

```text
이 Doodle/Image 백엔드 저장소에 AI Server 이미지 moderation 연동을 추가해라.

전제:
- AI Server는 로컬 Docker로 실행 중이다.
- AI Server image는 ghcr.io/monancho/ocl-ai-server:0.1.0 이다.
- 백엔드는 AI_SERVER_BASE_URL, AI_SERVER_API_KEY, AI_SERVER_TIMEOUT_SECONDS 환경변수를 사용한다.

중요:
- OPENAI_API_KEY는 Doodle/Image 백엔드에 추가하지 마라.
- AI_SERVER_API_KEY를 프론트엔드에 노출하지 마라.
- 이미지 원본, secret, token을 로그에 남기지 마라.
- 실제 유해 이미지 샘플을 저장소에 추가하지 마라.
- 기존 이미지 저장/업로드 구조를 훼손하지 마라.
- 실제 배포와 GitHub push는 하지 마라.

작업 범위:
1. AI Server client/service가 없으면 먼저 추가한다.
2. 이미지 업로드 workflow에서 저장 전에 AI Server moderation을 호출한다.
   - POST /ai/image/moderate
3. multipart/form-data image field로 파일을 전송한다.
4. 백엔드에서도 파일 크기/확장자/MIME 사전 검증을 유지한다.
5. AI Server action 값을 기준으로 분기한다.
   - action=allow: 업로드/저장 진행
   - action=review: 검토 필요 상태로 저장하거나 업로드 보류
   - action=block: 저장하지 않고 차단
6. allowed, risk_level, categories, message를 백엔드 정책에 맞게 저장/반환한다.
7. medium risk review 상태의 DB status 또는 response 정책을 정의한다.
8. AI Server error code를 백엔드 예외/응답으로 매핑한다.
9. 단위 테스트와 로컬 end-to-end 테스트를 추가한다.

권장 상태값:
- APPROVED: action=allow
- PENDING_REVIEW: action=review
- REJECTED: action=block

AI Server image error code 처리:
- IMAGE_FILE_MISSING: 파일 누락 안내
- IMAGE_FILE_EMPTY: 다른 이미지 선택 안내
- IMAGE_FILE_TOO_LARGE: 이미지 크기 축소 안내
- IMAGE_TYPE_NOT_ALLOWED: jpg/png/webp 사용 안내
- IMAGE_MODERATION_FAILED: 일시적 검사 실패 안내
- AI_RATE_LIMIT_EXCEEDED: 잠시 후 재시도 안내
- AI_DAILY_USAGE_LIMIT_EXCEEDED: 서비스 일시 제한 안내 또는 운영 알림

검증:
1. AI Server /health, /ready 호출 성공
2. 정상 PNG/JPG/WebP 이미지 allow 흐름 확인
3. 빈 파일 IMAGE_FILE_EMPTY 처리 확인
4. 잘못된 확장자 IMAGE_TYPE_NOT_ALLOWED 처리 확인
5. 확장자/MIME/header 불일치 차단 처리 확인
6. action=review mock 또는 fixture 처리 확인
7. action=block mock 또는 fixture 처리 확인
8. 잘못된 AI_SERVER_API_KEY가 INVALID_API_KEY로 처리됨

참고 문서:
- AI Server docs/BACKEND_INTEGRATION_GUIDE.md
- AI Server docs/API_SPECIFICATION.md
- AI Server docs/development/API_RESPONSE_SAMPLES.md
```

## 4. 통합 로컬 검증 프롬프트

```text
AI Server Docker image와 서비스 백엔드의 로컬 end-to-end 검증을 수행해라.

AI Server image:
ghcr.io/monancho/ocl-ai-server:0.1.0

AI Server 실행:
docker run --rm --env-file .env -p 8000:8000 ghcr.io/monancho/ocl-ai-server:0.1.0

백엔드 환경변수:
AI_SERVER_BASE_URL=http://localhost:8000
AI_SERVER_API_KEY=<AI Server의 AI_SERVER_API_KEY와 동일한 값>
AI_SERVER_TIMEOUT_SECONDS=30

중요:
- .env 실제 값과 API Key를 출력하지 마라.
- 실제 유해 이미지 샘플을 사용하지 마라.
- 실제 OpenAI 호출은 최소 횟수로 제한해라.
- GitHub push와 실제 배포는 하지 마라.

검증 범위:
1. AI Server /health 확인
2. AI Server /ready 확인
3. 백엔드에서 AI Server health check 호출 확인
4. text quiz end-to-end 성공 확인
5. web quiz end-to-end 또는 실패 code 정상 처리 확인
6. youtube quiz end-to-end 또는 실패 code 정상 처리 확인
7. image moderation 정상 이미지 allow 확인
8. image validation 실패 케이스 확인
9. 잘못된 AI_SERVER_API_KEY 처리 확인
10. 백엔드 로그에 secret과 사용자 원문 전체가 남지 않는지 확인

완료 후 보고:
1. 성공한 end-to-end 흐름
2. 실패한 흐름과 error code
3. 백엔드 수정 파일
4. 남은 리스크
5. 배포 전 필요한 환경변수/secret 목록
```

## 5. OCL 배포 전 연동 점검 프롬프트

```text
AI Server와 서비스 백엔드의 OCL 배포 전 연동 점검을 수행해라.

전제:
- AI Server image는 ghcr.io/monancho/ocl-ai-server:0.1.0 이다.
- 백엔드는 AI_SERVER_BASE_URL과 AI_SERVER_API_KEY로 AI Server를 호출한다.
- GitHub push 또는 실제 배포는 사용자 최종 승인 전까지 하지 않는다.

점검 항목:
1. AI Server image pull 가능 여부
2. AI Server 컨테이너 /health, /ready 성공 여부
3. 백엔드가 AI Server 네트워크 주소에 접근 가능한지 확인
4. 백엔드 secret에 AI_SERVER_API_KEY 등록 여부 확인
5. 프론트엔드에 AI_SERVER_API_KEY가 노출되지 않는지 확인
6. text quiz end-to-end smoke test
7. image moderation allow smoke test
8. action=review/block 정책의 백엔드 처리 확인
9. warning code 사용자 안내 정책 확인
10. 장애 시 request id를 추적할 수 있는지 확인

완료 후 보고:
1. 배포 가능 여부
2. 미해결 blocker
3. secret/환경변수 확인 사항
4. rollback 또는 재배포 전략
```
