from app.exceptions import VectorDatabaseError
from app.logger import logger

from vectordb.collection import get_collection


def search_resume_embeddings(
    query_embedding: list[float],
    top_k: int = 5,
) -> list[dict]:
    """
    Search resume embeddings in ChromaDB.
    """

    try:

        collection = get_collection()

        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k,
            include=[
                "metadatas",
                "distances",
            ],
        )


        resumes = []

        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]


        for index, resume_id in enumerate(ids):

            resumes.append(
                {
                    "id": int(resume_id),
                    "distance": distances[index],
                    "metadata": metadatas[index],
                }
            )


        logger.info(
            "Found {} similar resumes.",
            len(resumes),
        )


        return resumes


    except Exception as error:

        logger.exception(error)

        raise VectorDatabaseError(
            str(error)
        )