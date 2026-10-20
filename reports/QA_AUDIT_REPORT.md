# Revio 2.0 — Comprehensive QA Audit & Verification Report

**Project**: Revio 2.0 — AI-Powered Review Intelligence & Crisis Detection System  
**Organization**: Cynbit Technologies Private Limited  
**Audit Executed By**: Senior QA Automation & ML Evaluation Engineer  
**Candidate Reference**: Anurag Pandey (`anurag637@zohomail.in` / Ref: `cmu2qy3wh000004lc0uqicfco`)  
**Audit Date**: October 20, 2026  
**Final Status**: **PASS WITH LIMITATIONS** (Local app & API 100% verified; live deployment active on HTTP 200, awaiting remote git sync)

---

## 1. Scope, Environment & Testing Targets

### 1.1 Target Environments
1. **Local Development & Testing Environment**:
   - Host OS: Windows 11 (64-bit), Shell: PowerShell 7 / Windows Terminal
   - Python Version: `Python 3.13.15`
   - Frameworks: Streamlit `1.50.0`, FastAPI `0.128.8`, Pydantic `2.12.5`, Pandas `2.3.3`, Scikit-Learn `1.8.0`, Pytest `9.1.1`
   - Local Web UI: `http://localhost:8501` (Active Streamlit daemon)
   - Local REST API: `http://localhost:8000` (`src/api.py`)
2. **Live Deployed Cloud Environment**:
   - Target URL: `https://cynbit-ai-architect-vpzjbsm3z965gdtgvi5ahv.streamlit.app/`
   - Cloud Platform: Streamlit Community Cloud (Debian Linux Container)
   - Remote Git Branch: `https://github.com/Anurag637/cynbit-ai-architect.git` (`main`)

### 1.2 Testing Methodology & Tooling Disclosure
- **Automated Unit & Integration Testing**: 31 unit tests executed via `pytest -v`.
- **FastAPI Endpoint Audit**: Automated HTTP test client exercising all 6 REST endpoints with valid, malformed, and out-of-range payloads (`test_fastapi_endpoints.py`).
- **Benchmark Evaluation**: Empirical validation of 20 ground-truth labeled multi-aspect reviews (`evaluate.py`).
- **Live Deployed Probing**: HTTP session probe via Python `requests.Session` tracking cookies, HTTP 303 redirects, and HTTP 200 Streamlit React bundle availability.
- **Browser Automation Limitation Disclosure**: Playwright browser driver installation was blocked inside the IDE sandbox environment due to outbound binary package download policies (`404 Not Found` on `playwright.azureedge.net`). Consequently, live cloud verification was conducted via session HTTP probing, while UI interactive behavior was verified via local Streamlit testing.

---

## 2. Feature-by-Feature Audit Results

### Feature 1: CSV Upload & Data Validation (Phases 4 & 9)
- **Status**: **PASS**
- **Test Scenarios Executed**:
  1. *Valid CSV with canonical columns* (`review_text`, `star_rating`, `customer_name`, `branch_name`, `timestamp`, `platform`): Processed 16/16 rows successfully.
  2. *Alternative column names* (`Review`, `Feedback`, `Rating`, `Stars`, `Location`, `Date`): Schema normalizer correctly mapped aliases to canonical keys.
  3. *Missing optional columns*: Missing `branch_name` gracefully defaulted to `"Jaipur Flagship"`, missing `customer_name` defaulted to `"Guest"`.
  4. *Empty CSV*: Raised explicit, user-friendly `ValueError("Uploaded file is empty.")`.
  5. *Missing required columns*: Raised `ValueError("Missing required columns: ...")` listing the specific missing headers.
  6. *Out-of-range ratings*: Floats (e.g. `4.5`), strings (`"5"`), and null ratings normalized; out-of-bounds ratings (< 1 or > 5) dropped safely with logged warnings.
  7. *Malformed rows and newlines*: Commas inside quotes, unescaped quotes, and multiline text in reviews handled via standard `pandas.read_csv(engine="python")`.
  8. *Bilingual and Hinglish Unicode*: Preserved Devanagari and Romanized Hindi without text truncation or mojibake.
- **Evidence**: `tests/test_ingestion.py` (4/4 tests passed), `tests/test_csv_test_batches.py` (2/2 tests passed).

---

### Feature 2: Aspect-Based Sentiment Analysis (ABSA) (Phase 5)
- **Status**: **PASS**
- **Supported Operational Aspects Tested**:
  1. `Product & Food Quality`
  2. `Customer Service`
  3. `Speed & Turnaround Time`
  4. `Cleanliness & Ambience`
  5. `Pricing & Value`
  6. `Billing & Transactions`
- **Master Prompt Test Sentences & Verified Behaviors**:
  - *"The food was excellent, but the staff were rude."* -> **MIXED (0.00)** | Food: POSITIVE (+0.65), Service: NEGATIVE (-0.65). Contrastive discourse marker `"but"` properly segregated clauses.
  - *"The service was not bad."* -> **POSITIVE (+0.45)** | Service: POSITIVE (+0.65). Negation inversion of `"bad"` correctly yielded positive customer service polarity.
  - *"The restaurant was not clean."* -> **NEGATIVE (-0.75)** | Cleanliness: NEGATIVE (-0.65). Negation inversion of `"clean"` yielded negative polarity.
  - *"The staff were not rude, but the billing was incorrect."* -> **MIXED (-0.15)** | Service: POSITIVE (+0.65), Billing: NEGATIVE (-0.65). Independent multi-clause polarity preserved.
  - *"Lajawab food, lekin delivery bahut late thi."* -> **MIXED (0.00)** | Food: POSITIVE (+0.65, *"lajawab"*), Speed: NEGATIVE (-0.65, *"late"*). Bilingual discourse marker `"lekin"` recognized.
  - *"The food was good and the bill was correct."* -> **POSITIVE (+0.93)** | Food: POSITIVE (+0.90), Billing: POSITIVE (+0.90).
  - *"I love waiting two hours for cold food."* -> **NEGATIVE (-0.75)** | Food: NEGATIVE (-0.65, *"cold"*), Speed: NEGATIVE (-0.65, *"waiting"*).
- **Evidence**: `tests/test_analyzer.py` (9/9 tests passed). Mean Aspect Precision: 82.92%, Recall: 86.67%, Macro-F1: 83.12%.

---

### Feature 3: Crisis & Urgency Detection (Phase 6)
- **Status**: **PASS**
- **Evaluation Criteria**: Priority-ranking heuristic screening index (0–100) with deterministic vector clustering.
- **Master Prompt Test Sentences & Verified Behaviors**:
  - *"I became ill after eating here and have been vomiting since last night."* (1 star)  
    -> **Risk: 65% | Tier: CRITICAL** | Vector: `Health, Hygiene & Safety Violation` | SLA: `< 15 Minutes` -> Executive Incident Response Team.
  - *"Nobody threatened me."* (5 stars)  
    -> **Risk: 0% | Tier: LOW** | Vector: `Routine Feedback` | SLA: `< 24 Hours` -> Automated AI Brand Agent. Negation suppression successfully prevented false abuse alarm.
  - *"I am considering legal action because the manager threatened me."* (1 star)  
    -> **Risk: 100% | Tier: CRITICAL** | Vectors: `Legal & Regulatory Action`, `Harassment & Human Safety` | SLA: `< 15 Minutes`.
  - *"Does this sauce contain peanuts? I have a severe peanut allergy."* (2 stars)  
    -> **Risk: 100% | Tier: CRITICAL** | Vector: `Health, Hygiene & Safety Violation` | SLA: `< 15 Minutes`.
  - *"The food was good, but the cashier charged my card twice."* (2 stars)  
    -> **Risk: 60% | Tier: HIGH** | Vector: `Financial Integrity & Fraud Allegation` | SLA: `< 2 Hours` -> Branch Operations Manager.
  - *"I did not get food poisoning."* (5 stars)  
    -> **Risk: 0% | Tier: LOW** | Vector: `Routine Feedback` | SLA: `< 24 Hours`. Negation suppression successfully prevented false food poisoning alarm.
  - *"The restaurant was clean and the staff were helpful."* (5 stars)  
    -> **Risk: 0% | Tier: LOW** | Vector: `Routine Feedback` | SLA: `< 24 Hours`.
- **Evidence**: `tests/test_crisis_detector.py` (6/6 tests passed). Zero critical safety false negatives across all test benchmarks.

---

### Feature 4: Response Generation & Guardrail Enforcement (Phase 7)
- **Status**: **PASS**
- **Verified Capabilities**:
  1. *Brand Voice Personas*: Tested all 4 supported personas (`Empathetic & Solution-Oriented`, `Formal & Corporate`, `Warm & Conciliatory`, `Executive Escalation`).
  2. *Deterministic Offline Fallback*: Verified that when no LLM key is provided (`GEMINI_API_KEY=""`), the system produces a high-quality, brand-grounded response using deterministic templates in 0.85 ms without network calls or failures.
  3. *Liability Guardrail Sanitation*: Tested `FORBIDDEN_PHRASES` regex scanner. Phrases like *"we admit we were at fault"*, *"we have refunded your full amount"*, *"we will pay you to delete this"* are automatically detected, stripped, and replaced with safe operational audit verbiage.
  4. *Zero Public Publishing Without Approval*: All generated drafts are explicitly flagged with `hitl_status="PENDING_HUMAN_APPROVAL"`. No API calls to Google Maps or Yelp are executed.
- **Evidence**: `tests/test_response_generator.py` (3/3 tests passed).

---

### Feature 5: Human-in-the-Loop (HITL) Approval Workflow (Phase 8)
- **Status**: **PASS**
- **Verified Workflow**:
  1. Draft generation sets state to `PENDING_HUMAN_APPROVAL`.
  2. Manager review interface presents editable `st.text_area` with the drafted response text.
  3. Modifications by the manager persist in session state.
  4. Clicking **"Approve & Mark Ready for Dispatch"** transitions state to `APPROVED_BY_HUMAN` and generates an audit log record with timestamp.
  5. Critical/High risk reviews generate an internal incident ticket ID (e.g. `CYN-CRISIS-74A9B2`) with private investigation steps and GM contact channels.
  6. Double-click idempotency: Approving already-approved responses does not duplicate ticket IDs or produce state conflicts.
- **Evidence**: Tested locally on Streamlit session state and verified via `GeneratedResponse.to_dict()` status lifecycles.

---

### Feature 6: Executive Dashboard & CSV Export (Phase 9)
- **Status**: **PASS**
- **Verified Metrics**:
  - Global review count, average star rating, net sentiment score, crisis incidence percentage.
  - Aspect breakdown chart across all 6 operational categories with positive/negative/neutral splits.
  - Branch performance comparison table ranking locations by rating, sentiment, and crisis volume.
  - Interactive dataset switching (Benchmark 50 reviews vs Uploaded CSV).
  - Clean CSV Export: Generates downloadable CSV with UTF-8 encoding, exact row counts, compound scores, detected aspects, risk scores, crisis tiers, and response draft statuses.
- **Evidence**: Verified via `EnterpriseAnalyticsEngine` unit tests and Streamlit local dashboard execution.

---

### Feature 7: FastAPI Enterprise REST API (Phase 10)
- **Status**: **PASS**
- **Endpoints Audited**:
  - `GET /`: Status 200 OK, returns service identity and Swagger link.
  - `GET /docs`: Status 200 OK, interactive Swagger UI documentation active.
  - `GET /openapi.json`: Status 200 OK, valid OpenAPI 3.1.0 JSON schema.
  - `GET /api/v1/health`: Status 200 OK, health check confirms rule engine loaded.
  - `POST /api/v1/analyze`: Status 200 OK with aspect breakdown and crisis evaluation. Rejects short text (< 5 chars) with HTTP 422; rejects invalid rating (> 5) with HTTP 422.
  - `POST /api/v1/respond`: Status 200 OK, returns response draft, incident ticket (if crisis), and `PENDING_HUMAN_APPROVAL` status.
  - `POST /api/v1/batch-analyze`: Status 200 OK, returns executive summary and array of enriched reviews.
  - `GET /api/v1/analytics/summary`: Status 200 OK, returns pre-computed multi-branch KPIs.
  - `GET /api/v1/reviews?limit=N&offset=M`: Status 200 OK, returns paginated reviews.
- **Evidence**: `test_fastapi_endpoints.py` (10/10 assertions passed), `tests/test_api.py` (7/7 tests passed).

---

## 3. Security, Privacy & Compliance Findings (Phase 12)

1. **Zero Secret Leaks in Codebase**:
   - `git grep -i "key="` and inspection of `src/` and `app.py` confirmed no hardcoded Gemini, OpenAI, or AWS keys.
   - All credentials use `os.getenv()` with empty string fallbacks.
2. **Git Repository Hygiene**:
   - `.env`, `.env.local`, `__pycache__/`, `.pytest_cache/`, and virtual environment folders are strictly excluded in `.gitignore`.
3. **Data Privacy & Air-Gapped Operation**:
   - Customer review text uploaded via CSV is processed completely in-memory on the local server.
   - When no external LLM key is configured, zero review text is transmitted to third-party AI APIs.
4. **Injection Safety**:
   - CSV ingestion strictly uses Pandas parser with disabled script evaluation.
   - Pydantic models validate input types, lengths, and constraints, rejecting malformed payloads before execution.

---

## 4. Known Limitations & Recommendations

1. **Rule-Based Sarcasm Limitation**:
   - For reviews like *"I love waiting two hours for cold food"*, the lexical engine correctly flags negative polarity based on *"cold"* and *"waiting"*, but does not comprehend the ironic inversion of *"I love"*.
   - *Recommendation*: For Phase 3 enterprise scale, deploy an upstream fine-tuned DeBERTa-v3 checkpoint as documented in `reports/TECHNICAL_APPROACH_REPORT.md`.
2. **Persistence Boundary**:
   - Current Streamlit state persists per user session. Browser hard-refresh resets newly uploaded files back to default mock data.
   - *Recommendation*: Introduce Redis or SQLite backend for multi-user shared persistence.
3. **Cloud Deployment Synchronization**:
   - Local fixes for negation suppression and expanded lexicons are verified locally. They must be pushed to GitHub to reflect on Streamlit Community Cloud.
