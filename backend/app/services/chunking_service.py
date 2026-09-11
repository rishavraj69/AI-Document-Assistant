from __future__ import annotations

from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


def chunk_page_documents(
    page_documents: list[dict[str, Any]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """
    Split page-level documents into overlapping chunks while preserving page metadata.

    Each returned chunk includes:
    - text
    - source_filename
    - page_number
    """
    if not page_documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    chunk_documents: list[dict[str, Any]] = []

    for page_document in page_documents:
        page_content = page_document.get("content", "").strip()

        if not page_content:
            continue

        split_texts = splitter.split_text(page_content)

        for chunk_text in split_texts:
            chunk_text = chunk_text.strip()

            if not chunk_text:
                continue

            chunk_documents.append(
                {
                    "text": chunk_text,
                    "source_filename": page_document["source_filename"],
                    "page_number": page_document["page_number"],
                }
            )

    return chunk_documents
