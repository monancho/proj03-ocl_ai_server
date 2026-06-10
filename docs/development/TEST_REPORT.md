# Test Report

## 2026-06-10 - P0 Implementation

| 명령 | 결과 | 비고 |
|---|---|---|
| `python -m pip install -r requirements.txt` | 성공 | 테스트 의존성 설치 |
| `python -m pytest` | 성공 | 11 passed, 32 warnings |
| `python -c "from app.main import app; print(app.title)"` | 성공 | FastAPI 앱 import 확인 |
| `python -m uvicorn app.main:app --reload --port 8000` | 미실행 | 장기 실행 서버 대신 import 확인으로 대체 |
| `docker build -t ai-server:0.1.0 .` | 미실행 | P0 범위에 Dockerfile 없음 |

## 검증 내용

- `/health`가 인증 없이 200 응답을 반환하는지 확인했습니다.
- `/ai/*` API가 `X-Internal-Api-Key` 누락/불일치 시 `INVALID_API_KEY`를 반환하는지 확인했습니다.
- 직접 입력 문제 생성 API가 3문항, 4지선다, `answer_index=0` 응답 구조를 반환하는지 확인했습니다.
- 잘못된 난이도와 12,000자 초과 입력 오류를 확인했습니다.
- 이미지 moderation API의 누락, 빈 파일, 허용되지 않는 형식, 5MB 초과, 정상 png 요청을 확인했습니다.

## 미검증 항목

- 실제 OpenAI 퀴즈 생성 호출: 실제 `OPENAI_API_KEY`가 필요하므로 stub 테스트로 대체했습니다.
- 실제 OpenAI 이미지 moderation 호출: 실제 `OPENAI_API_KEY`가 필요하므로 stub 테스트로 대체했습니다.
- Docker build: Dockerfile이 P2 범위라 이번 P0에서는 실행하지 않았습니다.
