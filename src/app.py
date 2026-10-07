from __future__ import annotations
import gradio as gr
from .rag_pipeline import KidneyCareRAG

rag: KidneyCareRAG | None = None

def initialize() -> str:
    global rag
    try:
        rag = KidneyCareRAG(data_dir="data")
        return "KidneyCare RAG is ready. Ask a CKD education question."
    except Exception as exc:
        rag = None
        return f"Startup error: {exc}"

def answer_question(question: str) -> str:
    if rag is None:
        return "The application is not initialized. Add the required documents to data/ and restart."
    return rag.ask_text(question)

with gr.Blocks(title="KidneyCare RAG") as demo:
    gr.Markdown(
        "# KidneyCare RAG\n"
        "### Grounded CKD Education Assistant\n"
        "Ask a question about chronic kidney disease. Answers use the project's local healthcare documents."
    )
    status = gr.Markdown("Initializing...")
    question = gr.Textbox(
        label="CKD question",
        placeholder="Example: What are common risk factors for chronic kidney disease?",
        lines=3,
    )
    submit = gr.Button("Ask KidneyCare")
    output = gr.Textbox(label="Answer and sources", lines=14)
    gr.Markdown(
        "**Educational use only.** This tool does not diagnose conditions, prescribe medications, "
        "or replace professional medical advice."
    )
    submit.click(answer_question, inputs=question, outputs=output)
    question.submit(answer_question, inputs=question, outputs=output)
    demo.load(initialize, outputs=status)

if __name__ == "__main__":
    demo.launch()
