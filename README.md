# KidneyCare RAG

## Grounded CKD Education Assistant

KidneyCare RAG is a Retrieval-Augmented Generation (RAG) application designed to provide **grounded, educational information about Chronic Kidney Disease (CKD)** using a fixed collection of local healthcare documents.

The project was developed as a Human-Computer Interaction (HCI) group project. The application combines document retrieval, semantic search, open-source language generation, and a simple Gradio interface so users can ask CKD-related questions and see the sources used to support the response.

> **Educational use only:** KidneyCare RAG is not a diagnostic or clinical decision-support system. It does not diagnose conditions, prescribe medications, provide individualized treatment plans, or replace professional medical advice.

## Project Overview

The goal of KidneyCare RAG is to demonstrate how a grounded AI assistant can improve access to healthcare education while reducing unsupported responses through retrieval from a controlled document collection.

The application follows this workflow:

1. Load local CKD healthcare documents.
2. Extract text from PDF documents.
3. Clean and divide the text into overlapping chunks.
4. Generate semantic embeddings using Sentence Transformers.
5. Store the embeddings in a FAISS vector index.
6. Retrieve the most relevant document chunks for a user question.
7. Provide the retrieved context to an open-source Hugging Face language model.
8. Generate a grounded educational response.
9. Display the answer together with the retrieved document sources and similarity scores.
10. Reject questions when the available CKD documents do not contain sufficient relevant information.

## Application Screenshot

The following screenshot shows the working KidneyCare RAG Gradio interface running locally.

![KidneyCare RAG user interface](docs/kidneycare-ui.png)

**Interface:** The application provides a CKD question field, an **Ask KidneyCare** button, an answer/source area, and an educational-use disclaimer.

## Key Features

- **Local-document RAG:** Answers are grounded in the project's local healthcare document collection.
- **Semantic retrieval:** Sentence Transformers and FAISS are used to identify relevant passages.
- **Source transparency:** Retrieved source documents, page numbers, and similarity scores are shown with the response.
- **Out-of-scope rejection:** Questions unrelated to the available CKD knowledge base can be rejected rather than answered from general/current information.
- **Simple HCI:** A Gradio interface allows users to interact with the system without using the command line.
- **Reproducible setup:** Source code, requirements, evaluation questions, tests, and document-source information are included in the repository.
- **No live web search:** The application does not scrape websites or perform live web searches at runtime.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| User interface | Gradio |
| PDF processing | pypdf |
| Text embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector database/index | FAISS |
| Language model | Hugging Face Transformers (`google/flan-t5-base`) |
| ML framework | PyTorch |
| Testing | pytest |
| Source control | Git / GitHub |

## Data Sources

The knowledge base uses a fixed set of local CKD documents from authoritative healthcare organizations. The current project data directory contains:

- `CDC_CKD_2026.pdf`
- `CDC_CKD_Factsheet.pdf`
- `CDC_CKD_2023.pdf`
- `NIDDK_CKD_Guide.pdf`

The source information and official source references are documented in:

`data/SOURCES.md`

No patient records or personal medical information are required by the application.

## Repository Structure

```text
KidneyCare-RAG/
├── .github/
│   └── workflows/
│       └── validate.yml
├── data/
│   ├── README.md
│   └── SOURCES.md
├── evaluation/
│   ├── evaluate.py
│   └── questions.json
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── chunker.py
│   ├── document_loader.py
│   ├── rag_pipeline.py
│   └── vector_store.py
├── tests/
│   └── test_basic.py
├── .gitignore
├── README.md
└── requirements.txt
```

### Main source files

- `src/document_loader.py` — loads PDF/text documents and represents extracted content as document chunks.
- `src/chunker.py` — creates overlapping text chunks for retrieval.
- `src/vector_store.py` — creates Sentence Transformer embeddings and the FAISS similarity index.
- `src/rag_pipeline.py` — connects retrieval and language generation into the RAG workflow.
- `src/app.py` — launches the Gradio user interface.
- `evaluation/evaluate.py` — runs the predefined evaluation questions through the RAG pipeline.
- `evaluation/questions.json` — contains supported CKD questions and out-of-scope questions.
- `tests/test_basic.py` — basic document-loading and chunking tests.

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/sudheera96/KidneyCare-RAG.git
cd KidneyCare-RAG
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution for the virtual environment, use the appropriate Python/PowerShell execution-policy setting for your local environment.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The first execution may download the Sentence Transformers embedding model and the Hugging Face generation model.

## Run the Application

From the project root, run:

```powershell
python -m src.app
```

Gradio will start a local web interface. Open the local URL shown in the terminal, typically similar to:

```text
http://127.0.0.1:7860
```

The application initializes the document collection, builds the retrieval index, loads the language model, and then allows the user to submit CKD questions.

### Example questions

Questions within the intended scope include:

- What is chronic kidney disease?
- What are common risk factors for chronic kidney disease?
- How is chronic kidney disease tested or detected?
- What can people do to help prevent chronic kidney disease?
- What does CKD management generally involve?

Questions that require information outside the local CKD document collection should be rejected rather than answered using live/current information.

## Evaluation

The project includes a small evaluation set covering both supported and unsupported questions.

Run the evaluation from the project root with:

```powershell
python -m evaluation.evaluate
```

The evaluation reports:

- The question asked.
- Whether the question is expected to be supported by the knowledge base.
- The generated answer.
- Retrieved source documents.
- Source page numbers.
- Retrieval similarity scores.

### Evaluation categories

The current evaluation set contains:

- **5 supported CKD questions** covering CKD definition, risk factors, detection/testing, prevention, and management.
- **3 unsupported questions** covering current stock prices, recent sports results, and lottery numbers.

The unsupported questions are intentionally outside the application's static CKD knowledge base and are used to evaluate whether the system appropriately refuses to answer when sufficient relevant information is unavailable.

## Testing

Run the automated tests with:

```powershell
python -m pytest -q
```

The GitHub Actions workflow also performs source compilation, dependency installation, and pytest validation.

## Why RAG?

A general-purpose language model can produce fluent answers even when it does not have the appropriate evidence. KidneyCare RAG instead retrieves relevant passages from a controlled collection of CKD documents before generating an answer.

This approach provides three important benefits for the project:

1. **Grounding** — responses are based on retrieved project documents.
2. **Traceability** — users can see which documents and pages were retrieved.
3. **Scope control** — the application can decline questions that are not sufficiently supported by the local knowledge base.

## HCI Considerations

The interface was designed around a simple question-and-answer interaction:

- A clear application title communicates the purpose.
- The input field provides an example CKD question.
- A single primary action, **Ask KidneyCare**, submits the question.
- The answer and supporting sources are presented together.
- A visible educational-use disclaimer communicates the system's limitations.

The source display is particularly important for healthcare education because it gives users visibility into the documents used by the retrieval pipeline rather than presenting an unsupported answer without context.

## Safety and Scope

KidneyCare RAG is intentionally limited to **CKD education**.

The application does **not**:

- Diagnose a patient.
- Interpret an individual's medical records.
- Prescribe or recommend medications.
- Create individualized treatment plans.
- Replace a physician, nurse, dietitian, pharmacist, or other qualified healthcare professional.
- Provide live medical or current-event information.
- Perform live web searches or website scraping.

Users should consult qualified healthcare professionals for personal medical questions or decisions.

## Reproducibility

To reproduce the project:

1. Clone the GitHub repository.
2. Create and activate a Python virtual environment.
3. Install `requirements.txt`.
4. Ensure the required local CKD documents are available in `data/`.
5. Run `python -m src.app` to launch the application.
6. Run `python -m evaluation.evaluate` to reproduce the evaluation workflow.
7. Run `python -m pytest -q` to execute the automated tests.

The project does not require a live external healthcare API for the RAG workflow.

## GitHub Repository

**Repository:** https://github.com/sudheera96/KidneyCare-RAG

## Project Deliverables

The repository contains the main components needed to demonstrate the proposed system:

- RAG source code
- Local-document loading and preprocessing
- FAISS vector retrieval
- Hugging Face generation
- Gradio HCI interface
- Evaluation questions and evaluation script
- Automated tests
- Dependency specification
- Healthcare source documentation
- GitHub Actions validation workflow

## Important Note

This project is an academic prototype intended to demonstrate grounded information retrieval, natural-language interaction, and human-computer interaction for healthcare education. It should not be used as a clinical system or as a substitute for professional medical advice.
