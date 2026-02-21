"""
PDF Reader Tool — PyPDF + ChromaDB vector store wrapper for agent nodes.

Loads PDF files, splits them into chunks, stores embeddings in a local
ChromaDB collection, and performs similarity search against queries.
Requires the CHROMA_PERSIST_DIR environment variable for storage location.
"""

import os
from typing import List, Optional

from langchain_core.tools import tool

# Module-level collection cache to avoid re-initializing on every call
_collection_cache: dict = {}


def _get_chroma_collection(collection_name: str = "council_pdfs"):
    """Get or create a ChromaDB collection for PDF content."""
    if collection_name in _collection_cache:
        return _collection_cache[collection_name]

    import chromadb

    persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    _collection_cache[collection_name] = collection
    return collection


def ingest_pdf(file_path: str, collection_name: str = "council_pdfs") -> int:
    """
    Read a PDF file, split into chunks, and store in ChromaDB.

    Args:
        file_path: Path to the PDF file.
        collection_name: ChromaDB collection name.

    Returns:
        Number of chunks ingested.
    """
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    chunks: List[str] = []
    metadata_list: List[dict] = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text or not text.strip():
            continue

        # Split long pages into ~500 character chunks with overlap
        words = text.split()
        chunk_size = 100  # words per chunk
        overlap = 20

        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i : i + chunk_size]
            chunk_text = " ".join(chunk_words)
            if chunk_text.strip():
                chunks.append(chunk_text)
                metadata_list.append({
                    "source": os.path.basename(file_path),
                    "page": page_num + 1,
                })

    if not chunks:
        return 0

    collection = _get_chroma_collection(collection_name)

    # Generate deterministic IDs based on file and chunk position
    ids = [
        f"{os.path.basename(file_path)}_chunk_{i}"
        for i in range(len(chunks))
    ]

    collection.upsert(
        documents=chunks,
        metadatas=metadata_list,
        ids=ids,
    )

    return len(chunks)


@tool
def pdf_search(query: str, n_results: int = 5) -> str:
    """
    Search the PDF knowledge base for information relevant to a query.

    Args:
        query: The search query to find relevant PDF content.
        n_results: Number of results to return (default 5).

    Returns:
        A formatted string with relevant passages from ingested PDFs.
    """
    try:
        collection = _get_chroma_collection()
    except Exception as exc:  # noqa: BLE001
        return f"[PDF Search Error] Could not access vector store: {exc}"

    if collection.count() == 0:
        return "[PDF Search] No documents have been ingested yet."

    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count()),
        )
    except Exception as exc:  # noqa: BLE001
        return f"[PDF Search Error] {exc}"

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return f"No relevant passages found for: {query}"

    formatted = []
    for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
        source = meta.get("source", "unknown")
        page = meta.get("page", "?")
        formatted.append(f"{i}. [Source: {source}, Page {page}]\n   {doc}")

    return "\n\n".join(formatted)


def create_pdf_search_tool() -> Optional[tool]:
    """Factory that returns the pdf_search tool if ChromaDB is configured."""
    persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")
    if persist_dir:
        return pdf_search
    return None
