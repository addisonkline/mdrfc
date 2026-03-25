import re
import unicodedata


_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)

# Inline markdown stripping patterns — applied in order to extract plain text
# from heading content, matching how rehype-slug sees headings after rendering.
_INLINE_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_INLINE_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_INLINE_BOLD_ITALIC_STAR_RE = re.compile(r"\*{1,3}([^*]+)\*{1,3}")
_INLINE_BOLD_ITALIC_UNDER_RE = re.compile(r"_{1,3}([^_]+)_{1,3}")
_INLINE_STRIKETHROUGH_RE = re.compile(r"~~([^~]+)~~")
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")

# Unicode categories that github-slugger preserves (letters, marks, numbers).
_KEEP_CATEGORIES = frozenset(
    {
        "Ll",
        "Lu",
        "Lt",
        "Lm",
        "Lo",  # Letters
        "Mn",
        "Mc",
        "Me",  # Marks
        "Nd",
        "Nl",
        "No",  # Numbers
    }
)


def _strip_inline_markdown(text: str) -> str:
    """Strip inline markdown syntax to get plain text."""
    text = _INLINE_IMAGE_RE.sub(r"\1", text)
    text = _INLINE_LINK_RE.sub(r"\1", text)
    text = _INLINE_BOLD_ITALIC_STAR_RE.sub(r"\1", text)
    text = _INLINE_BOLD_ITALIC_UNDER_RE.sub(r"\1", text)
    text = _INLINE_STRIKETHROUGH_RE.sub(r"\1", text)
    text = _INLINE_CODE_RE.sub(r"\1", text)
    return text


def _is_slug_char(ch: str) -> bool:
    """Check if github-slugger would preserve this character."""
    if ch in (" ", "-", "_"):
        return True
    return unicodedata.category(ch) in _KEEP_CATEGORIES


def github_slug(text: str) -> str:
    """
    Slugify text using the same algorithm as github-slugger.

    Lowercase, strip characters that aren't letters/digits/spaces/hyphens/underscores,
    then replace spaces with hyphens.
    """
    text = text.lower()
    text = "".join(ch for ch in text if _is_slug_char(ch))
    text = text.replace(" ", "-")
    return text


def extract_heading_slugs(content: str) -> list[str]:
    """
    Extract all heading slugs from raw Markdown content.
    Returns a list of slugified anchors in document order,
    with duplicate headings disambiguated using -1, -2, etc.
    (matching github-slugger / rehype-slug behavior).
    """
    occurrences: dict[str, int] = {}
    slugs: list[str] = []
    for match in _HEADING_RE.finditer(content):
        heading_text = _strip_inline_markdown(match.group(1).strip())
        base = github_slug(heading_text)
        if not base:
            continue

        # Deduplicate: same logic as github-slugger's BananaSlug.slug()
        result = base
        while result in occurrences:
            occurrences[base] += 1
            result = f"{base}-{occurrences[base]}"
        occurrences[result] = 0

        slugs.append(result)
    return slugs
