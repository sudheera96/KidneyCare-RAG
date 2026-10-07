from pathlib import Path
from src.chunker import chunk_documents
from src.document_loader import DocumentChunk, load_documents

def test_loader_reads_text(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text("Chronic kidney disease information. " * 20, encoding="utf-8")
    documents = load_documents(tmp_path)
    assert len(documents) == 1
    assert documents[0].source == "sample.txt"

def test_chunker_creates_chunks() -> None:
    document = DocumentChunk(text="word " * 100, source="sample.txt")
    chunks = chunk_documents([document], chunk_size=20, overlap=5)
    assert len(chunks) > 1
    assert chunks[0].chunk_id == 0
