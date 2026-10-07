# KidneyCare RAG — Evaluation Report

## 1. Evaluation Overview

KidneyCare RAG was evaluated to verify two core behaviors:

1. **Grounded CKD question answering** — questions that should be answerable from the project's local CKD documents.
2. **Out-of-scope question rejection** — questions that are unrelated to the project's CKD document collection.

The evaluation uses the project's existing retrieval and generation pipeline. For each question, the evaluation script reports:

- Whether the question is expected to be supported by the project documents.
- The generated answer.
- The retrieved document sources.
- The page numbers of the retrieved content.
- The similarity score for each retrieved result.

### Evaluation Set

| Category | Number of Questions |
|---|---:|
| Supported CKD questions | 5 |
| Unsupported / out-of-scope questions | 3 |
| **Total** | **8** |

The evaluation was run with:

```powershell
python -m evaluation.evaluate
```

---

## 2. Evaluation Results

### Supported CKD Questions

#### 1. What is chronic kidney disease?

**Expected supported:** Yes

**Generated answer:**

> US adults–about 35.5 million people–are estimated to have CKD.

**Retrieved sources:**

| Source | Page | Similarity |
|---|---:|---:|
| CDC_CKD_2026.pdf | 1 | 0.679 |
| CDC_CKD_Factsheet.pdf | 1 | 0.659 |
| NIDDK_CKD_Guide.pdf | 1 | 0.650 |
| CDC_CKD_2023.pdf | 1 | 0.643 |

**Observation:** Relevant CKD documents were retrieved with relatively high similarity scores. The generated response, however, answers with a CKD prevalence statistic rather than providing a direct definition. This identifies an area for future answer-quality refinement.

---

#### 2. What are common risk factors for chronic kidney disease?

**Expected supported:** Yes

**Generated answer:**

> Diabetes, high blood pressure, heart disease, obesity, a family history of CKD, inherited kidney disorders, past damage to the kidneys, and older age.

**Retrieved sources:**

| Source | Page | Similarity |
|---|---:|---:|
| CDC_CKD_Factsheet.pdf | 1 | 0.675 |
| CDC_CKD_2023.pdf | 1 | 0.668 |
| CDC_CKD_2026.pdf | 1 | 0.646 |
| CDC_CKD_2023.pdf | 1 | 0.645 |

**Observation:** The system retrieved relevant CKD sources and generated a concise answer listing common risk factors.

---

#### 3. How is chronic kidney disease tested or detected?

**Expected supported:** Yes

**Generated answer:**

> It is defined as r eduction of kidney function — defined as an eGFR < 60 mL/min/1.73 m2 for > 3 months AND/OR evidence of kidney damage, including persistent albuminuria — defined as > 30 mg of urine albumin per gram of urine creatinine for > 3 months Kidney failure is typically definedas an eGFR < 15 mL/min/1.73 m2. ” Percentage of US Adults Aged 18 Y ears and Older With Both CKD and Diagnosed Diabetes Who Were Prescribed Blood Pressure–Lowering Medications,† by Age, Sex, and Race/Ethnicity Testing and Treatment: Find it Early, Treat it Early • Test for CKD regularly in people who have diabetes, high blood pressure, or other risk factors for CKD.

**Retrieved sources:**

| Source | Page | Similarity |
|---|---:|---:|
| CDC_CKD_2023.pdf | 2 | 0.673 |
| NIDDK_CKD_Guide.pdf | 4 | 0.652 |
| NIDDK_CKD_Guide.pdf | 7 | 0.642 |
| NIDDK_CKD_Guide.pdf | 8 | 0.628 |

**Observation:** The retrieval results are relevant to CKD detection/testing. The generated response contains document text and formatting artifacts and is longer than desired. This is a known answer-generation quality issue and an opportunity for future prompt/model refinement.

---

#### 4. What can people do to help prevent chronic kidney disease?

**Expected supported:** Yes

**Generated answer:**

> Talk to a kidney doctor about treatment options

**Retrieved sources:**

| Source | Page | Similarity |
|---|---:|---:|
| CDC_CKD_2023.pdf | 1 | 0.703 |
| CDC_CKD_2023.pdf | 3 | 0.683 |
| NIDDK_CKD_Guide.pdf | 1 | 0.662 |
| CDC_CKD_2023.pdf | 1 | 0.640 |

**Observation:** Relevant sources were retrieved, although the generated answer is narrower than the question and does not fully summarize prevention guidance.

---

#### 5. What does CKD management generally involve?

**Expected supported:** Yes

**Generated answer:**

> identifying and slowing progression among patients at highest risk for progression to kidney failure

**Retrieved sources:**

| Source | Page | Similarity |
|---|---:|---:|
| NIDDK_CKD_Guide.pdf | 1 | 0.792 |
| NIDDK_CKD_Guide.pdf | 3 | 0.740 |
| NIDDK_CKD_Guide.pdf | 5 | 0.709 |
| CDC_CKD_2023.pdf | 2 | 0.683 |

**Observation:** The system retrieved highly relevant CKD management content and generated an answer grounded in the retrieved material.

---

## 3. Unsupported / Out-of-Scope Questions

### 6. What is the current stock price of Apple?

**Expected supported:** No

**Generated answer:**

> The available KidneyCare documents do not provide enough relevant information to answer this question.

**Retrieved sources:**

| Source | Page | Similarity |
|---|---:|---:|
| CDC_CKD_Factsheet.pdf | 1 | 0.111 |
| CDC_CKD_Factsheet.pdf | 4 | 0.107 |
| CDC_CKD_Factsheet.pdf | 4 | 0.106 |
| CDC_CKD_Factsheet.pdf | 1 | 0.097 |

**Observation:** The system correctly refused to provide an answer because the question is outside the CKD document collection.

---

### 7. Who won the latest Super Bowl?

**Expected supported:** No

**Generated answer:**

> The available KidneyCare documents do not provide enough relevant information to answer this question.

**Retrieved sources:**

| Source | Page | Similarity |
|---|---:|---:|
| CDC_CKD_Factsheet.pdf | 4 | 0.058 |
| CDC_CKD_Factsheet.pdf | 1 | 0.039 |
| CDC_CKD_Factsheet.pdf | 1 | 0.030 |
| CDC_CKD_2026.pdf | 1 | 0.028 |

**Observation:** The system correctly refused to answer an unrelated current-events question.

---

### 8. What are the lottery numbers for tonight?

**Expected supported:** No

**Generated answer:**

> The available KidneyCare documents do not provide enough relevant information to answer this question.

**Retrieved sources:**

| Source | Page | Similarity |
|---|---:|---:|
| CDC_CKD_2023.pdf | 4 | 0.159 |
| CDC_CKD_2023.pdf | 4 | 0.155 |
| CDC_CKD_Factsheet.pdf | 4 | 0.137 |
| CDC_CKD_Factsheet.pdf | 1 | 0.134 |

**Observation:** The system correctly refused to answer an unrelated question.

---

## 4. Retrieval Score Summary

Across the evaluation:

- Supported CKD questions produced top retrieved similarity scores of approximately **0.64–0.79**.
- Unsupported questions produced substantially lower retrieved similarity scores of approximately **0.03–0.16**.

This indicates that the retrieval layer generally distinguishes questions that are semantically related to the CKD knowledge base from unrelated questions.

The similarity scores should be interpreted as **retrieval signals**, not clinical accuracy measurements.

---

## 5. Evaluation Interpretation

The evaluation demonstrates that the current KidneyCare RAG prototype can:

- Retrieve relevant CKD information for supported questions.
- Return document names, page numbers, and similarity scores for retrieved content.
- Ground responses in the project's local healthcare documents.
- Reject unrelated questions when the retrieval similarity is below the configured relevance threshold.
- Avoid using live web search or external runtime information.

The evaluation also identifies areas for improvement:

- Some generated answers are too short or incomplete.
- Some answers may select a related passage that does not directly answer the user's wording.
- One detection/testing response contains document formatting artifacts and excessive copied text.
- A future evaluation could add human answer-quality ratings, faithfulness checks, retrieval precision/recall, or additional test questions.

These limitations are documented intentionally rather than presenting unsupported accuracy claims.

---

## 6. Safety and Scope

KidneyCare RAG is an **educational prototype** for chronic kidney disease information.

It does not:

- Diagnose medical conditions.
- Prescribe medications.
- Generate individualized treatment plans.
- Analyze personal medical records.
- Provide live medical, financial, sports, or other current information.
- Replace a qualified healthcare professional.

The unsupported-question tests are included to verify that the system remains grounded in its intended document collection.

---

## 7. Reproducing the Evaluation

From the repository root:

```powershell
python -m evaluation.evaluate
```

For automated unit tests:

```powershell
python -m pytest -q
```

The evaluation questions are stored in:

```text
evaluation/questions.json
```

The evaluation implementation is:

```text
evaluation/evaluate.py
```

---

## 8. Conclusion

The evaluation confirms that the KidneyCare RAG prototype is functioning as a document-grounded CKD education assistant. The retrieval component successfully identifies relevant CKD documents and produces substantially lower similarity scores for unrelated questions. The results also show specific answer-generation limitations that can guide future refinement of the system.

This evaluation is a **functional and retrieval-grounding assessment**, not a clinical validation study.
