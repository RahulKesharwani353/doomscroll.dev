import re
from typing import Optional

from shared.schemas.common import SourceType

VALID_SOURCES = [source.value for source in SourceType]


def is_valid_source(source: Optional[str]) -> bool:
    """Validate if the source is a valid content source."""
    if source is None:
        return True
    return source.lower() in VALID_SOURCES


def is_valid_search_query(query: str) -> bool:
    """Validate search query for safe characters."""
    if not query:
        return False
    pattern = r'^[\w\s\-\.\,\!\?\:\;\'\"]+$'
    return bool(re.match(pattern, query, re.UNICODE))


def sanitize_input(value: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not value:
        return ""

    sanitized = value.strip()
    dangerous_patterns = [
        r'--', r';', r'\/\*', r'\*\/', r'xp_',
        r'UNION', r'SELECT', r'INSERT', r'UPDATE',
        r'DELETE', r'DROP', r'CREATE', r'ALTER', r'EXEC',
    ]

    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

    return sanitized


def get_valid_sources() -> list[str]:
    """Get list of valid source identifiers."""
    return VALID_SOURCES.copy()
