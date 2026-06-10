# 개발 계획 및 체크리스트

## 1. 개발 단계

| 단계 | 작업 | 완료 기준 |
|---:|---|---|
| 1 | FastAPI 프로젝트 초기 세팅 | `/health` 응답 확인 |
| 2 | 환경변수/config 구성 | `OPENAI_API_KEY`, `AI_SERVER_API_KEY`, 모델명 로딩 |
| 3 | 내부 API Key 인증 구현 | 잘못된 Key 요청 401 반환 |
| 4 | 공통 error response 구현 | `success=false`, `code/message` 응답 통일 |
| 5 | 문제 생성 schema 작성 | `Question`, `QuizGenerateResponse` Pydantic 모델 정의 |
| 6 | 직접 입력 문제 생성 구현 | 한국어 4지선다 3문항 반환 |
| 7 | 웹사이트 본문 추출 구현 | 정적 HTML 추출 및 12,000자 제한 적용 |
| 8 | YouTube 자막 추출 구현 | 자막 있는 영상만 처리 |
| 9 | 문제 생성 1회 재시도 구현 | schema 실패 시 재생성 후 실패 처리 |
| 10 | 이미지 moderation API 구현 | multipart 이미지 검사 및 allowed 반환 |
| 11 | Dockerfile 작성 | 이미지 빌드 및 컨테이너 실행 성공 |
| 12 | API 문서/README 정리 | Swagger, curl 예시, 환경변수 설명 포함 |

## 2. 우선순위

| 우선순위 | 기능 |
|---|---|
| P0 | `/health`, API Key 인증, 직접 입력 문제 생성, 이미지 moderation |
| P1 | 웹사이트 본문 추출, YouTube 자막 추출, 공통 오류 코드 |
| P2 | Dockerfile, curl/Postman 예시, README 정리 |
| P2.5 | 규칙 기반 전처리, warning/action 정책, AI 서버 보호 제한 |
| P3 | LangGraph, RAG, 서비스 백엔드 연동, 사용자별 생성 횟수 제한 |

## 3. 테스트 체크리스트

| 분류 | 테스트 항목 |
|---|---|
| Health | `GET /health`가 200과 `status=ok`를 반환하는가 |
| Auth | `X-Internal-Api-Key` 누락/오류 시 401을 반환하는가 |
| Text Quiz | 100자 이상 본문으로 정확히 3문항을 반환하는가 |
| Text Quiz | 각 문항이 4보기이고 `answer_index`가 0인가 |
| Difficulty | 잘못된 difficulty가 `DIFFICULTY_INVALID`를 반환하는가 |
| Web Quiz | 정적 HTML 페이지에서 본문 추출 후 문제를 생성하는가 |
| Web Quiz | 본문 추출 실패 시 `WEB_CONTENT_EXTRACT_FAILED`를 반환하는가 |
| YouTube Quiz | 자막이 있는 영상에서 자막 기반 문제를 생성하는가 |
| YouTube Quiz | 자막 없는 영상에서 `YOUTUBE_TRANSCRIPT_NOT_FOUND`를 반환하는가 |
| Image | jpg/png/webp 이미지를 moderation 처리하는가 |
| Image | 5MB 초과 파일을 `IMAGE_FILE_TOO_LARGE`로 차단하는가 |
| Schema | 모델 응답 구조 오류 시 1회 재시도하는가 |
| Docker | 컨테이너에서 `/health`와 주요 API가 동작하는가 |

## 4. 제출 산출물 체크리스트

- GitHub 저장소 링크
- README.md
- API 명세서 PDF/DOCX 또는 Markdown
- Dockerfile
- `.env.example`
- curl 또는 Postman 테스트 예시
- Swagger 화면 캡처
- 테스트 결과 요약

## 5. README 포함 항목

- 프로젝트 소개
- 핵심 기능
- 기술 스택
- API 목록
- 요청/응답 예시
- 환경변수 예시
- 로컬 실행 방법
- Docker 실행 방법
- 오류 코드 목록
- MVP 제외 범위
- 향후 개선사항

## 6. 포트폴리오 어필 포인트

- 문제 생성 입력 방식을 text/web/youtube로 분리해 API 책임을 명확히 한다.
- AI 출력은 Pydantic schema로 검증하고 실패 시 1회 재시도하도록 설계한다.
- 이미지 moderation을 독립 API로 분리해 향후 두들 서비스 업로드 전에 사용할 수 있게 한다.
- 생성 횟수 제한은 사용자 인증이 필요한 백엔드 서버 책임으로 분리해 AI 서버를 stateless하게 유지한다.
- Docker 이미지 기반 실행을 전제로 운영 서버에 소스코드가 없어도 동작할 수 있게 설계한다.

## 7. 향후 개선사항

| 항목 | 설명 |
|---|---|
| 서비스 연동 | Quiz/Doodle Backend에서 AI 서버 호출 |
| 사용자별 생성 횟수 제한 | 사용자 인증과 DB 기반으로 백엔드 서버에서 구현 |
| AI 서버 보호 제한 | 전체 일일/분당 보호 제한은 in-memory MVP에서 시작하고 운영 환경에서는 공유 저장소 검토 |
| 문제 검수 | 생성 후 정답/보기 중복/난이도 검증 node 추가 |
| LangGraph | 검증/재시도/분기 workflow가 복잡해질 때 도입 |
| RAG | 문서 업로드와 벡터 검색 기반 문제 생성 |
| 관리자 검토 | medium risk 이미지나 문제 품질 낮은 결과를 검토 큐로 전달 |
