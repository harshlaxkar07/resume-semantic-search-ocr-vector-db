from pathlib import Path
from app.exceptions import PDFExtractionError
from app.logger import logger

from extractor.pdf_ocr import extract_text_with_ocr
from extractor.pdf_reader import extract_text
from extractor.text_cleaner import clean_text


MIN_TEXT_LENGTH = 200

SUPPORTED_PDF = {".pdf"}
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
SUPPORTED_DOCX = {".docx"}


def get_text(file_path: str | Path) -> tuple[str, str]:
    """
    Main extraction entry point.

    Returns
    -------
    (
        cleaned_text,
        raw_text,
    )
    """

    file_path = Path(file_path)

    extension = file_path.suffix.lower()



    # ---------------------------------------------------
    # PDF
    # ---------------------------------------------------

    if extension in SUPPORTED_PDF:

        raw_text = extract_text(str(file_path))

        if len(raw_text.strip()) < MIN_TEXT_LENGTH:

            logger.warning(
                "Very little text extracted ({} chars). Falling back to OCR.",
                len(raw_text),
            )

            raw_text = extract_text_with_ocr(str(file_path))

    # ---------------------------------------------------
    # Images
    # ---------------------------------------------------

    elif extension in SUPPORTED_IMAGES:


        raw_text = extract_text_with_ocr(str(file_path))

    # ---------------------------------------------------
    # DOCX
    # ---------------------------------------------------

    elif extension in SUPPORTED_DOCX:

        raise NotImplementedError(
            "DOCX extraction is not implemented yet."
        )

    # ---------------------------------------------------
    # Unsupported
    # ---------------------------------------------------

    else:

        raise PDFExtractionError(
            f"Unsupported file type: {extension}"
        )

    cleaned_text = clean_text(raw_text)

    logger.info("Raw text length: {}", len(raw_text))
    logger.info("Cleaned text length: {}", len(cleaned_text))

    debug_dir = Path("Debug")
    debug_dir.mkdir(exist_ok=True)

    with open(
        debug_dir / "raw_text.txt",
        "w",
        encoding="utf-8",
    ) as file:

        file.write("\n")
        file.write("=" * 80)
        file.write("\n")
        file.write(file_path.name)
        file.write("\n")
        file.write("=" * 80)
        file.write("\n\n")
        file.write(cleaned_text)
        file.write("\n\n")

    logger.success("Extraction completed successfully.")

    return cleaned_text, raw_text