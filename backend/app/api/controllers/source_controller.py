from fastapi import APIRouter

from app.schemas.common import SourceInfo, SourcesResponse

router = APIRouter(prefix="/sources", tags=["Sources"])

AVAILABLE_SOURCES = [
    SourceInfo(id="hackernews", name="Hacker News", url="https://news.ycombinator.com", description="Tech news from Y Combinator"),
    SourceInfo(id="devto", name="Dev.to", url="https://dev.to", description="Developer articles and tutorials"),
    SourceInfo(id="reddit", name="Reddit", url="https://reddit.com", description="r/programming and r/webdev"),
    SourceInfo(id="lobsters", name="Lobste.rs", url="https://lobste.rs", description="Curated tech content"),
]


@router.get("", response_model=SourcesResponse)
async def get_sources() -> SourcesResponse:
    """Get list of available content sources."""
    return SourcesResponse(sources=AVAILABLE_SOURCES)
