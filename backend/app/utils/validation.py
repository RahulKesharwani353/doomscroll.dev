import re
import html
from typing import Optional

from shared.schemas.common import SourceType

VALID_SOURCES = [source.value for source in SourceType]

SEARCH_QUERY_PATTERN = re.compile(r'^[\w\s\-\.\,\!\?\:\;\'\"\@\#\$\%\&\(\)\[\]\+\=]+$', re.UNICODE)
SLUG_PATTERN = re.compile(r'^[a-z0-9\-]+$')
MAX_SEARCH_QUERY_LENGTH = 200
MAX_SLUG_LENGTH = 50


def is_valid_source(source: Optional[str]) -> bool:
    """Validate if the source is a valid content source."""
    if source is None:
        return True
    return source.lower() in VALID_SOURCES


def is_valid_search_query(query: str) -> bool:
    """Validate search query using allowlist pattern."""
    if not query or len(query) > MAX_SEARCH_QUERY_LENGTH:
        return False

    return bool(SEARCH_QUERY_PATTERN.match(query))


def is_valid_slug(slug: str) -> bool:
    """Validate slug contains only lowercase alphanumeric and hyphens."""
    if not slug or len(slug) > MAX_SLUG_LENGTH:
        return False

    return bool(SLUG_PATTERN.match(slug))


def sanitize_search_input(value: str) -> str:
    """Sanitize search input, keeping only allowlisted characters."""
    if not value:
        return ""

    value = value.strip()[:MAX_SEARCH_QUERY_LENGTH]
    sanitized = ''.join(c for c in value if SEARCH_QUERY_PATTERN.match(c) or c.isspace())
    return ' '.join(sanitized.split())


def sanitize_for_display(value: str) -> str:
    """HTML escape value for safe display."""
    if not value:
        return ""
    return html.escape(value)


def get_valid_sources() -> list[str]:
    """Get list of valid source identifiers."""
    return VALID_SOURCES.copy()


sanitize_input = sanitize_search_input
