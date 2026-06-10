# Troubleshooting

## 현재 상태

초기 부트스트랩 단계라 실제 런타임 오류 사례는 없다.

## 예상 이슈

| 이슈 | 원인 | 대응 |
|---|---|---|
| OpenAI 호출 실패 | `OPENAI_API_KEY` 없음 또는 잘못된 값 | 사용자가 `.env`에 실제 값을 등록. 로그에 key 출력 금지 |
| 내부 API 인증 실패 | `X-Internal-Api-Key` 누락/불일치 | `.env`의 `AI_SERVER_API_KEY`와 요청 header 확인 |
| 웹 본문 추출 실패 | 동적 렌더링, 로그인 필요 페이지, PDF | MVP 제외 범위로 처리하고 `WEB_CONTENT_EXTRACT_FAILED` 반환 |
| YouTube 자막 없음 | 영상에 사용 가능한 자막 없음 | `YOUTUBE_TRANSCRIPT_NOT_FOUND` 반환 |
| 이미지 업로드 실패 | 형식/크기 제한 위반 | jpg/jpeg/png/webp, 5MB 이하 확인 |
| schema 검증 실패 | AI 출력 구조 불일치 | 1회 재생성 후 실패 응답 반환 |
