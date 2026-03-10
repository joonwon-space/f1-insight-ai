"""Unsplash image search proxy endpoint."""

from fastapi import APIRouter, Query

from app.services.unsplash import UnsplashSearchResult, search_images

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("/search", response_model=UnsplashSearchResult | None)
async def image_search(
    q: str = Query(..., description="Search query (e.g. 'Max Verstappen Red Bull')"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(5, ge=1, le=30, description="Results per page"),
    orientation: str = Query("landscape", description="Image orientation"),
) -> UnsplashSearchResult | None:
    """Search Unsplash for copyright-free F1-related images.

    Images from Unsplash are free to use commercially without attribution
    requirements (though attribution is appreciated).
    """
    return await search_images(q, page=page, per_page=per_page, orientation=orientation)
