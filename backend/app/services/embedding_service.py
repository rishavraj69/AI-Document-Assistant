from __future__ import annotations

from typing import Any

from langchain_huggingface import HuggingFaceEmbeddings


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingService:
    """Service for generating embeddings from chunk documents."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = HuggingFaceEmbeddings(model_name=model_name)

    def embed_chunks(self, chunk_documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Generate embeddings for chunk documents while preserving original metadata.

        Each returned chunk includes:
        - text
        - source_filename
        - page_number
        - embedding
        """
        if not chunk_documents:
            return []

        valid_chunks: list[tuple[dict[str, Any], str]] = []

        for chunk_document in chunk_documents:
            text = (chunk_document.get("text") or "").strip()
            if text:
                valid_chunks.append((chunk_document, text))

        if not valid_chunks:
            return []

        texts = [text for _, text in valid_chunks]
        embeddings = self.model.embed_documents(texts)

        enriched_chunks: list[dict[str, Any]] = []

        for (chunk_document, _), embedding in zip(valid_chunks, embeddings):
            enriched_chunks.append(
                {
                    **chunk_document,
                    "embedding": embedding,
                }
            )

        return enriched_chunks

    def embed_query(self, query: str) -> list[float]:
        """Generate an embedding for a single query string."""
        if not query or not query.strip():
            raise ValueError("Query text must not be empty.")

        return self.model.embed_query(query)
