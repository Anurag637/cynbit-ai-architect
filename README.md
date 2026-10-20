# ⚡ Revio 2.0: AI-Powered Review Intelligence & Crisis Detection System

> **Technical Assessment Submission: AI/ML Engineer Intern**  
> **Candidate:** Anurag Pandey  
> **Target Company:** [Cynbit Technologies Private Limited](https://cynbit.in) (Jaipur, Rajasthan)  
> **Candidate Application Reference:** `cmu2qy3wh000004lc0uqicfco`  
> **Assessment Task:** *Identify an AI Opportunity for Cynbit & Build a Working Proof of Concept*  
> **Deliverables:** (1) AI Opportunity Report, (2) Functional AI/ML Proof of Concept, (3) Technical Approach Report  

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg?style=flat&logo=streamlit)](https://streamlit.io/)
[![Test Suite](https://img.shields.io/badge/PyTest-19%20Passed%20(100%25)-success.svg?style=flat&logo=pytest)](https://pytest.org/)
[![Proof of Concept](https://img.shields.io/badge/Status-Functional%20PoC-orange.svg?style=flat)](https://github.com/Anurag637/cynbit-ai-architect)

---

## 📌 Executive Summary

**Cynbit Technologies Private Limited** is a software engineering and digital transformation consultancy headquartered in Jaipur, Rajasthan. Operating under the brand identity *"The Optimistic Architect"*, Cynbit maintains client digital engineering services alongside proprietary B2B SaaS products including **Revio** (reputation and review aggregator) and **TenantEase** (property management), as well as talent accelerators (**Cynbit Studio / BitElevate**).

### The Selected AI Opportunity
While generic reputation management platforms merely compute high-level star averages and output robotic canned replies, multi-location enterprise brands (hospitality, clinics, restaurants, retail) suffer operational blindness and acute liability risks.

**Revio 2.0** upgrades Cynbit's flagship SaaS into a **functional Proof of Concept for Brand Intelligence and Crisis Triage**:
- **Aspect-Based Sentiment Analysis (ABSA):** Automatically parses customer reviews into 6 operational categories (*Customer Service, Product & Food Quality, Speed & Turnaround Time, Cleanliness & Ambience, Pricing & Value, Billing & Transactions*).
- **Crisis & Urgency Screening Index (0–100):** Heuristic screening estimate prioritizing reviews containing legal threats (police, consumer court, lawsuits), health/safety hazards (food poisoning, pests), or fraud allegations for urgent human review.
- **Governed Response Drafting:** Synthesizes context-grounded replies aligned with brand personas, support policies, and deterministic zero-liability guardrails that forbid hallucinating refunds or admitting unverified legal fault.
- **Human-in-the-Loop (HITL) Workflow:** Enforces human approval and editing for every response before dispatch.
- **Multi-Location Analytics & Ingestion:** Supports live CSV upload with schema validation, synthetic data labeling, and export of analyzed datasets.

---

## 🗺️ System Architecture

```
                   +-------------------------------------------------------------+
                   |         Multi-Channel Customer Review Stream (CSV / API)    |
                   |          (review_text, star_rating, branch_name, date)      |
                   +-------------------------------------------------------------+
                                                  │
                                                  ▼
                   +-------------------------------------------------------------+
                   |           Revio Ingestion & Schema Validation Gateway       |
                   |       (Column Normalization, Row Filtering, Error Handling) |
                   +-------------------------------------------------------------+
                                                  │
                                                  ▼
              ┌───────────────────────────────────┴───────────────────────────────────┐
              ▼                                                                       ▼
+------------------------------------+                             +------------------------------------+
| Aspect-Based Sentiment Engine      |                             | Crisis & Urgency Screening Engine  |
| (6 Categories, Contrastive Clauses,|                             | (0-100 Screening Index, Evidence-  |
|  Negation Inversion, Polarity)     |                             |  Matched Vectors, SLA Triage)      |
+------------------------------------+                             +------------------------------------+
              │                                                                       │
              └───────────────────────────────────┬───────────────────────────────────┘
                                                  │
                                                  ▼
                   +-------------------------------------------------------------+
                   |             Multi-Agent Response Drafting Synthesizer       |
                   |  - Persona Alignment (Empathetic / Formal / Warm / Exec)    |
                   |  - Safe Offline Policy Templates (Deterministic Fallback)   |
                   |  - Pluggable LLM Provider Hook (Gemini / OpenAI via .env)   |
                   +-------------------------------------------------------------+
                                                  │
                                                  ▼
                   +-------------------------------------------------------------+
                   |           Compliance & Anti-Hallucination Guardrails        |
                   |  (Intercepts Unverified Refunds, Concessions, Fault Claims) |
                   +-------------------------------------------------------------+
                                                  │
                                                  ▼
                   +-------------------------------------------------------------+
                   |             Human-in-the-Loop (HITL) Review Queue           |
                   |    (Mandatory Review & Edit Before Public Reply Sign-off)   |
                   +-------------------------------------------------------------+
                                                  │
                                                  ▼
                   +-------------------------------------------------------------+
                   |       Simulated Channel Dispatch (Mock Platform Connector)  |
                   +-------------------------------------------------------------+
```

---

## 🔬 System Components: What is ML, Deterministic, or Simulated?

To provide complete technical transparency, every subsystem is classified below:

| Subsystem | Underlying Technology | Why This Choice? | Current Status in PoC |
| :--- | :--- | :--- | :--- |
| **Review Ingestion & Validation** | Python, Pandas, Schema Parser | Strict normalization of column names and validation of 1-5 star ratings | **Fully Implemented** |
| **Aspect Sentiment Analysis (ABSA)** | Rule-based Lexical Engine + Clause Splitter | Fast (< 1 ms), zero API cost, transparent logic, negation & Hinglish support | **Fully Implemented (Baseline)** |
| **Crisis & Urgency Triage** | Weighted Threat Keyword Clustering | High recall screening estimate for urgent triage routing | **Fully Implemented (Screening)** |
| **Response Generation** | Grounded Policy Fallback + Optional LLM Hook | Offline template safety + optional Google Gemini / OpenAI via `.env` | **Fully Implemented** |
| **Anti-Hallucination Guardrails** | Deterministic Regex Filter (`FORBIDDEN_PHRASES`) | Intercepts liability admissions and unverified monetary refund claims | **Fully Implemented** |
| **Human-in-the-Loop Interface** | Streamlit Approval & Edit Box | Enforces human oversight on every drafted message | **Fully Implemented** |
| **Incident Case Reference** | Hash-based Generator (`#SIM-XXXX`) | Generates reproducible tracking references for internal routing | **Simulated (Clearly Labeled)** |
| **External Publishing Connectors** | Mock Connector | Simulates Google Maps / Yelp API dispatch without sending real requests | **Simulated (Clearly Labeled)** |

---

## 📦 Repository Structure

```
cynbit-ai-architect/
├── reports/
│   ├── AI_OPPORTUNITY_REPORT.md       # [Deliverable 1] Strategic AI Opportunity Analysis
│   ├── TECHNICAL_APPROACH_REPORT.md   # [Deliverable 3] Technical Blueprint & Measured Evaluation
│   └── evaluation_results.json        # Output of empirical evaluation script
├── src/
│   ├── __init__.py
│   ├── config.py                      # Taxonomies, crisis weights, persona definitions, .env loading
│   ├── ingestion.py                   # CSV schema validation and malformed row filtering
│   ├── data_generator.py              # Synthetic benchmark review generator (labeled synthetic)
│   ├── analyzer.py                    # Aspect-Based Sentiment Analysis & Clause Decomposer
│   ├── crisis_detector.py             # Crisis Screening Index & Evidence-Matched Vectors
│   ├── response_generator.py          # Grounded response synthesizer with legal guardrails
│   ├── analytics.py                   # Multi-location enterprise aggregation engine
│   └── api.py                         # FastAPI REST microservice with OpenAPI documentation
├── tests/
│   ├── test_analyzer.py               # Unit tests for ABSA, negation, and Hinglish keywords
│   ├── test_crisis_detector.py        # Unit tests for crisis scoring, triggers, and SLA targets
│   ├── test_response_generator.py     # Unit tests for guardrails, anti-hallucination, and HITL
│   ├── test_ingestion.py              # Unit tests for CSV schema validation and error recovery
│   └── test_api.py                    # Unit tests for FastAPI REST endpoints
├── data/
│   ├── sample_reviews.csv             # 50 synthetic benchmark reviews (CSV format)
│   ├── sample_reviews.json            # 50 synthetic benchmark reviews (JSON format)
│   └── labeled_eval_dataset.json      # 20 ground truth labeled reviews for empirical evaluation
├── app.py                             # [Deliverable 2] Interactive Streamlit Enterprise Dashboard
├── evaluate.py                        # Reproducible empirical evaluation benchmark script
├── submission_notes.txt               # Candidate portal submission text
├── requirements.txt                   # Project dependencies
├── .env.example                       # Environment configuration template
├── .gitignore                         # Excludes secrets, caches, and build artifacts
├── Dockerfile                         # Container definition
└── README.md                          # Comprehensive documentation
```

---

## 📊 Empirical Evaluation & Measured Results

We evaluated Revio 2.0 against a curated ground truth benchmark dataset (`data/labeled_eval_dataset.json`) containing 20 reviews covering positive, negative, mixed-polarity, negation, Hinglish slang (*bakwas*, *battameez*, *lajawab*, *loot*), and severe crisis categories (food poisoning, fraud, threats).

Run the reproducible evaluation script:
```powershell
python evaluate.py
```

### Measured Benchmark Metrics:
* **Aspect Classification Precision:** **81.67%**
* **Aspect Classification Recall:** **82.50%**
* **Aspect Macro-F1 Score:** **80.67%**
* **Crisis Detection Precision:** **100.00%**
* **Crisis Detection Recall:** **100.00%**
* **Crisis Detection F1-Score:** **100.00%**
* **Critical Safety Category False Negatives:** **0 / 6 (Zero)** on the evaluation dataset
* **Guardrail Concession Leaks:** **0 (Zero)** unverified refund or liability leaks
* **Mean Processing Latency:** **~0.73 ms / review** (P95: 0.77 ms) measured with `time.perf_counter()` over 50 iterations on CPU.

> **Honest Evaluation Note:** The 100% recall was achieved on the defined 20-sample benchmark set. In real-world open-domain deployments, rare idioms or subtle sarcasm may not trigger keywords; this is why Human-in-the-Loop review is mandatory.

---

## 🚀 Quickstart Guide (Windows PowerShell)

### 1. Local Environment Setup
```powershell
# Navigate to project directory
cd e:\cynbit-ai-architect

# (Optional) Copy environment template and configure keys if desired
Copy-Item .env.example .env

# Verify dependencies
pip install -r requirements.txt
```

### 2. Run the Full Automated Test Suite (19 Tests)
```powershell
python -m pytest -v
```
*Expected Result:* **19 passed in ~1.0s (100% test pass rate across parsing, classification, guardrails, and APIs).**

### 3. Run the Empirical Benchmark Evaluation
```powershell
python evaluate.py
```
*Expected Result:* Evaluates 20 labeled test cases, outputs macro metrics, and saves results to `reports/evaluation_results.json`.

### 4. Run the Interactive Streamlit Dashboard
```powershell
python -m streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser:
* **Executive Command Center:** View live aspect health radar, crisis counts, and export analyzed CSVs.
* **Interactive AI Review Lab:** Test preset enterprise scenarios or custom reviews, inspect ABSA pills, edit drafted replies, and approve responses.
* **Multi-Location Deep-Dive:** Filter reviews by branch or risk tier.
* **Strategic Architecture & Reports:** View measured evaluation metrics and download deliverables.

### 5. Run the FastAPI REST Microservice (Optional)
```powershell
python -m uvicorn src.api:app --reload --port 8000
```
* Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
* Health Check Endpoint: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🔒 Security, Privacy & Compliance Notes

1. **Zero Secret Exposure:** API keys are never hardcoded or committed to version control. They are read dynamically from environment variables (`.env`).
2. **Offline Fallback Guarantee:** The system functions completely without an internet connection or external LLM API key, utilizing deterministic policy templates.
3. **No Real Public Posts:** In this Proof of Concept, review publishing actions are simulated mock connectors. No real public replies or customer communications are dispatched.
4. **Data Privacy (DPDP Act 2023):** Review ingestion supports anonymous identifiers and customer name redaction.

---

## 👨‍💻 Candidate Profile

* **Name:** Anurag Pandey
* **Degree:** B.Tech in Computer Science Engineering (Artificial Intelligence & Machine Learning)
* **University:** K. R. Mangalam University (Batch of 2027)
* **Email:** [anurag637@zohomail.in](mailto:anurag637@zohomail.in)
* **GitHub:** [https://github.com/Anurag637](https://github.com/Anurag637)
* **LinkedIn:** [https://www.linkedin.com/in/anurag637/](https://www.linkedin.com/in/anurag637/)
* **Application Token:** `cmu2qy3wh000004lc0uqicfco`

---

*(c) 2026 Cynbit Technologies Private Limited Assessment Submission.*
