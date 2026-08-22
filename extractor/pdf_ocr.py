from pathlib import Path

import fitz
import numpy as np
from paddleocr import PaddleOCR

from app.exceptions import PDFExtractionError
from app.logger import logger


# Load OCR model once when the application starts.
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)


def extract_text_with_ocr(pdf_path: str) -> str:
    """
    Extract text from a scanned PDF using PaddleOCR.

    Workflow
    --------
    PDF
        ↓
    Render each page as an image
        ↓
    Convert PIL Image to NumPy array
        ↓
    Run PaddleOCR
        ↓
    Combine all detected text
        ↓
    Return raw text
    """

    try:

        document = fitz.open(pdf_path)

        pages = []


        for page_number in range(len(document)):

            page = document.load_page(page_number)

            # Render the page as an image
            pixmap = page.get_pixmap(dpi=300)

            # Convert PIL Image to NumPy array (supported by PaddleOCR)
            pil_image = pixmap.pil_image()
            image_np = np.array(pil_image)

            # Run OCR on the NumPy array
            result = ocr.predict(image_np)

            page_lines = []

            if result:

                for block in result:

                    if "rec_texts" in block:

                        page_lines.extend(block["rec_texts"])

            pages.append("\n".join(page_lines))

        document.close()

        text = "\n\n".join(pages)

        logger.success(
            "OCR extracted {} characters.",
            len(text),
        )

        return text

    except Exception as error:

        logger.exception(error)

        raise PDFExtractionError(str(error))