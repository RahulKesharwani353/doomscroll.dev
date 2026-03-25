"""Rate limiting middleware."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings


def get_request_identifier(request: Request) -> str:
    """Get client IP for rate limiting, handling proxied requests."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request) or "unknown"


limiter = Limiter(
    key_func=get_request_identifier,
    enabled=settings.RATE_LIMIT_ENABLED,
    default_limits=[f"{settings.RATE_LIMIT_API_REQUESTS}/minute"]
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": exc.detail
        }
    )


def auth_rate_limit():
    """Stricter rate limit for auth endpoints."""
    return limiter.limit(f"{settings.RATE_LIMIT_AUTH_REQUESTS}/minute")


def api_rate_limit():
    """Standard rate limit for API endpoints."""
    return limiter.limit(f"{settings.RATE_LIMIT_API_REQUESTS}/minute")
