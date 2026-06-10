# 배포 및 운영 명세서

## 1. 배포 대상

| 대상 | 배포/실행 위치 | 비고 |
|---|---|---|
| AI Server | Docker container | FastAPI + OpenAI structured output 기반 독립 API 서버 |
| 외부 모델 API | OpenAI API | 문제 생성과 이미지 moderation 호출 |
| 문서 | Markdown/DOCX/PDF | 기획/API/운영/체크리스트 산출물 |

## 2. 로컬 실행 기준

구현 완료 후 다음 방식으로 실행한다.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Windows 환경에서는 다음을 사용한다.

```bash
venv\Scripts\activate
```

## 3. Dockerfile 기준

구현 단계에서 다음 기준으로 Dockerfile을 작성한다.

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 4. Docker 이미지 빌드/실행

```bash
docker build -t ai-server:0.1.0 .
docker run --env-file .env -p 8000:8000 ai-server:0.1.0
```

## 5. 환경변수

| 변수 | 필수 | 설명 |
|---|---:|---|
| `OPENAI_API_KEY` | 예 | 외부 모델 API 호출 Key |
| `AI_SERVER_API_KEY` | 예 | 내부 API 호출 검증용 Key |
| `AI_TEXT_MODEL` | 예 | 문제 생성 모델명. 기본 문서값: `gpt-5.4-mini` |
| `IMAGE_MODERATION_MODEL` | 예 | 이미지 moderation 모델명. 기본 문서값: `omni-moderation-latest` |
| `MAX_SOURCE_CHARS` | 아니오 | 기본 12000 |
| `MAX_IMAGE_SIZE_MB` | 아니오 | 기본 5 |
| `REQUEST_TIMEOUT_SECONDS` | 아니오 | 기본 15 |
| `AI_DAILY_REQUEST_LIMIT` | 아니오 | AI 서버 전체 in-memory 일일 보호 한도. 기본 1000 |
| `AI_RATE_LIMIT_PER_MINUTE` | 아니오 | endpoint별 in-memory 분당 보호 한도. 기본 120 |
| `LOG_LEVEL` | 아니오 | info/debug 등 |

## 6. 보안 정책

- `OPENAI_API_KEY`와 `AI_SERVER_API_KEY`는 GitHub에 커밋하지 않는다.
- 오류 메시지와 로그에 API Key, raw token, private key, 전체 사용자 입력을 포함하지 않는다.
- 이미지 파일은 요청 처리 중에만 사용하고 서버에 영구 저장하지 않는다.
- MVP 단독 테스트 이후 실제 서비스 연동 시 AI 서버는 외부 직접 공개하지 않는다.

## 7. 운영 주의사항

| 항목 | 주의사항 |
|---|---|
| 모델 비용 | 문제 생성 호출은 비용이 발생하므로 `question_count`를 받지 않고 3문항으로 고정한다. |
| 긴 입력 | 웹/YouTube 추출 텍스트는 12,000자까지 사용한다. |
| URL 처리 | fetch timeout을 적용해 서버가 오래 묶이지 않게 한다. |
| Moderation | low는 허용, medium은 검토 필요, high는 차단한다. 사용자 메시지는 상세 카테고리 대신 일반 안내를 사용한다. |
| 사용량 보호 | in-memory 보호 제한은 프로세스 재시작 시 초기화된다. 사용자별 quota와 결제 정책은 백엔드에서 처리한다. |
| Swagger | 운영 공개 시 Swagger 접근 제한을 검토한다. MVP에서는 테스트 편의를 위해 제공한다. |
| Request ID | 모든 응답의 `X-Request-Id`로 장애 요청을 추적한다. 본문과 secret은 로그에 남기지 않는다. |

## 8. 배포 체크리스트

- `.env`에 `OPENAI_API_KEY`, `AI_SERVER_API_KEY` 등록
- `/health` 응답 확인
- `/ready` 응답 확인
- Swagger `/docs` 접근 확인
- text/web/youtube 문제 생성 API 테스트
- 이미지 moderation API 테스트
- 잘못된 API Key 차단 확인
- Docker build 성공 확인
- Docker run 또는 compose up 성공 확인
- 로그에 secret 값이 남지 않는지 확인
