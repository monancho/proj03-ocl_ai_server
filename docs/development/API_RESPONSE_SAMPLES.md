# API Response Samples

이 문서는 백엔드 연동과 수동 검증 시 참고할 대표 응답 예시를 정리한다. 예시는 실제 API Key나 secret을 포함하지 않는다.

## Health

```json
{
  "status": "ok",
  "service": "ai-server",
  "version": "0.1.0"
}
```

## Ready

```json
{
  "status": "ready",
  "service": "ai-server",
  "version": "0.1.0"
}
```

필수 환경변수가 없으면:

```json
{
  "success": false,
  "error": {
    "code": "SERVICE_NOT_READY",
    "message": "필수 환경변수 설정이 완료되지 않았습니다."
  }
}
```

## Auth Fail

```json
{
  "success": false,
  "error": {
    "code": "INVALID_API_KEY",
    "message": "허용되지 않은 요청입니다."
  }
}
```

## Text Quiz Success

```json
{
  "success": true,
  "data": {
    "source": {
      "type": "text",
      "title": null,
      "url": null,
      "warning": null
    },
    "questions": [
      {
        "question": "FastAPI가 API 서버 구현에 적합한 이유는 무엇인가요?",
        "options": [
          "요청과 응답 검증, 자동 문서화를 지원하기 때문입니다.",
          "브라우저 화면을 직접 렌더링하기 때문입니다.",
          "데이터베이스를 자동으로 생성하기 때문입니다.",
          "이미지 파일을 자동으로 압축하기 때문입니다."
        ],
        "answer_index": 0,
        "explanation": "FastAPI는 Pydantic 기반 검증과 Swagger UI를 제공해 API 개발과 테스트를 쉽게 합니다."
      }
    ],
    "usage": {
      "question_count": 3,
      "input_chars": 420
    }
  }
}
```

## Web Quiz With Warning

```json
{
  "success": true,
  "data": {
    "source": {
      "type": "web",
      "title": "문서 제목",
      "url": "https://example.com/article",
      "warning": "CONTENT_TRUNCATED,NO_MAIN_CONTENT_FOUND"
    },
    "questions": [],
    "usage": {
      "question_count": 3,
      "input_chars": 12000
    }
  }
}
```

## YouTube Quiz With Warning

```json
{
  "success": true,
  "data": {
    "source": {
      "type": "youtube",
      "title": null,
      "url": "https://www.youtube.com/watch?v=VIDEO_ID",
      "warning": "YOUTUBE_EN_TRANSCRIPT_USED,YOUTUBE_AUTO_TRANSCRIPT_USED"
    },
    "questions": [],
    "usage": {
      "question_count": 3,
      "input_chars": 3200
    }
  }
}
```

## Image Allow

```json
{
  "success": true,
  "data": {
    "allowed": true,
    "risk_level": "low",
    "action": "allow",
    "categories": [],
    "message": null
  }
}
```

## Image Review

```json
{
  "success": true,
  "data": {
    "allowed": false,
    "risk_level": "medium",
    "action": "review",
    "categories": ["violence"],
    "message": "검토가 필요한 이미지입니다."
  }
}
```

## Image Block

```json
{
  "success": true,
  "data": {
    "allowed": false,
    "risk_level": "high",
    "action": "block",
    "categories": ["violence/graphic"],
    "message": "업로드할 수 없는 이미지입니다. 다른 이미지를 선택해 주세요."
  }
}
```

## Validation Error

```json
{
  "success": false,
  "error": {
    "code": "REQUEST_VALIDATION_ERROR",
    "message": "요청 형식이 올바르지 않습니다."
  }
}
```

## Blocked Web URL

```json
{
  "success": false,
  "error": {
    "code": "WEB_URL_BLOCKED",
    "message": "허용되지 않는 웹 URL입니다."
  }
}
```
