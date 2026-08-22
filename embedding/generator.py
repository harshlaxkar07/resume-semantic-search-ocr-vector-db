from app.exceptions import EmbeddingGenerationError
from app.logger import logger

from embedding.model import get_embedding_model


def generate_embedding(
    text: str,
) -> list[float]:
    """
    Generate vector embedding from text.
    """

    try:

        model = get_embedding_model()

        embedding = model.encode(
            text,
            normalize_embeddings=True,
        )
        
        return embedding.tolist()


    except Exception as error:

        logger.exception(error)

        raise EmbeddingGenerationError(
            str(error)
        )