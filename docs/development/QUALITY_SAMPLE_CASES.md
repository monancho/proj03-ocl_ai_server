# Quality Sample Cases

이 문서는 배포 전 수동 품질 검증에 사용할 샘플 유형과 평가 기준을 정리한다. 실제 유해 이미지나 secret은 포함하지 않는다.

## Text Quiz Samples

| Case | 목적 | 기대 확인 |
|---|---|---|
| FastAPI/Pydantic 설명 | 기술 개념 이해 문제 | 단순 문장 찾기보다 이유/적용 문제 포함 |
| 초등 과학 설명 | 쉬운 난이도 검증 | 쉬운 어휘, 정답 1번, 해설 자연스러움 |
| 역사 사건 요약 | 사실 관계 문제 | 시간/원인/결과 구분 |
| 경제 개념 설명 | 오개념 구분 | 보기들이 너무 뻔하지 않음 |
| 긴 문서 12,000자 초과 | 길이 제한 | 직접 입력은 `SOURCE_TEXT_TOO_LONG` |

## Web Quiz Samples

| Case | 목적 | 기대 확인 |
|---|---|---|
| 정적 HTML 문서 | 정상 추출 | title, 본문 추출, 3문항 생성 |
| nav/footer 많은 페이지 | 비본문 제거 | 로그인/약관/광고 문구 제외 |
| 긴 HTML | truncation | `CONTENT_TRUNCATED` warning |
| SPA/동적 페이지 | 한계 표현 | `DYNAMIC_PAGE_LIKELY` warning 또는 추출 실패 |
| localhost/private URL | SSRF 방어 | `WEB_URL_BLOCKED` |

## YouTube Quiz Samples

| Case | 목적 | 기대 확인 |
|---|---|---|
| 한국어 수동 자막 영상 | 정상 생성 | warning 없음 또는 최소 warning |
| 한국어 자동 자막 영상 | 자동 자막 표시 | `YOUTUBE_AUTO_TRANSCRIPT_USED` |
| 영어 자막 영상 | 영어 자막 사용 표시 | `YOUTUBE_EN_TRANSCRIPT_USED` |
| 자막 없는 영상 | 실패 처리 | `YOUTUBE_TRANSCRIPT_NOT_FOUND` |
| 긴 자막 영상 | truncation | `CONTENT_TRUNCATED` |

## Image Moderation Samples

실제 유해 이미지를 저장하거나 커밋하지 않는다. 로컬에서 안전한 정상 이미지와 validation 실패 케이스를 우선 검증한다.

| Case | 목적 | 기대 확인 |
|---|---|---|
| 정상 PNG/JPG/WebP | allow 흐름 | `action=allow` |
| 빈 파일 | validation | `IMAGE_FILE_EMPTY` |
| 5MB 초과 파일 | size validation | `IMAGE_FILE_TOO_LARGE` |
| GIF/TXT 파일 | type validation | `IMAGE_TYPE_NOT_ALLOWED` |
| 확장자/MIME/header 불일치 | spoofing 방어 | `IMAGE_TYPE_NOT_ALLOWED` |

## Quiz Quality Rubric

각 샘플에 대해 1~5점으로 평가한다.

| 항목 | 기준 |
|---|---|
| 근거성 | 입력 자료에 기반하는가 |
| 이해도 | 단순 키워드 찾기보다 이해를 확인하는가 |
| 보기 품질 | 오답이 너무 노골적이지 않은가 |
| 해설 품질 | 자연스럽고 학습자에게 도움이 되는가 |
| 형식 준수 | 3문항, 4보기, `answer_index=0`을 지키는가 |

운영 전 권장 기준:

```text
평균 4점 이상: 통과
평균 3점대: 프롬프트/전처리 개선 검토
평균 2점 이하: 배포 전 수정 필요
```
