from __future__ import annotations
from dataclasses import dataclass
import faiss
from sentence_transformers import SentenceTransformer
from .document_loader import DocumentChunk

@dataclass
class RetrievedChunk:
    chunk: DocumentChunk
    score: float

class VectorStore:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks: list[DocumentChunk] = []

    def build(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            raise ValueError("Cannot build a vector index from zero chunks.")
        self.chunks = chunks
        vectors = self.model.encode([c.text for c in chunks], normalize_embeddings=True,
                                    convert_to_numpy=True, show_progress_bar=False).astype("float32")
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    def search(self, query: str, top_k: int = 4) -> list[RetrievedChunk]:
        if self.index is None:
            raise RuntimeError("Vector index has not been built.")
        query_vector = self.model.encode([query], normalize_embeddings=True,
                                         convert_to_numpy=True, show_progress_bar=False).astype("float32")
        scores, indices = self.index.search(query_vector, min(top_k, len(self.chunks)))
        return [RetrievedChunk(self.chunks[i], float(s)) for s, i in zip(scores[0], indices[0]) if i >= 0]
