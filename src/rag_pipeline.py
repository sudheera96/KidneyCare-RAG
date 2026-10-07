from __future__ import annotations

import os
import re
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
    """
    Grounded RAG assistant for chronic kidney disease education.

    Pipeline:
        Local PDFs
            ↓
        Document extraction
            ↓
        Chunking
            ↓
        SentenceTransformer embeddings
            ↓
        FAISS similarity search
            ↓
        Relevant context
            ↓
        FLAN-T5 generation
            ↓
        Grounded answer + sources

    The system is intentionally limited to educational CKD content.
    """

    def __init__(
        self,
        data_dir: str = "data",
        embedding_model: str | None = None,
        generation_model: str | None = None,
        top_k: int | None = None,
    ) -> None:

        self.embedding_model_name = embedding_model or os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )

        self.generation_model_name = generation_model or os.getenv(
            "GENERATION_MODEL",
            "google/flan-t5-base",
        )

        self.top_k = top_k or int(os.getenv("TOP_K", "4"))

        # ---------------------------------------------------------
        # Build local document retrieval index
        # ---------------------------------------------------------
        self.store = VectorStore(self.embedding_model_name)

        documents = load_documents(data_dir)

        if not documents:
            raise RuntimeError(
                f"No supported documents were found in '{data_dir}'. "
                "Add PDF or TXT healthcare documents before starting the app."
            )

        chunks = chunk_documents(documents)

        if not chunks:
            raise RuntimeError(
                "Documents were found, but no text chunks could be created."
            )

        self.store.build(chunks)

        # ---------------------------------------------------------
        # Load generation model
        # ---------------------------------------------------------
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.generation_model_name
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.generation_model_name
        )

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model.to(self.device)
        self.model.eval()

    # =============================================================
    # Question classification
    # =============================================================

    @staticmethod
    def _question_type(question: str) -> str:
        """
        Classify the question so retrieval can be improved.

        This is not a medical diagnosis. It only identifies the
        educational topic being requested.
        """

        q = question.lower()

        if any(
            phrase in q
            for phrase in [
                "risk factor",
                "risk factors",
                "cause of ckd",
                "causes of ckd",
                "causes chronic kidney",
                "who is at risk",
                "risk for kidney disease",
            ]
        ):
            return "risk_factors"

        if any(
            phrase in q
            for phrase in [
                "detected",
                "detect ckd",
                "diagnosed",
                "diagnosis",
                "diagnose",
                "testing",
                "tests",
                "test for ckd",
                "screening",
                "screen for ckd",
                "how do doctors know",
                "how is ckd found",
            ]
        ):
            return "detection"

        if any(
            phrase in q
            for phrase in [
                "symptom",
                "symptoms",
                "signs",
                "feel",
            ]
        ):
            return "symptoms"

        if any(
            phrase in q
            for phrase in [
                "what is ckd",
                "what is chronic kidney disease",
                "define ckd",
                "definition of ckd",
            ]
        ):
            return "definition"

        if any(
            phrase in q
            for phrase in [
                "treatment",
                "treated",
                "manage ckd",
                "management",
                "prevent",
                "prevention",
            ]
        ):
            return "management"

        return "general"

    # =============================================================
    # Retrieval query expansion
    # =============================================================

    @staticmethod
    def _expanded_query(question: str, question_type: str) -> str:
        """
        Add topic-specific retrieval terms.

        This improves semantic retrieval when the user's wording
        differs from the wording used in the healthcare documents.
        """

        if question_type == "detection":
            return (
                f"{question} "
                "chronic kidney disease detection diagnosis "
                "blood test urine test eGFR albumin urine albumin-creatinine "
                "kidney function testing"
            )

        if question_type == "risk_factors":
            return (
                f"{question} "
                "chronic kidney disease risk factors "
                "diabetes high blood pressure hypertension heart disease "
                "obesity family history age kidney disease"
            )

        if question_type == "symptoms":
            return (
                f"{question} "
                "chronic kidney disease symptoms signs "
                "swelling fatigue urination nausea"
            )

        if question_type == "definition":
            return (
                f"{question} "
                "chronic kidney disease kidney damage kidney function "
                "kidney failure"
            )

        if question_type == "management":
            return (
                f"{question} "
                "chronic kidney disease treatment management "
                "healthcare provider blood pressure diabetes"
            )

        return question

    # =============================================================
    # Context construction
    # =============================================================

    @staticmethod
    def _context(retrieved: list[RetrievedChunk]) -> str:
        """
        Build a compact context for the generation model.
        """

        blocks: list[str] = []

        for item in retrieved:

            location = (
                f"page {item.chunk.page}"
                if item.chunk.page
                else "text file"
            )

            text = item.chunk.text.strip()

            # Prevent a single large chunk from consuming
            # the entire model input.
            text = text[:2500]

            blocks.append(
                f"SOURCE: {item.chunk.source} ({location})\n"
                f"TEXT: {text}"
            )

        return "\n\n".join(blocks)

    # =============================================================
    # Sentence processing
    # =============================================================

    @staticmethod
    def _sentences(text: str) -> list[str]:
        """
        Convert retrieved text into reasonably clean sentences.
        """

        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return []

        sentences = re.split(r"(?<=[.!?])\s+", text)

        cleaned: list[str] = []

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            # Remove obvious PDF/header artifacts.
            if sentence.lower().startswith(
                (
                    "http://",
                    "https://",
                    "www.",
                    "source:",
                )
            ):
                continue

            if len(sentence.split()) < 5:
                continue

            cleaned.append(sentence)

        return cleaned

    @staticmethod
    def _clean_answer(answer: str) -> str:
        """
        Remove common FLAN-T5/PDF artifacts from generated answers.
        """

        answer = answer.strip()

        # Remove leading labels sometimes generated by the model.
        answer = re.sub(
            r"^(answer|response|output)\s*:\s*",
            "",
            answer,
            flags=re.IGNORECASE,
        )

        # Remove accidental HTML prefix.
        answer = re.sub(
            r"^html\s*",
            "",
            answer,
            flags=re.IGNORECASE,
        )

        # Remove excessive whitespace.
        answer = re.sub(r"\s+", " ", answer).strip()

        # Remove URLs accidentally copied from documents.
        answer = re.sub(
            r"https?://\S+",
            "",
            answer,
            flags=re.IGNORECASE,
        )

        answer = re.sub(r"\s+", " ", answer).strip()

        return answer

    # =============================================================
    # Grounded extractive answer
    # =============================================================

    @classmethod
    def _grounded_answer(
        cls,
        retrieved: list[RetrievedChunk],
        question_type: str,
    ) -> str:
        """
        Conservative fallback.

        When FLAN-T5 generates a poor answer, select sentences
        directly from the retrieved healthcare documents.

        This prevents unsupported information from being invented.
        """

        if not retrieved:
            return (
                "The available KidneyCare documents do not provide "
                "enough relevant information to answer this question."
            )

        keyword_groups = {
            "detection": [
                "blood",
                "urine",
                "test",
                "testing",
                "eGFR",
                "albumin",
                "creatinine",
                "kidney function",
                "detected",
                "diagnosed",
            ],
            "risk_factors": [
                "diabetes",
                "high blood pressure",
                "hypertension",
                "heart disease",
                "obesity",
                "family history",
                "older age",
                "risk",
            ],
            "symptoms": [
                "symptom",
                "swelling",
                "fatigue",
                "urination",
                "nausea",
            ],
            "definition": [
                "chronic kidney disease",
                "kidney damage",
                "kidney function",
                "kidney failure",
            ],
            "management": [
                "treatment",
                "manage",
                "health care",
                "healthcare",
                "blood pressure",
                "diabetes",
            ],
            "general": [],
        }

        keywords = keyword_groups.get(question_type, [])

        candidates: list[tuple[int, float, str]] = []

        for item in retrieved:

            sentences = cls._sentences(item.chunk.text)

            for sentence in sentences:

                lower = sentence.lower()

                keyword_score = sum(
                    1
                    for keyword in keywords
                    if keyword.lower() in lower
                )

                # Prefer sentences from stronger retrieved chunks.
                score = float(keyword_score) + float(item.score)

                candidates.append(
                    (
                        keyword_score,
                        score,
                        sentence,
                    )
                )

        if not candidates:
            text = retrieved[0].chunk.text.strip()

            if text:
                return text[:500]

            return (
                "The available KidneyCare documents do not provide "
                "enough relevant information to answer this question."
            )

        # Sort first by topic relevance, then by retrieval similarity.
        candidates.sort(
            key=lambda x: (x[0], x[1]),
            reverse=True,
        )

        selected: list[str] = []

        for keyword_score, _, sentence in candidates:

            if sentence in selected:
                continue

            # For topic-specific questions, prefer sentences that
            # actually contain the relevant terminology.
            if keywords and keyword_score == 0:
                continue

            selected.append(sentence)

            if len(selected) >= 2:
                break

        # If no keyword-specific sentence was found, use the
        # strongest retrieved sentence.
        if not selected:
            selected = [candidates[0][2]]

        answer = " ".join(selected)

        return cls._clean_answer(answer)

    # =============================================================
    # Generated answer quality check
    # =============================================================

    @staticmethod
    def _answer_is_acceptable(
        answer: str,
        question_type: str,
    ) -> bool:
        """
        Detect obviously poor FLAN-T5 output.
        """

        if not answer:
            return False

        cleaned = answer.lower().strip()

        # Common bad outputs.
        bad_answers = {
            "kidney disease",
            "kidney disease.",
            "ckd",
            "ckd.",
            "kidney disease by age, sex, and race/ethnicity",
            "html",
        }

        if cleaned in bad_answers:
            return False

        # Very short answers are usually incomplete.
        if len(cleaned.split()) < 7:
            return False

        # Obvious document heading contamination.
        bad_phrases = [
            "by age, sex, and race/ethnicity",
            "chronic kidney disease common",
            "more than risk factors",
            "more than 1 in",
            "1 in 5",
            "1 in 7",
            "cs 363495-a",
            "accessible version",
        ]

        if any(phrase in cleaned for phrase in bad_phrases):
            return False

        # Answers containing many URLs or PDF artifacts are rejected.
        if "http://" in cleaned or "https://" in cleaned:
            return False

        if cleaned.count("|") > 1:
            return False

        # Topic-specific sanity checks.
        if question_type == "detection":
            detection_terms = [
                "blood",
                "urine",
                "test",
                "testing",
                "egfr",
                "albumin",
                "creatinine",
            ]

            if not any(term in cleaned for term in detection_terms):
                return False

        if question_type == "risk_factors":
            risk_terms = [
                "diabetes",
                "blood pressure",
                "hypertension",
                "heart disease",
                "obesity",
                "family history",
                "age",
                "risk",
            ]

            if not any(term in cleaned for term in risk_terms):
                return False

        return True

    # =============================================================
    # Main RAG operation
    # =============================================================

    def ask(self, question: str) -> RAGResponse:

        question = question.strip()

        if not question:
            return RAGResponse(
                "Please enter a CKD question.",
                [],
            )

        # ---------------------------------------------------------
        # Identify educational topic
        # ---------------------------------------------------------
        question_type = self._question_type(question)

        # ---------------------------------------------------------
        # Expand retrieval query
        # ---------------------------------------------------------
        retrieval_query = self._expanded_query(
            question,
            question_type,
        )

        # ---------------------------------------------------------
        # Retrieve relevant healthcare chunks
        # ---------------------------------------------------------
        retrieved = self.store.search(
            retrieval_query,
            self.top_k,
        )

        # ---------------------------------------------------------
        # Reject unrelated questions
        # ---------------------------------------------------------
        if not retrieved or retrieved[0].score < 0.25:
            return RAGResponse(
                "The available KidneyCare documents do not provide "
                "enough relevant information to answer this question.",
                retrieved,
            )

        # ---------------------------------------------------------
        # Build grounded context
        # ---------------------------------------------------------
        context = self._context(retrieved)

        # ---------------------------------------------------------
        # Generation prompt
        # ---------------------------------------------------------
        prompt = f"""
You are KidneyCare RAG, an educational assistant focused only on
chronic kidney disease (CKD).

Answer the user's question using ONLY the healthcare document
context provided below.

IMPORTANT RULES:
- Answer the exact question.
- Give 2 to 4 concise sentences.
- Use simple educational language.
- Do not invent facts.
- Do not use information outside the provided documents.
- Do not diagnose anyone.
- Do not prescribe medication.
- Do not give individualized medical advice.
- Do not include URLs.
- Do not copy document headings.
- Do not mention source filenames in the answer.
- Do not answer unrelated questions.
- If the context does not support the question, say that the
  documents do not provide enough information.

QUESTION:
{question}

DOCUMENT CONTEXT:
{context}

ANSWER:
""".strip()

        # ---------------------------------------------------------
        # Tokenize
        # ---------------------------------------------------------
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        ).to(self.device)

        # ---------------------------------------------------------
        # Generate
        # ---------------------------------------------------------
        with torch.no_grad():

            output = self.model.generate(
                **inputs,
                max_new_tokens=100,
                min_new_tokens=8,
                do_sample=False,
                num_beams=4,
                no_repeat_ngram_size=3,
                early_stopping=True,
            )

        answer = self.tokenizer.decode(
            output[0],
            skip_special_tokens=True,
        ).strip()

        answer = self._clean_answer(answer)

        # ---------------------------------------------------------
        # Validate generated answer
        # ---------------------------------------------------------
        if not self._answer_is_acceptable(
            answer,
            question_type,
        ):

            # Use a conservative grounded answer directly from
            # retrieved document text.
            answer = self._grounded_answer(
                retrieved,
                question_type,
            )

        return RAGResponse(
            answer=answer,
            sources=retrieved,
        )

    # =============================================================
    # UI formatting
    # =============================================================

    def ask_text(self, question: str) -> str:

        response = self.ask(question)

        lines = [
            response.answer,
            "",
            "Sources:",
        ]

        if not response.sources:
            lines.append("No sources retrieved.")

        for item in response.sources:

            location = (
                f"page {item.chunk.page}"
                if item.chunk.page
                else "text file"
            )

            lines.append(
                f"- {item.chunk.source} ({location}) "
                f"| similarity={item.score:.3f}"
            )

        return "\n".join(lines)