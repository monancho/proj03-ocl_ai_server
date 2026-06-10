# Next Task Prompt

```text
이 저장소의 커밋 이후 제출/푸시 전 최종 확인을 시작해라.

작업 전 AGENTS.md와 docs 문서를 다시 읽고, 현재 구현을 훼손하지 마라.

중요:
- 현재 프로젝트는 .venv를 사용한다.
- 테스트/서버 실행은 반드시 .venv 안에서 실행해라.
- .env 실제 값과 API Key는 절대 출력하지 마라.
- GitHub push는 사용자 최종 승인 전까지 하지 마라.
- force push, hard reset, rebase, amend는 하지 마라.

범위:
1. git status 확인
2. 최근 commit 목록 확인
3. pytest 전체 실행
4. FastAPI app import와 OpenAPI schema 생성 확인
5. Docker build 재확인
6. README, API_SPECIFICATION, CURL_EXAMPLES 최종 확인
7. secret 패턴과 .gitignore/.dockerignore 최종 확인
8. 제출용 변경 요약 작성
9. 사용자가 승인하면 push 수행 여부를 별도로 확인

완료 후 한국어로 보고:
1. 현재 커밋 상태
2. 검증 결과
3. 제출 전 남은 리스크
4. push 전 사용자 확인 사항
```
