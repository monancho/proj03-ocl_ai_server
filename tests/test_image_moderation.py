from fastapi.testclient import TestClient
from types import SimpleNamespace

from app.main import app
from app.services.image_moderation_service import ImageModerationService


client = TestClient(app)


def auth_headers() -> dict[str, str]:
    return {"X-Internal-Api-Key": "test-internal-key"}


def fake_openai_moderation(self, content_type: str, data: bytes):
    return SimpleNamespace(
        results=[
            SimpleNamespace(
                flagged=False,
                categories=SimpleNamespace(),
                category_scores=SimpleNamespace(),
            )
        ]
    )


def test_moderate_image_accepts_png(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")
    monkeypatch.setattr(
        ImageModerationService,
        "_moderate_with_openai",
        fake_openai_moderation,
    )

    response = client.post(
        "/ai/image/moderate",
        headers=auth_headers(),
        files={"image": ("sample.png", b"not-a-real-image-but-non-empty", "image/png")},
    )

    body = response.json()
    assert response.status_code == 200
    assert body == {
        "success": True,
        "data": {
            "allowed": True,
            "risk_level": "low",
            "action": "allow",
            "categories": [],
            "message": None,
        },
    }


def test_moderate_image_returns_review_for_medium_risk(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    def medium_risk_moderation(self, content_type: str, data: bytes):
        return SimpleNamespace(
            results=[
                SimpleNamespace(
                    flagged=True,
                    categories=SimpleNamespace(violence=True),
                    category_scores=SimpleNamespace(violence=0.5),
                )
            ]
        )

    monkeypatch.setattr(
        ImageModerationService,
        "_moderate_with_openai",
        medium_risk_moderation,
    )

    response = client.post(
        "/ai/image/moderate",
        headers=auth_headers(),
        files={"image": ("sample.png", b"not-a-real-image-but-non-empty", "image/png")},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["data"]["allowed"] is False
    assert body["data"]["risk_level"] == "medium"
    assert body["data"]["action"] == "review"
    assert body["data"]["message"] == "검토가 필요한 이미지입니다."


def test_moderate_image_rejects_missing_file(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    response = client.post("/ai/image/moderate", headers=auth_headers())

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "IMAGE_FILE_MISSING"


def test_moderate_image_rejects_empty_file(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    response = client.post(
        "/ai/image/moderate",
        headers=auth_headers(),
        files={"image": ("empty.png", b"", "image/png")},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "IMAGE_FILE_EMPTY"


def test_moderate_image_rejects_unsupported_type(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    response = client.post(
        "/ai/image/moderate",
        headers=auth_headers(),
        files={"image": ("sample.gif", b"non-empty", "image/gif")},
    )

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "IMAGE_TYPE_NOT_ALLOWED"


def test_moderate_image_rejects_too_large_file(monkeypatch) -> None:
    monkeypatch.setenv("AI_SERVER_API_KEY", "test-internal-key")

    response = client.post(
        "/ai/image/moderate",
        headers=auth_headers(),
        files={"image": ("large.png", b"a" * (5 * 1024 * 1024 + 1), "image/png")},
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "IMAGE_FILE_TOO_LARGE"
