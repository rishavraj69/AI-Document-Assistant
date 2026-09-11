from __future__ import annotations

from typing import Any

import pymupdf


class PdfProcessingError(Exception):
    """Raised when PDF processing fails."""


def extract_pages_from_pdf(file_bytes: bytes, filename: str) -> list[dict[str, Any]]:
    """
    Extract text from a PDF, preserving page metadata.

    Returns a list of dictionaries containing:
    - source_filename
    - page_number
    - content
    """
    if not file_bytes:
        raise PdfProcessingError("Uploaded PDF is empty.")

    try:
        pdf_document = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PdfProcessingError(f"Unable to open PDF: {str(exc)}") from exc

    try:
        extracted_pages: list[dict[str, Any]] = []

        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            content = page.get_text()

            extracted_pages.append(
                {
                    "source_filename": filename,
                    "page_number": page_number + 1,
                    "content": content.strip(),
                }
            )

        return extracted_pages
    except Exception as exc:
        raise PdfProcessingError(f"Error extracting text from PDF: {str(exc)}") from exc
    finally:
        pdf_document.close()
