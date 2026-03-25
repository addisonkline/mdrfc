import re
import unicodedata


_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
_SPECIAL_CHARS_RE = re.compile(r"[^\w\s-]")
_WHITESPACE_RE = re.compile(r"[\s]+")


def slugify_heading(text: str) -> str:
    """
    Slugify a Markdown heading to match GitHub-style anchor generation.
    Lowercase, spaces to hyphens, strip special characters.
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.lower().strip()
    text = _SPECIAL_CHARS_RE.sub("", text)
    text = _WHITESPACE_RE.sub("-", text)
    text = text.strip("-")
    return text


def extract_heading_slugs(content: str) -> list[str]:
    """
    Extract all heading slugs from raw Markdown content.
    Returns a list of slugified anchors in document order.
    """
    slugs: list[str] = []
    for match in _HEADING_RE.finditer(content):
        heading_text = match.group(1).strip()
        slug = slugify_heading(heading_text)
        if slug:
            slugs.append(slug)
    return slugs
