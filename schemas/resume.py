from datetime import datetime

from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    pdf_path: str
    raw_text: str
    uploaded_at: datetime | None 


class UploadResponse(BaseModel):
    message: str
    resume: ResumeResponse