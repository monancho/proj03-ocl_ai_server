from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.services.text_processing_service import truncate_learning_text


CONTENT_TRUNCATED = "CONTENT_TRUNCATED"
DYNAMIC_PAGE_LIKELY = "DYNAMIC_PAGE_LIKELY"
NO_MAIN_CONTENT_FOUND = "NO_MAIN_CONTENT_FOUND"
SKIP_TAGS = {"script", "style", "noscript", "nav", "footer", "header", "aside", "svg"}
BLOCK_TAGS = {
    "article",
    "main",
    "section",
    "p",
    "div",
    "br",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
}


class StaticHtmlTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: str | None = None
        self._in_title = False
        self._skip_depth = 0
        self._chunks: list[str] = []
        self._title_chunks: list[str] = []
        self.has_main_content_tag = False

    def handle_starttag(self, tag: str, _attrs) -> None:
        normalized = tag.lower()
        if normalized == "title":
            self._in_title = True
        if normalized in {"article", "main"}:
            self.has_main_content_tag = True
        if normalized in SKIP_TAGS:
            self._skip_depth += 1
        if normalized in BLOCK_TAGS and self._skip_depth == 0:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        if normalized == "title":
            self._in_title = False
            title = " ".join(" ".join(self._title_chunks).split())
            self.title = title or None
        if normalized in SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        if normalized in BLOCK_TAGS and self._skip_depth == 0:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self._title_chunks.append(text)
            return
        if self._skip_depth == 0:
            self._chunks.append(text)

    def text(self) -> str:
        return "\n".join(chunk for chunk in self._chunks if chunk.strip())


class WebExtractResult:
    def __init__(self, text: str, title: str | None, warning: str | None) -> None:
        self.text = text
        self.title = title
        self.warning = warning


class WebExtractService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def extract(self, url: str) -> WebExtractResult:
        self._validate_url(url)
        html = await self._fetch_html(url)
        parser = StaticHtmlTextExtractor()
        parser.feed(html)
        text, was_truncated = truncate_learning_text(
            parser.text(),
            self.settings.max_source_chars,
        )
        if len(text) < 100:
            raise ApiError(
                422,
                "WEB_CONTENT_EXTRACT_FAILED",
                "해당 페이지에서 문제 생성을 위한 본문을 추출할 수 없습니다.",
            )

        warnings: list[str] = []
        if was_truncated:
            warnings.append(CONTENT_TRUNCATED)
        if not parser.has_main_content_tag:
            warnings.append(NO_MAIN_CONTENT_FOUND)
        if self._looks_like_dynamic_page(html, text):
            warnings.append(DYNAMIC_PAGE_LIKELY)

        return WebExtractResult(
            text=text,
            title=parser.title,
            warning=",".join(warnings) or None,
        )

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ApiError(400, "WEB_URL_INVALID", "올바른 웹 URL이 아닙니다.")
        if parsed.path.lower().endswith(".pdf"):
            raise ApiError(400, "WEB_URL_INVALID", "PDF 문서는 MVP 범위에서 지원하지 않습니다.")

    async def _fetch_html(self, url: str) -> str:
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.request_timeout_seconds
            ) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ApiError(
                422,
                "WEB_CONTENT_EXTRACT_FAILED",
                "해당 페이지에서 문제 생성을 위한 본문을 추출할 수 없습니다.",
            ) from exc

        content_type = response.headers.get("content-type", "")
        if "html" not in content_type.lower():
            raise ApiError(
                422,
                "WEB_CONTENT_EXTRACT_FAILED",
                "해당 페이지에서 문제 생성을 위한 본문을 추출할 수 없습니다.",
            )
        return response.text

    def _looks_like_dynamic_page(self, html: str, text: str) -> bool:
        normalized_html = html.lower()
        script_count = normalized_html.count("<script")
        app_root_markers = ("id=\"root\"", "id=\"app\"", "__next", "data-reactroot")
        return len(text) < 500 and (
            script_count >= 3 or any(marker in normalized_html for marker in app_root_markers)
        )
