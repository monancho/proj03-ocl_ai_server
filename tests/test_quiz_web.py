from fastapi.testclient import TestClient

from app.main import app
from app.services.quiz_generation_service import QuizGenerationService
from app.services.web_extract_service import WebExtractService


client = TestClient(app)


def auth_headers() -> dict[str, str]:
    return {"X-Internal-Api-Key": "test-internal-key"}


def fake_question_payloads(self, source_text: str, difficulty: str) -> list[dict]:
    return [
        {
            "question": f"웹 테스트 문제 {index}입니다.",
            "options": ["정답", "오답 1", "오답 2", "오답 3"],
            "answer_index": 0,
            "explanation": "테스트용 해설입니다.",
        }
        for index in range(1, 4)
    ]


def test_web_quiz_extracts_static_html(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    monkeypatch.setattr(
        QuizGenerationService,
        "_generate_question_payloads",
        fake_question_payloads,
    )
    html = """
    <html>
      <head><title>테스트 문서</title><style>.hidden { display: none; }</style></head>
      <body>
        <script>console.log("skip")</script>
        <article>
          FastAPI는 API 서버를 빠르게 만들 수 있는 파이썬 프레임워크입니다.
          타입 힌트와 Pydantic을 활용해 요청과 응답을 검증할 수 있습니다.
          Swagger UI를 기본 제공해 API 테스트가 쉽습니다.
          정적 HTML 문서의 본문을 추출해 퀴즈를 만들 수 있습니다.
        </article>
      </body>
    </html>
    """

    async def fake_fetch_html(self, url: str) -> str:
        return html

    monkeypatch.setattr(WebExtractService, "_fetch_html", fake_fetch_html)

    response = client.post(
        "/ai/quiz/generate/web",
        headers=auth_headers(),
        json={"url": "https://example.com/article", "difficulty": "beginner"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["data"]["source"]["type"] == "web"
    assert body["data"]["source"]["title"] == "테스트 문서"
    assert body["data"]["source"]["url"] == "https://example.com/article"
    assert len(body["data"]["questions"]) == 3


def test_web_quiz_rejects_invalid_url(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    response = client.post(
        "/ai/quiz/generate/web",
        headers=auth_headers(),
        json={"url": "ftp://example.com/article", "difficulty": "beginner"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "WEB_URL_INVALID"


def test_web_quiz_blocks_localhost_url(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    response = client.post(
        "/ai/quiz/generate/web",
        headers=auth_headers(),
        json={"url": "http://127.0.0.1:8000/private", "difficulty": "beginner"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "WEB_URL_BLOCKED"


def test_web_quiz_truncates_long_html_with_warning(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    monkeypatch.setattr(
        QuizGenerationService,
        "_generate_question_payloads",
        fake_question_payloads,
    )

    async def fake_fetch_html(self, url: str) -> str:
        return f"<html><body>{'가' * 13000}</body></html>"

    monkeypatch.setattr(WebExtractService, "_fetch_html", fake_fetch_html)

    response = client.post(
        "/ai/quiz/generate/web",
        headers=auth_headers(),
        json={"url": "https://example.com/long", "difficulty": "beginner"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["data"]["usage"]["input_chars"] == 12000
    assert body["data"]["source"]["warning"] == "CONTENT_TRUNCATED,NO_MAIN_CONTENT_FOUND"


def test_web_quiz_removes_navigation_and_footer_text(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    captured = {}

    def capture_question_payloads(self, source_text: str, difficulty: str) -> list[dict]:
        captured["source_text"] = source_text
        return fake_question_payloads(self, source_text, difficulty)

    monkeypatch.setattr(
        QuizGenerationService,
        "_generate_question_payloads",
        capture_question_payloads,
    )

    async def fake_fetch_html(self, url: str) -> str:
        return """
        <html><body>
          <nav>로그인 회원가입 광고 메뉴</nav>
          <main>
            FastAPI는 API 서버를 빠르게 만들 수 있는 파이썬 프레임워크입니다.
            Pydantic으로 요청과 응답을 검증하고 Swagger UI를 제공합니다.
            정적 HTML 본문을 추출해 학습 자료로 사용할 수 있습니다.
            테스트 가능한 API 서버를 구성하는 데 유용합니다.
          </main>
          <footer>회사 소개 이용약관</footer>
        </body></html>
        """

    monkeypatch.setattr(WebExtractService, "_fetch_html", fake_fetch_html)

    response = client.post(
        "/ai/quiz/generate/web",
        headers=auth_headers(),
        json={"url": "https://example.com/article", "difficulty": "beginner"},
    )

    assert response.status_code == 200
    assert "로그인" not in captured["source_text"]
    assert "이용약관" not in captured["source_text"]
