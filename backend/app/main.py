from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.services.chunking_service import chunk_page_documents
from app.services.embedding_service import EmbeddingService
from app.services.gemini_service import GeminiService
from app.services.pdf_service import PdfProcessingError, extract_pages_from_pdf
from app.services.vector_store import VectorStore

app = FastAPI(
    title="AI Document Assistant",
    description="Backend for querying PDF documents using a simple RAG pipeline.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_service = EmbeddingService()
vector_store = VectorStore(embedding_service=embedding_service)

try:
    gemini_service = GeminiService()
except ValueError:
    gemini_service = None


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI Document Assistant backend is running.",
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to the AI Document Assistant backend.",
        "health": "/health",
    }


@app.post("/api/query")
async def api_query(file: UploadFile = File(...), question: str = Form(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question text must not be empty.")

    if gemini_service is None:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured. Please add it to your environment or .env file.",
        )

    try:
        uploaded_bytes = await file.read()
        extracted_pages = extract_pages_from_pdf(uploaded_bytes, file.filename)
        chunks = chunk_page_documents(extracted_pages)

        vector_store.build_index(chunks)
        retrieved_chunks = vector_store.search(question, top_k=3)

        if not retrieved_chunks:
            raise HTTPException(status_code=404, detail="No relevant chunks were found for the provided question.")

        answer = gemini_service.generate_answer(question, retrieved_chunks)

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "source_filename": chunk["source_filename"],
                    "page_number": chunk["page_number"],
                    "preview": chunk["preview"],
                    "score": chunk.get("similarity", chunk.get("distance")),
                }
                for chunk in retrieved_chunks
            ],
        }
    except (PdfProcessingError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc



