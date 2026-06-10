# AI Assisted Development Guide

## 목적

이 문서는 Codex 또는 AI 개발 에이전트가 Doodle & Quiz AI Server MVP를 이어서 구현할 때 지켜야 할 작업 규칙을 정리한다.

## 작업 원칙

- 구현 전 문서를 먼저 읽는다.
- 작업은 작은 phase 단위로 나눈다.
- 각 phase마다 변경 범위를 명확히 한다.
- MVP 범위를 벗어나는 기능은 명시 요청 없이는 구현하지 않는다.
- secret, token, key, credential은 생성/출력/커밋하지 않는다.
- 작업 후 로그와 완료 보고를 남긴다.

## 작업 전 확인 순서

```bash
pwd
ls
git status --short
find . -maxdepth 3 -type f | sort
```

문서 읽기 순서:

1. `AGENTS.md`
2. `docs/DOCUMENT_INDEX.md`
3. `docs/REQUIREMENTS.md`
4. `docs/FUNCTIONAL_SPECIFICATION.md`
5. `docs/API_SPECIFICATION.md`
6. `docs/ARCHITECTURE.md`
7. `docs/DEPLOYMENT_OPERATION.md`
8. `docs/DEVELOPMENT_PLAN_CHECKLIST.md`
9. `docs/TESTING.md`

## 구현 전 계획

작업 시작 전 다음을 정리한다.

- 이번 phase 목표
- 수정할 파일
- 수정하지 않을 파일
- 검증 명령
- 예상 blocking condition

## 보안 규칙

- `.env` 실제 값 작성 금지
- API Key 생성 금지
- secret 출력 금지
- secret 커밋 금지
- OpenAI API Key 노출 금지
- 내부 API Key 노출 금지
- 외부 서비스 생성 금지
- 실제 배포 금지
- GitHub push 금지

## 사용자 확인이 필요한 상황

- 실제 `.env` 값이 필요한 경우
- OpenAI API Key가 필요한 경우
- 외부 계정 생성이 필요한 경우
- 배포 secret 등록이 필요한 경우
- GitHub push가 필요한 경우
- 실제 운영 서버 배포가 필요한 경우
- MVP 제외 범위 구현이 필요한 경우
- API 계약 변경이 필요한 경우
- 비용이 발생하는 대량 API 호출이 필요한 경우

## 작업 로그 규칙

작업 후 `docs/development/AI_ASSISTED_DEVELOPMENT_LOG.md`에 기록한다.

형식:

```md
## YYYY-MM-DD - 작업명

### 변경 요약
- 

### 변경 파일
- 

### 검증 명령
- 

### 검증 결과
- 

### 미실행/실패 사유
- 

### 리스크/후속 작업
- 
```

## 완료 보고 형식

```md
## 작업 완료 보고

### 1. 변경 요약
- 

### 2. 변경 파일
- 

### 3. 실행한 검증 명령
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
- 

### 9. 다음 작업 추천 프롬프트
```text
...
```
```
