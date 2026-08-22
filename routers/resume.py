from fastapi import APIRouter, File, UploadFile, status

from schemas.resume import UploadResponse
from services.upload_service import upload_resume

from pathlib import Path
from fastapi import UploadFile
from starlette.datastructures import Headers


router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a resume",
)
async def upload_resume_endpoint(
    file: UploadFile = File(...),
) -> UploadResponse:
    """
    Upload a resume PDF, extract its text, generate embeddings,
    store the embedding in ChromaDB, and save metadata in MySQL.
    """

    return await upload_resume(file)




async def bulk_upload_resume(directory_path: str):
    """
    Upload all PDF files from a directory.

    Args:
        directory_path (str): Path containing PDF files.

    Returns:
        list: List of upload results.
    """
    directory = Path(directory_path)

    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"Invalid directory: {directory_path}")

    results = []

    pdf_files = directory.glob("*.pdf")

    for pdf_path in pdf_files:
        with pdf_path.open("rb") as f:
            upload_file = UploadFile(
                file=f,
                filename=pdf_path.name,
                headers=Headers({"content-type": "application/pdf"}),
            )

            try:
                result = await upload_resume(upload_file)
                results.append(
                    {
                        "file": pdf_path.name,
                        "status": "success",
                        "result": result,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "file": pdf_path.name,
                        "status": "failed",
                        "error": str(e),
                    }
                )

    return results
