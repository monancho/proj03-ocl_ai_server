# Backend Client Examples

이 문서는 서비스 백엔드에서 AI Server를 호출하는 예시를 정리한다. 실제 API Key는 예시에 포함하지 않는다.

## Common Settings

```text
AI_SERVER_BASE_URL=http://127.0.0.1:8000
AI_SERVER_API_KEY=your-internal-api-key
AI_SERVER_TIMEOUT_SECONDS=30
```

공통 header:

```text
X-Internal-Api-Key: <AI_SERVER_API_KEY>
```

## Node.js fetch

```js
export async function generateTextQuiz({ content, difficulty }) {
  const response = await fetch(`${process.env.AI_SERVER_BASE_URL}/ai/quiz/generate/text`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Internal-Api-Key": process.env.AI_SERVER_API_KEY,
    },
    body: JSON.stringify({ content, difficulty }),
  });

  const body = await response.json();
  if (!response.ok || body.success === false) {
    throw new Error(body.error?.code ?? "AI_SERVER_ERROR");
  }
  return body.data;
}
```

## Node.js Multipart Image Moderation

```js
export async function moderateImage(fileBlob) {
  const form = new FormData();
  form.append("image", fileBlob);

  const response = await fetch(`${process.env.AI_SERVER_BASE_URL}/ai/image/moderate`, {
    method: "POST",
    headers: {
      "X-Internal-Api-Key": process.env.AI_SERVER_API_KEY,
    },
    body: form,
  });

  const body = await response.json();
  if (!response.ok || body.success === false) {
    throw new Error(body.error?.code ?? "AI_SERVER_ERROR");
  }
  return body.data;
}
```

## Python httpx

```python
import httpx


class AiServerClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {"X-Internal-Api-Key": self.api_key}

    async def generate_text_quiz(self, content: str, difficulty: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/ai/quiz/generate/text",
                headers={**self._headers(), "Content-Type": "application/json"},
                json={"content": content, "difficulty": difficulty},
            )
        body = response.json()
        if response.status_code >= 400 or body.get("success") is False:
            raise RuntimeError(body.get("error", {}).get("code", "AI_SERVER_ERROR"))
        return body["data"]
```

## Spring WebClient Sketch

```java
WebClient client = WebClient.builder()
    .baseUrl(aiServerBaseUrl)
    .defaultHeader("X-Internal-Api-Key", aiServerApiKey)
    .build();

Mono<QuizGenerateResponse> response = client.post()
    .uri("/ai/quiz/generate/text")
    .contentType(MediaType.APPLICATION_JSON)
    .bodyValue(Map.of(
        "content", content,
        "difficulty", difficulty
    ))
    .retrieve()
    .bodyToMono(QuizGenerateResponse.class);
```

## Error Mapping

| AI Server code | 백엔드 권장 예외 |
|---|---|
| `INVALID_API_KEY` | Internal configuration error |
| `SOURCE_TEXT_TOO_SHORT` | User input validation error |
| `WEB_URL_BLOCKED` | User input validation error |
| `WEB_CONTENT_EXTRACT_FAILED` | Source extraction error |
| `YOUTUBE_TRANSCRIPT_NOT_FOUND` | Source extraction error |
| `IMAGE_TYPE_NOT_ALLOWED` | User upload validation error |
| `AI_RATE_LIMIT_EXCEEDED` | Retry later |
| `AI_DAILY_USAGE_LIMIT_EXCEEDED` | Service temporarily unavailable |
| `QUIZ_GENERATION_FAILED` | AI generation error |
| `IMAGE_MODERATION_FAILED` | AI moderation error |
