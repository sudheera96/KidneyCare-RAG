from __future__ import annotations
import os
from dataclasses import dataclass
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from .chunker import chunk_documents
from .document_loader import load_documents
from .vector_store import RetrievedChunk, VectorStore

@dataclass
class RAGResponse:
    answer: str
    sources: list[RetrievedChunk]

class KidneyCareRAG:
    def __init__(self, data_dir: str = "data", embedding_model: str | None = None,
                 generation_model: str | None = None, top_k: int | None = None) -> None:
        self.embedding_model_name = embedding_model or os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.generation_model_name = generation_model or os.getenv(
            "GENERATION_MODEL", "google/flan-t5-small")
        self.top_k = top_k or int(os.getenv("TOP_K", "4"))
        self.store = VectorStore(self.embedding_model_name)
        documents = load_documents(data_dir)
        self.store.build(chunk_documents(documents))

        self.tokenizer = AutoTokenizer.from_pretrained(self.generation_model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.generation_model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()

    @staticmethod
    def _context(retrieved: list[RetrievedChunk]) -> str:
        blocks = []
        for item in retrieved:
            location = f"page {item.chunk.page}" if item.chunk.page else "text file"
            blocks.append(f"SOURCE: {item.chunk.source} ({location})\nRETRIEVED TEXT: {item.chunk.text}")
        return "\n\n".join(blocks)

    def ask(self, question: str) -> RAGResponse:
        question = question.strip()
        if not question:
            return RAGResponse("Please enter a CKD question.", [])
        retrieved = self.store.search(question, self.top_k)
        if not retrieved or retrieved[0].score < 0.25:
            return RAGResponse(
                "The available KidneyCare documents do not provide enough relevant information to answer this question.",
                retrieved,
            )
        prompt = (
            "You are KidneyCare RAG, an educational assistant for chronic kidney disease. "
            "Answer only from the provided context. Do not diagnose, prescribe, or invent facts. "
            "If the context does not support the answer, say that the documents do not provide enough information. "
            "Give a concise educational answer.\n\n"
            f"CONTEXT:\n{self._context(retrieved)}\n\nQUESTION: {question}\n\nANSWER:"
        )
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to(self.device)
        with torch.no_grad():
            output = self.model.generate(**inputs, max_new_tokens=220, do_sample=False)
        answer = self.tokenizer.decode(output[0], skip_special_tokens=True).strip()
        if not answer:
            answer = "The model did not produce an answer from the retrieved context."
        return RAGResponse(answer, retrieved)

    def ask_text(self, question: str) -> str:
        response = self.ask(question)
        lines = [response.answer, "", "Sources:"]
        if not response.sources:
            lines.append("No sources retrieved.")
        for item in response.sources:
            location = f"page {item.chunk.page}" if item.chunk.page else "text file"
            lines.append(f"- {item.chunk.source} ({location}) | similarity={item.score:.3f}")
        return "\n".join(lines)
