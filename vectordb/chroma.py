from app.exceptions import VectorDatabaseError
from app.logger import logger

from vectordb.collection import get_collection


def add_resume_embedding(
    resume_id: int,
    embedding: list[float],
    metadata: dict,
):
    """
    Store resume vector in ChromaDB.
    """

    try:

        collection = get_collection()

        collection.add(
            ids=[
                str(resume_id)
            ],
            embeddings=[
                embedding
            ],
            metadatas=[
                metadata
            ],
        )


        logger.info(
            "Resume embedding stored: {}",
            resume_id,
        )


    except Exception as error:

        logger.exception(error)

        raise VectorDatabaseError(
            str(error)
        )