import fitz

from app.exceptions import PDFExtractionError
from app.logger import logger


def extract_text(pdf_path: str) -> str:
    """
    Extract text from a PDF using PyMuPDF.
    """

    try:

        document = fitz.open(pdf_path)

        pages = []
        links = []

        for page in document:

            pages.append(page.get_text())

            for link in page.get_links():

                uri = link.get("uri")

                if uri:
                    links.append(uri)

        document.close()

        text = "\n".join(pages)

        if links:

            # Remove duplicate links while preserving order
            links = list(dict.fromkeys(links))

            text += "\n\n===== HYPERLINKS =====\n"

            for link in links:
                text += f"{link}\n"


        return text

    except Exception as error:

        logger.exception(error)

        raise PDFExtractionError(str(error))