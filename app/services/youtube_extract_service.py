from urllib.parse import parse_qs, urlparse

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.services.text_processing_service import truncate_learning_text


CONTENT_TRUNCATED = "CONTENT_TRUNCATED"
YOUTUBE_AUTO_TRANSCRIPT_USED = "YOUTUBE_AUTO_TRANSCRIPT_USED"
YOUTUBE_EN_TRANSCRIPT_USED = "YOUTUBE_EN_TRANSCRIPT_USED"


class YouTubeTranscriptResult:
    def __init__(self, text: str, video_id: str, warning: str | None) -> None:
        self.text = text
        self.video_id = video_id
        self.warning = warning


class YouTubeTranscriptService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def extract(self, url: str) -> YouTubeTranscriptResult:
        video_id = self._extract_video_id(url)
        transcript_data = await self._get_transcript_text(video_id)
        if isinstance(transcript_data, tuple):
            raw_text, extraction_warnings = transcript_data
        else:
            raw_text, extraction_warnings = transcript_data, []

        text, was_truncated = truncate_learning_text(
            raw_text,
            self.settings.max_source_chars,
        )
        if len(text) < 100:
            raise ApiError(
                422,
                "YOUTUBE_TRANSCRIPT_NOT_FOUND",
                "이 영상에는 사용할 수 있는 자막이 없습니다.",
            )

        warnings = list(extraction_warnings)
        if was_truncated:
            warnings.append(CONTENT_TRUNCATED)

        return YouTubeTranscriptResult(
            text=text,
            video_id=video_id,
            warning=",".join(warnings) or None,
        )

    def _extract_video_id(self, url: str) -> str:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if host in {"youtu.be", "www.youtu.be"} and parsed.path.strip("/"):
            return parsed.path.strip("/").split("/")[0]
        if host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            if parsed.path == "/watch" and video_id:
                return video_id
        raise ApiError(400, "YOUTUBE_URL_INVALID", "올바른 YouTube URL이 아닙니다.")

    async def _get_transcript_text(self, video_id: str) -> tuple[str, list[str]]:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError as exc:
            raise ApiError(
                422,
                "YOUTUBE_TRANSCRIPT_NOT_FOUND",
                "이 영상에는 사용할 수 있는 자막이 없습니다.",
            ) from exc

        api = YouTubeTranscriptApi()
        try:
            transcript_list = api.list(video_id)
            transcript, warnings = self._select_transcript(transcript_list)
        except Exception as exc:
            try:
                transcript = api.fetch(video_id, languages=["ko", "en"])
                warnings = []
            except Exception as fallback_exc:
                raise ApiError(
                    422,
                    "YOUTUBE_TRANSCRIPT_NOT_FOUND",
                    "이 영상에는 사용할 수 있는 자막이 없습니다.",
                ) from fallback_exc

        return " ".join(item.get("text", "") for item in transcript.to_raw_data()), warnings

    def _select_transcript(self, transcript_list):
        candidates = [
            ("ko", False, []),
            ("ko", True, [YOUTUBE_AUTO_TRANSCRIPT_USED]),
            ("en", False, [YOUTUBE_EN_TRANSCRIPT_USED]),
            ("en", True, [YOUTUBE_EN_TRANSCRIPT_USED, YOUTUBE_AUTO_TRANSCRIPT_USED]),
        ]
        last_error: Exception | None = None
        for language, generated, warnings in candidates:
            try:
                finder = (
                    transcript_list.find_generated_transcript
                    if generated
                    else transcript_list.find_manually_created_transcript
                )
                transcript = finder([language]).fetch()
                return transcript, warnings
            except Exception as exc:
                last_error = exc
        raise last_error or ValueError("transcript not found")
