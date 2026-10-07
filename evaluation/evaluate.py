from __future__ import annotations
import json
from pathlib import Path
from src.rag_pipeline import KidneyCareRAG

def main() -> None:
    questions = json.loads(Path("evaluation/questions.json").read_text(encoding="utf-8"))
    rag = KidneyCareRAG(data_dir="data")
    print("KidneyCare RAG evaluation")
    print("=" * 72)
    for row in questions:
        response = rag.ask(row["question"])
        print(f"\nQuestion: {row['question']}")
        print(f"Expected supported by project documents: {row['supported']}")
        print(f"Answer: {response.answer}")
        print("Retrieved sources:")
        for source in response.sources:
            location = f"page {source.chunk.page}" if source.chunk.page else "text file"
            print(f"  - {source.chunk.source} ({location}), score={source.score:.3f}")

if __name__ == "__main__":
    main()
