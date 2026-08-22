import chromadb

from app.config import settings


client = chromadb.PersistentClient(
    path=str(settings.chroma_db_path)
)


def get_collection():
    """
    Get or create resume vector collection.
    """

    collection = client.get_or_create_collection(
        name=settings.chroma_collection,
        metadata={
            "hnsw:space": "cosine"
        },
    )

    return collection