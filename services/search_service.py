from schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
)

from embedding.generator import generate_embedding
from vectordb.search import search_resume_embeddings

from crud.resume import get_resume_by_id

from app.logger import logger


async def search_resumes(
    request: SearchRequest,
) -> SearchResponse:
    """
    Search resumes using semantic similarity.
    """


    # Generate embedding for search query

    query_embedding = generate_embedding(
        request.query
    )


    logger.info(
        "Query embedding generated."
    )


    # Search vectors from ChromaDB

    vector_results = search_resume_embeddings(
        query_embedding=query_embedding,
        top_k=request.top_k,
    )


    logger.info(
        "Vector results: {}",
        vector_results,
    )


    results = []


    # Get resume details from MySQL

    for item in vector_results:


        resume = get_resume_by_id(
            item["id"]
        )


        if not resume:
            continue


        distance = item["distance"]


        # Convert cosine distance to similarity score

        similarity_score = round(
            1 - distance,
            4
        )


        logger.info(
            "Resume ID: {}, Distance: {}, Similarity: {}",
            item["id"],
            distance,
            similarity_score,
        )


        results.append(
            SearchResult(
                id=resume["id"],
                original_filename=resume["original_filename"],          
                pdf_path=resume["pdf_path"],
                similarity_score=similarity_score,
            )
        )


    return SearchResponse(
        results=results
    )