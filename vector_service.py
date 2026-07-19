"""ChromaDB vector store service for sports knowledge persistence and retrieval."""

import os
import chromadb
from config import Config


_client = None
_collections: dict = {}


def _get_client() -> chromadb.PersistentClient:
    """Lazy-initialize the ChromaDB persistent client."""
    global _client
    if _client is None:
        os.makedirs(Config.CHROMA_DB_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
    return _client


def _get_collection(sport: str) -> chromadb.Collection:
    """Get or create a ChromaDB collection for a specific sport."""
    if sport not in _collections:
        client = _get_client()
        _collections[sport] = client.get_or_create_collection(
            name=f"sports_{sport}",
            metadata={"hnsw:space": "cosine"},
        )
    return _collections[sport]


def store_documents(sport: str, documents: list[dict]) -> int:
    """
    Store search result documents into ChromaDB.

    Each document should have 'title', 'content', and 'url' keys.
    Returns the number of newly stored documents.
    """
    collection = _get_collection(sport)
    stored = 0

    for doc in documents:
        content = doc.get("content", "").strip()
        if not content or len(content) < 30:
            continue

        # Use URL as a stable unique ID to avoid duplicates
        doc_id = str(hash(doc.get("url", content)))

        # Check if already exists
        existing = collection.get(ids=[doc_id])
        if existing and existing["ids"]:
            continue

        collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[
                {
                    "title": doc.get("title", ""),
                    "url": doc.get("url", ""),
                    "sport": sport,
                }
            ],
        )
        stored += 1

    print(f"[VectorDB] Stored {stored} new documents for '{sport}'")
    return stored


def query_relevant_context(sport: str, query: str, n_results: int = 5) -> str:
    """
    Query ChromaDB for the most relevant passages for a given sport and query.

    Returns a combined string of the top relevant passages.
    """
    collection = _get_collection(sport)

    # If collection is empty, return empty context
    count = collection.count()
    if count == 0:
        return ""

    actual_n = min(n_results, count)

    results = collection.query(
        query_texts=[query],
        n_results=actual_n,
    )

    passages = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            title = meta.get("title", "")
            source = meta.get("url", "")
            passages.append(
                f"[Source {i + 1}: {title}]\n{doc}\n(Source: {source})"
            )

    context = "\n\n---\n\n".join(passages)
    print(f"[VectorDB] Retrieved {len(passages)} passages for context")
    return context
