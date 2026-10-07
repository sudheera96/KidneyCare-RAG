from __future__ import annotations
from dataclasses import replace
from .document_loader import DocumentChunk

def chunk_documents(documents: list[DocumentChunk], chunk_size: int = 180, overlap: int = 40) -> list[DocumentChunk]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap must be smaller than chunk_size")
    chunks: list[DocumentChunk] = []
    next_id = 0
    for doc in documents:
        words = doc.text.split()
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            text = " ".join(words[start:end]).strip()
            if text:
                chunks.append(replace(doc, text=text, chunk_id=next_id))
                next_id += 1
            if end >= len(words):
                break
            start = end - overlap
    return chunks
