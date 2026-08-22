from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Natural language search query.",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Maximum number of resumes to return.",
    )


class SearchResult(BaseModel):
    id: int
    original_filename: str
    pdf_path: str
    similarity_score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]