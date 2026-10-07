# KidneyCare RAG

Grounded healthcare document assistant for chronic kidney disease (CKD) education.

This repository implements the Human-Computer Interaction group project proposal using local healthcare documents, Sentence Transformers, FAISS, a Hugging Face model, and Gradio.

## Scope

Educational use only. The system does not diagnose conditions, prescribe medications, process personal medical records, or replace professional medical advice. Runtime answers use only the documents stored in `data/`; no live web search is used.

## Workflow

Local PDF/TXT documents -> text extraction -> chunking -> Sentence Transformer embeddings -> FAISS retrieval -> Hugging Face generation -> Gradio answer with sources.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Place the project's curated CKD PDF/TXT files in `data/`, then run:

```bash
python -m src.app
```

The first run may download the configured Hugging Face models.

## Configuration

- `EMBEDDING_MODEL`: `sentence-transformers/all-MiniLM-L6-v2`
- `GENERATION_MODEL`: `google/flan-t5-small`
- `TOP_K`: `4`

## Evaluation

Use `evaluation/questions.json` and `evaluation/evaluate.py` to examine retrieval and grounded-answer behavior, including questions that are outside the fixed document collection.

## Structure

```text
KidneyCare-RAG/
├── data/
├── src/
├── evaluation/
├── requirements.txt
├── .gitignore
└── README.md
```
