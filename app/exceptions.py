class ResumeSearchEngineError(Exception):
    """Base exception."""


class DatabaseConnectionError(ResumeSearchEngineError):
    """Database connection failed."""


class PDFExtractionError(ResumeSearchEngineError):
    """PDF extraction failed."""


class VectorDatabaseError(ResumeSearchEngineError):
    """Vector database operation failed."""


class EmbeddingGenerationError(ResumeSearchEngineError):
    """Embedding generation failed."""