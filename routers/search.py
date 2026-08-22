from fastapi import APIRouter

from schemas.search import SearchRequest, SearchResponse
from services.search_service import search_resumes


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.post(
    "",
    response_model=SearchResponse,
    summary="Semantic resume search",
)
async def search_resume_endpoint(
    request: SearchRequest,
) -> SearchResponse:
    """
    Search resumes using semantic similarity.
    """

    return await search_resumes(request)