from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    debug: bool = Field(default=False, alias="DEBUG")


    # -------------------------
    # MySQL
    # -------------------------

    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(alias="DB_PORT")
    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")
    db_name: str = Field(alias="DB_NAME")

    # -------------------------
    # Uploads
    # -------------------------

    upload_directory: Path = Field(alias="UPLOAD_DIRECTORY")
    max_file_size: int = Field(alias="MAX_FILE_SIZE")

    # -------------------------
    # Embedding Model
    # -------------------------

    embedding_model: str = Field(alias="EMBEDDING_MODEL")

    # -------------------------
    # ChromaDB
    # -------------------------

    chroma_db_path: Path = Field(alias="CHROMA_DB_PATH")
    chroma_collection: str = Field(alias="CHROMA_COLLECTION")

    # -------------------------
    # Logging
    # -------------------------

    log_level: str = Field(alias="LOG_LEVEL")
    log_directory: Path = Field(alias="LOG_DIRECTORY")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()