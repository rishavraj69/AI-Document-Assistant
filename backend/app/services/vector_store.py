from __future__ import annotations

from typing import Any

import faiss
import numpy as np

from app.services.embedding_service import EmbeddingService


class VectorStore:
    """Simple in-memory FAISS vector store for chunk retrieval."""

    def __init__(self, embedding_service: EmbeddingService | None = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.index: faiss.Index | None = None
        self.documents: list[dict[str, Any]] = []

    def build_index(self, chunk_documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Build a FAISS index from chunk documents while preserving metadata.

        If embeddings are not already present on the chunk documents, they are
        generated using the shared embedding service from Phase 4A.
        """
        if not chunk_documents:
            self.index = None
            self.documents = []
            return []

        embedded_chunks = chunk_documents

        if not embedded_chunks[0].get("embedding"):
            embedded_chunks = self.embedding_service.embed_chunks(chunk_documents)

        valid_chunks = [chunk for chunk in embedded_chunks if chunk.get("embedding")]

        if not valid_chunks:
            self.index = None
            self.documents = []
            return []

        vectors = np.asarray([chunk["embedding"] for chunk in valid_chunks], dtype="float32")
        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(vectors)
        self.documents = valid_chunks

        return valid_chunks

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """
        Search the vector index using a user query and return matching chunks
        together with their metadata and score information.
        """
        if not query or not query.strip():
            raise ValueError("Query text must not be empty.")

        if self.index is None or not self.documents:
            raise RuntimeError("Vector index has not been built yet.")

        query_embedding = np.asarray(
            self.embedding_service.embed_query(query),
            dtype="float32",
        ).reshape(1, -1)

        number_of_results = min(top_k, len(self.documents))
        distances, indices = self.index.search(query_embedding, number_of_results)

        results: list[dict[str, Any]] = []

        for distance, index_position in zip(distances[0], indices[0]):
            if index_position < 0:
                continue

            source_chunk = self.documents[int(index_position)]
            similarity = 1.0 / (1.0 + float(distance))

            results.append(
                {
                    "text": source_chunk.get("text", ""),
                    "source_filename": source_chunk.get("source_filename", ""),
                    "page_number": source_chunk.get("page_number"),
                    "distance": float(distance),
                    "similarity": float(similarity),
                    "preview": source_chunk.get("text", "")[:300],
                }
            )

        return results
