import html
import re


MIN_MEANINGFUL_LINE_CHARS = 2


def normalize_learning_text(text: str) -> str:
    decoded = html.unescape(text or "")
    decoded = decoded.replace("\r\n", "\n").replace("\r", "\n")

    lines: list[str] = []
    seen: set[str] = set()
    for raw_line in decoded.split("\n"):
        line = normalize_inline_text(raw_line)
        if len(line) < MIN_MEANINGFUL_LINE_CHARS:
            continue
        if line in seen:
            continue
        seen.add(line)
        lines.append(line)

    if not lines:
        return normalize_inline_text(decoded)
    return normalize_inline_text("\n".join(lines))


def normalize_inline_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def truncate_learning_text(text: str, max_chars: int) -> tuple[str, bool]:
    normalized = normalize_learning_text(text)
    if len(normalized) <= max_chars:
        return normalized, False
    return normalized[:max_chars].rstrip(), True
