from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
from pypdf import PdfReader

@dataclass
class DocumentChunk:
    text: str
    source: str
    page: int | None = None
    chunk_id: int = 0

def _clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def load_documents(data_dir: str | Path) -> list[DocumentChunk]:
    root = Path(data_dir)
    if not root.exists():
        raise FileNotFoundError(f"Data directory not found: {root}")

    documents: list[DocumentChunk] = []
    for path in sorted(root.iterdir()):
        if path.name.startswith("README") or not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            for page_number, page in enumerate(PdfReader(str(path)).pages, start=1):
                text = _clean_text(page.extract_text() or "")
                if text:
                    documents.append(DocumentChunk(text, path.name, page_number))
        elif suffix == ".txt":
            text = _clean_text(path.read_text(encoding="utf-8", errors="ignore"))
            if text:
                documents.append(DocumentChunk(text, path.name))

    if not documents:
        raise ValueError("No PDF/TXT documents were found in data/. Add the curated CKD documents.")
    return documents
