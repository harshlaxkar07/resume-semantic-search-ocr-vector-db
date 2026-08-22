from sentence_transformers import SentenceTransformer

from app.config import settings


model = SentenceTransformer(
    settings.embedding_model
)


def get_embedding_model() -> SentenceTransformer:
    """
    Return loaded embedding model.
    """

    return model