"""Token blacklist service for logout and token revocation."""
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from threading import Lock

from app.config import settings
from shared.core.logging_config import get_logger

logger = get_logger(__name__)


class TokenBlacklist:
    """In-memory token blacklist with automatic cleanup."""

    def __init__(self):
        self._blacklist: dict[str, datetime] = {}
        self._lock = Lock()
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Token blacklist cleanup task started")

    async def stop(self):
        """Stop the background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Token blacklist cleanup task stopped")

    def add(self, token: str, expires_at: Optional[datetime] = None):
        """Add a token to the blacklist."""
        if expires_at is None:
            expires_at = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 5
            )

        with self._lock:
            self._blacklist[token] = expires_at
        logger.debug(f"Token blacklisted until {expires_at}")

    def add_refresh_token(self, token: str):
        """Add a refresh token to the blacklist."""
        expires_at = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS + 1
        )
        self.add(token, expires_at)

    def is_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted."""
        with self._lock:
            if token not in self._blacklist:
                return False

            expires_at = self._blacklist[token]
            if datetime.utcnow() > expires_at:
                del self._blacklist[token]
                return False

            return True

    def _cleanup(self):
        """Remove expired tokens from the blacklist."""
        now = datetime.utcnow()
        with self._lock:
            expired = [
                token for token, expires_at in self._blacklist.items()
                if now > expires_at
            ]
            for token in expired:
                del self._blacklist[token]

            if expired:
                logger.debug(f"Cleaned up {len(expired)} expired blacklisted tokens")

    async def _cleanup_loop(self):
        """Background task to clean up expired tokens every 5 minutes."""
        while True:
            try:
                await asyncio.sleep(300)
                self._cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in token blacklist cleanup: {e}")

    def get_stats(self) -> dict:
        """Get blacklist statistics."""
        with self._lock:
            return {
                "blacklisted_tokens": len(self._blacklist)
            }


# Singleton instance
_token_blacklist: Optional[TokenBlacklist] = None


def get_token_blacklist() -> TokenBlacklist:
    """Get the token blacklist singleton."""
    global _token_blacklist
    if _token_blacklist is None:
        _token_blacklist = TokenBlacklist()
    return _token_blacklist


async def init_token_blacklist():
    """Initialize and start the token blacklist service."""
    blacklist = get_token_blacklist()
    await blacklist.start()
    return blacklist


async def shutdown_token_blacklist():
    """Shutdown the token blacklist service."""
    global _token_blacklist
    if _token_blacklist:
        await _token_blacklist.stop()
