from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings
from app.logger import logger

from extractor import get_text

from crud.resume import create_resume

from schemas.resume import (
    UploadResponse,
    ResumeResponse,
)

from embedding.generator import generate_embedding
from vectordb.chroma import add_resume_embedding



async def upload_resume(
    file: UploadFile,
) -> UploadResponse:
    """
    Upload resume, extract text, and save metadata.
    """

    try:

        upload_directory = Path(
            settings.upload_directory
        )

        upload_directory.mkdir(
            parents=True,
            exist_ok=True,
        )


        file_extension = Path(
            file.filename
        ).suffix.lower()


        stored_filename = (
            f"{uuid4().hex}{file_extension}"
        )


        file_path = (
            upload_directory / stored_filename
        )


        # Save uploaded file

        content = await file.read()

        with open(
            file_path,
            "wb",
        ) as resume_file:

            resume_file.write(content)


        logger.info(
            "Resume saved: {}",
            file_path,
        )


        # Extract text

        cleaned_text, raw_text = get_text(
            file_path
        )


        logger.info(
            "Resume text extracted successfully."
        )
        

        # Save database record

        resume_id = create_resume(
            original_filename=file.filename,
            stored_filename=stored_filename,
            pdf_path=str(file_path),
            raw_text=raw_text,
        )


        # Generate embedding
        embedding = generate_embedding(
            cleaned_text
        )



        add_resume_embedding(
            resume_id=resume_id,
            embedding=embedding,
            metadata={
                "original_filename": file.filename,
                "pdf_path": str(file_path),
            },
        )

        logger.info(
            "Resume saved in database with id {}",
            resume_id,
        )


        return UploadResponse(
            message="Resume uploaded successfully.",
            resume=ResumeResponse(
                id=resume_id,
                original_filename=file.filename,
                stored_filename=stored_filename,
                pdf_path=str(file_path),
                raw_text=raw_text,
                uploaded_at=None,
            ),
        )


    except Exception as error:

        logger.exception(error)

        raise