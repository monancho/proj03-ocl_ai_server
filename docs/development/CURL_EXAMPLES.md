# curl Test Examples

Base URL:

```bash
BASE_URL=http://localhost:8000
AI_SERVER_API_KEY=your-internal-api-key
```

Replace `AI_SERVER_API_KEY` with the same value configured in `.env`. Do not paste real OpenAI keys into curl examples.

PowerShell users can set placeholders like this without printing secret values:

```powershell
$BASE_URL = "http://localhost:8000"
$AI_SERVER_API_KEY = "your-internal-api-key"
```

## Health

```bash
curl "$BASE_URL/health"
```

## Text Quiz

PowerShell:

```powershell
$body = @{
  content = "FastAPI는 Python 기반 API 서버를 빠르게 만들 수 있는 프레임워크입니다. Pydantic을 사용해 요청과 응답 데이터를 검증하고, 자동으로 OpenAPI 문서를 제공합니다. 테스트와 배포가 쉬운 구조를 갖추고 있어 MVP 서버 구현에 적합합니다."
  difficulty = "beginner"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "$BASE_URL/ai/quiz/generate/text" `
  -Method Post `
  -ContentType "application/json" `
  -Headers @{ "X-Internal-Api-Key" = $AI_SERVER_API_KEY } `
  -Body $body
```

Bash:

```bash
curl -X POST "$BASE_URL/ai/quiz/generate/text" \
  -H "Content-Type: application/json" \
  -H "X-Internal-Api-Key: $AI_SERVER_API_KEY" \
  -d "{\"content\":\"FastAPI는 Python 기반 API 서버를 빠르게 만들 수 있는 프레임워크입니다. Pydantic을 사용해 요청과 응답 데이터를 검증하고, 자동으로 OpenAPI 문서를 제공합니다. 테스트와 배포가 쉬운 구조를 갖추고 있어 MVP 서버 구현에 적합합니다.\",\"difficulty\":\"beginner\"}"
```

## Web Quiz

```bash
curl -X POST "$BASE_URL/ai/quiz/generate/web" \
  -H "Content-Type: application/json" \
  -H "X-Internal-Api-Key: $AI_SERVER_API_KEY" \
  -d "{\"url\":\"https://example.com/article\",\"difficulty\":\"intermediate\"}"
```

## YouTube Quiz

```bash
curl -X POST "$BASE_URL/ai/quiz/generate/youtube" \
  -H "Content-Type: application/json" \
  -H "X-Internal-Api-Key: $AI_SERVER_API_KEY" \
  -d "{\"url\":\"https://www.youtube.com/watch?v=VIDEO_ID\",\"difficulty\":\"advanced\"}"
```

## Image Moderation

PowerShell:

```powershell
Invoke-RestMethod `
  -Uri "$BASE_URL/ai/image/moderate" `
  -Method Post `
  -Headers @{ "X-Internal-Api-Key" = $AI_SERVER_API_KEY } `
  -Form @{ image = Get-Item ".\sample.png" }
```

Bash:

```bash
curl -X POST "$BASE_URL/ai/image/moderate" \
  -H "X-Internal-Api-Key: $AI_SERVER_API_KEY" \
  -F "image=@sample.png"
```

Image moderation response includes an action value:

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

## Invalid API Key Check

```bash
curl -X POST "$BASE_URL/ai/quiz/generate/text" \
  -H "Content-Type: application/json" \
  -H "X-Internal-Api-Key: wrong-key" \
  -d "{\"content\":\"FastAPI는 Python 기반 API 서버를 빠르게 만들 수 있는 프레임워크입니다. Pydantic을 사용해 요청과 응답 데이터를 검증하고, 자동으로 OpenAPI 문서를 제공합니다. 테스트와 배포가 쉬운 구조를 갖추고 있어 MVP 서버 구현에 적합합니다.\",\"difficulty\":\"beginner\"}"
```
