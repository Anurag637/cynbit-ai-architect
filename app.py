"""
Revio 2.0: AI-Powered Review Intelligence & Crisis Detection System
Interactive Enterprise Dashboard for Cynbit Technologies
Author: Anurag Pandey (AI/ML Engineer Intern Assessment)
"""

import os
import json
import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.analyzer import AspectSentimentAnalyzer
from src.crisis_detector import CrisisDetector
from src.response_generator import ResponseGenerator
from src.analytics import EnterpriseAnalyticsEngine
from src.data_generator import load_dataset
from src.ingestion import validate_and_parse_dataframe, IngestionError
from src.config import (
    BrandPersona,
    DEFAULT_BRANCHES,
    CrisisLevel,
    BRAND_NAME,
    SUPPORT_EMAIL,
    ESCALATION_EMAIL,
    SUPPORT_PHONE,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    HUGGINGFACE_API_KEY,
    HUGGINGFACE_MODEL
)

# Page Configuration
st.set_page_config(
    page_title="Revio 2.0 | Cynbit AI Reputation Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Cynbit Brand Identity)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .cynbit-header {
        background: linear-gradient(135deg, #004D53 0%, #006067 50%, #4338CA 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 1.2rem;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 96, 103, 0.18);
    }
    
    .metric-card {
        background: white;
        padding: 1.2rem 1.4rem;
        border-radius: 1rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    .badge-critical {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        border: 1px solid #FCA5A5;
    }
    .badge-high {
        background-color: #FFEDD5;
        color: #C2410C;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        border: 1px solid #FDBA74;
    }
    .badge-low {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        border: 1px solid #6EE7B7;
    }
    
    .aspect-pill-pos {
        background-color: #ECFDF5;
        color: #047857;
        padding: 3px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
        border: 1px solid #A7F3D0;
    }
    .aspect-pill-neg {
        background-color: #FEF2F2;
        color: #B91C1C;
        padding: 3px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
        border: 1px solid #FECACA;
    }
    .aspect-pill-neu {
        background-color: #F1F5F9;
        color: #475569;
        padding: 3px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
        border: 1px solid #CBD5E1;
    }
    
    .provenance-tag {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .provenance-synthetic {
        background: #FFFBEB;
        color: #B45309;
        border: 1px solid #FCD34D;
    }
    .provenance-user {
        background: #ECFDF5;
        color: #047857;
        border: 1px solid #6EE7B7;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Core Engines (instant initialization without st.cache_resource prevents stale class definition retention in Cloud deployments)
def get_engines():
    analyzer = AspectSentimentAnalyzer()
    crisis_detector = CrisisDetector()
    response_gen = ResponseGenerator()
    analytics_engine = EnterpriseAnalyticsEngine()
    return analyzer, crisis_detector, response_gen, analytics_engine

analyzer, crisis_detector, response_gen, analytics_engine = get_engines()


# -----------------------------------------------------------------------------
# SIDEBAR: DATA INGESTION & DATASET CONTROLLER
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ Revio 2.0 Ingestion")
    st.caption("Upload multi-channel customer reviews or load the benchmark suite.")

    data_source = st.radio(
        "Select Data Source:",
        ["Synthetic Benchmark Suite (50 Reviews)", "Upload Custom CSV Dataset"],
        index=0
    )

    active_raw_reviews = []
    is_dataset_synthetic = True
    upload_meta = {}

    if data_source == "Synthetic Benchmark Suite (50 Reviews)":
        active_raw_reviews = load_dataset()
        is_dataset_synthetic = True
        st.info("ℹ️ Built-in benchmark dataset loaded (50 synthetic multi-location reviews labeled for reproducible testing).")
    else:
        uploaded_file = st.file_uploader(
            "Upload Review CSV (Expected: review_text, star_rating, branch_name):",
            type=["csv"]
        )
        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                parsed_records, meta = validate_and_parse_dataframe(uploaded_df, is_synthetic=False)
                active_raw_reviews = parsed_records
                is_dataset_synthetic = False
                upload_meta = meta
                st.success(f"✅ Ingested {meta['valid_rows_retained']} valid rows ({meta['dropped_rows']} malformed dropped).")
            except IngestionError as e:
                st.error(f"Schema Validation Error: {e}")
                st.warning("Falling back to synthetic benchmark dataset.")
                active_raw_reviews = load_dataset()
                is_dataset_synthetic = True
            except Exception as e:
                st.error(f"Failed to read file: {e}")
                active_raw_reviews = load_dataset()
                is_dataset_synthetic = True
        else:
            st.info("Please upload a CSV or download the template below.")
            sample_template = pd.DataFrame([
                {"review_text": "Food was delicious and service was super fast!", "star_rating": 5, "branch_name": "Jaipur Malviya Nagar Flagship", "date": "2026-10-15"},
                {"review_text": "Wait time was 50 minutes and waiter was rude.", "star_rating": 1, "branch_name": "Gurugram CyberCity Premier", "date": "2026-10-16"}
            ])
            st.download_button(
                "📥 Download CSV Template",
                data=sample_template.to_csv(index=False),
                file_name="revio_sample_template.csv",
                mime="text/csv"
            )
            active_raw_reviews = load_dataset()
            is_dataset_synthetic = True




# Process active dataset
@st.cache_data
def process_active_dataset(raw_data_json: str):
    raw = json.loads(raw_data_json)
    enriched = analytics_engine.process_reviews(raw)
    summary = analytics_engine.generate_executive_summary(enriched)
    return enriched, summary

enriched_reviews, executive_summary = process_active_dataset(json.dumps(active_raw_reviews))


# -----------------------------------------------------------------------------
# MAIN HEADER BANNER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="cynbit-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
            <span style="text-transform: uppercase; letter-spacing: 0.25em; font-size: 0.75rem; opacity: 0.85; font-weight: 800;">
                CYNBIT TECHNOLOGIES • AI/ML ENGINEERING ASSESSMENT
            </span>
            <h1 style="margin: 0.4rem 0 0.2rem 0; font-size: 2.2rem; font-weight: 900; letter-spacing: -0.03em;">
                Revio 2.0 Intelligence Hub
            </h1>
            <p style="margin: 0; font-size: 0.95rem; opacity: 0.9; max-width: 680px;">
                AI-Powered Multi-Location Review Intelligence, Aspect-Based Sentiment Decomposition & Crisis Interception Engine.
            </p>
        </div>
        <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); padding: 0.8rem 1.4rem; border-radius: 1rem; border: 1px solid rgba(255,255,255,0.25); text-align: right;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.15em; opacity: 0.85;">CANDIDATE SUBMISSION</div>
            <div style="font-weight: 800; font-size: 1.05rem;">Anurag Pandey</div>
            <div style="font-size: 0.75rem; opacity: 0.85;">AI Opportunity & Technical Proof of Concept</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Provenance notification
if is_dataset_synthetic:
    st.markdown("""
    <div class="provenance-tag provenance-synthetic">
        ⚠️ <b>Data Provenance: Synthetic Demonstration Dataset</b> — 50 simulated reviews covering health crises, fraud, Hinglish, negations, and service bottlenecks. Clearly labeled synthetic.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="provenance-tag provenance-user">
        📁 <b>Data Provenance: User Uploaded Dataset</b> — {len(enriched_reviews)} verified records analyzed live.
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# MAIN NAVIGATION TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Command Center",
    "⚡ Interactive AI Review Lab",
    "🏢 Multi-Location Deep-Dive",
    "📑 Strategic Architecture & Evaluation"
])


# =============================================================================
# TAB 1: EXECUTIVE COMMAND CENTER
# =============================================================================
with tab1:
    st.subheader("Enterprise Reputation & Risk Radar")
    st.caption("Empirical KPIs computed from the currently loaded review dataset.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Total Analyzed Reviews</div>
            <div style="color: #0F172A; font-size: 2rem; font-weight: 900; margin-top: 0.2rem;">{executive_summary.get('total_reviews', 0)}</div>
            <div style="color: #059669; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">Processed via Revio ABSA pipeline</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        avg_rt = executive_summary.get('avg_rating', 0.0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Network Average Rating</div>
            <div style="color: #0F172A; font-size: 2rem; font-weight: 900; margin-top: 0.2rem;">{avg_rt} ★</div>
            <div style="color: {'#059669' if avg_rt >= 4.0 else '#D97706'}; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">
                {'Above 4.0 Benchmark' if avg_rt >= 4.0 else 'Under Operational Target'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_sent = executive_summary.get('avg_sentiment', 0.0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Net Polarity Index</div>
            <div style="color: #006067; font-size: 2rem; font-weight: 900; margin-top: 0.2rem;">{avg_sent:+.2f}</div>
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">Calculated compound polarity (-1 to +1)</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        cr_cnt = executive_summary.get('crisis_count', 0)
        cr_pct = executive_summary.get('crisis_pct', 0.0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">High / Critical Crisis Reviews</div>
            <div style="color: #DC2626; font-size: 2rem; font-weight: 900; margin-top: 0.2rem;">{cr_cnt} <span style="font-size: 1rem; color: #64748B;">({cr_pct}%)</span></div>
            <div style="color: #DC2626; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">Heuristic screening triage flags</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Section
    c_left, c_right = st.columns([6, 5])

    with c_left:
        st.markdown("##### 📌 Granular Aspect Health Breakdown")
        st.caption("Net sentiment score and volume across 6 key operational aspects.")
        aspect_data = executive_summary.get("aspect_health", {})
        if aspect_data:
            aspect_names = list(aspect_data.keys())
            avg_scores = [aspect_data[a]["avg_score"] for a in aspect_names]
            mentions = [aspect_data[a]["mentions"] for a in aspect_names]

            fig_bar = px.bar(
                x=avg_scores,
                y=aspect_names,
                orientation='h',
                labels={'x': 'Net Sentiment Score (-1.0 Negative to +1.0 Positive)', 'y': 'Operational Aspect'},
                color=avg_scores,
                color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
                text=[f"{s:+.2f} ({m} mentions)" for s, m in zip(avg_scores, mentions)]
            )
            fig_bar.update_layout(
                margin=dict(l=20, r=20, t=10, b=20),
                height=340,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, width='stretch')

    with c_right:
        st.markdown("##### 🌐 Sentiment & Platform Distribution")
        st.caption("Distribution of emotional polarity across all uploaded records.")
        sent_dist = executive_summary.get("sentiment_distribution", {})
        if sent_dist:
            fig_pie = px.pie(
                names=list(sent_dist.keys()),
                values=list(sent_dist.values()),
                hole=0.45,
                color=list(sent_dist.keys()),
                color_discrete_map={
                    "POSITIVE": "#10B981",
                    "NEGATIVE": "#EF4444",
                    "MIXED": "#F59E0B",
                    "NEUTRAL": "#64748B"
                }
            )
            fig_pie.update_layout(
                margin=dict(l=20, r=20, t=10, b=20),
                height=340
            )
            st.plotly_chart(fig_pie, width='stretch')

    st.markdown("---")
    st.markdown("##### 🏆 Multi-Branch Comparative Performance Table")
    st.caption("Ranked by average star rating, net aspect sentiment, and crisis incidence rate.")
    
    branch_rows = executive_summary.get("branch_rankings", [])
    if branch_rows:
        branch_df = pd.DataFrame(branch_rows)
        branch_df.rename(columns={
            "branch_name": "Location Name",
            "city": "City",
            "total_reviews": "Total Reviews",
            "avg_rating": "Avg Star Rating",
            "avg_sentiment": "Net Sentiment Score",
            "crisis_count": "Crisis Count",
            "crisis_rate_pct": "Crisis Rate (%)"
        }, inplace=True)
        st.dataframe(
            branch_df,
            column_config={
                "Avg Star Rating": st.column_config.NumberColumn(format="%.2f ★"),
                "Net Sentiment Score": st.column_config.NumberColumn(format="%+.2f"),
                "Crisis Rate (%)": st.column_config.NumberColumn(format="%.1f%%")
            },
            hide_index=True,
            width='stretch'
        )

    # Export Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📥 Export Analyzed Dataset")
    st.caption("Download the complete dataset enriched with ABSA tags, crisis classifications, and threat vectors.")

    export_df = pd.DataFrame(enriched_reviews)
    # Flatten aspects for clean CSV representation
    export_df["detected_aspects_list"] = export_df["aspects"].apply(
        lambda asps: ", ".join([f"{a['category']} ({a['sentiment']})" for a in asps]) if asps else "None"
    )
    cols_to_export = [
        "id", "date", "customer_name", "branch_name", "platform",
        "star_rating", "review_text", "overall_sentiment", "compound_score",
        "detected_aspects_list", "risk_score", "crisis_level", "is_crisis", "primary_emotion"
    ]
    cols_present = [c for c in cols_to_export if c in export_df.columns]
    csv_bytes = export_df[cols_present].to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Analyzed Results (CSV)",
        data=csv_bytes,
        file_name=f"revio_analyzed_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


# =============================================================================
# TAB 2: INTERACTIVE AI REVIEW LAB (PLAYGROUND)
# =============================================================================
with tab2:
    st.subheader("Interactive AI Review Analysis & Human-in-the-Loop Studio")
    st.caption("Test the Aspect-Based Sentiment, Crisis Scoring, and Persona-Calibrated Response pipeline in real time.")

    # Sample Presets
    presets = {
        "Custom Input": {
            "text": "",
            "rating": 3,
            "name": "Anurag Pandey",
            "branch": "Jaipur Malviya Nagar Flagship"
        },
        "🚨 Critical Crisis: Severe Food Poisoning & Hospitalization": {
            "text": "EMERGENCY: Three of us had dinner here last night and woke up with severe food poisoning and vomiting. My brother is admitted to the hospital right now. When I called the store manager, he was completely rude and dismissive. We are reporting this to the food safety authority and filing a police complaint!",
            "rating": 1,
            "name": "Rohan Malhotra",
            "branch": "Jaipur Malviya Nagar Flagship"
        },
        "⚖️ High Risk: Credit Card Fraud & Unauthorized Charge": {
            "text": "Absolute fraud! Checked my credit card statement today and discovered an unauthorized charge of Rs. 4,500 that was never on my receipt. The cashier refused to give me a printed invoice. If this is not refunded in 24 hours, my lawyer is taking this to consumer court.",
            "rating": 1,
            "name": "Meera Sen",
            "branch": "Jaipur Pratap Nagar Tech Hub"
        },
        "🗣️ Hinglish Complaint: Khana Bakwas & Battameez Staff": {
            "text": "Khana ekdum bakwas tha aur staff bohot battameez tha. Table par ganda tissue pada tha. Dhoka hua hamare sath.",
            "rating": 1,
            "name": "Amit Sharma",
            "branch": "Jaipur Malviya Nagar Flagship"
        },
        "⏳ Mixed: Delicious Food but 55-Min Wait Time": {
            "text": "The truffle pasta and mocktails were utterly delicious and freshly prepared! But we had to wait 55 minutes for our table and another 40 minutes for the main course. The floor supervisor was slow and distracted.",
            "rating": 3,
            "name": "Siddharth Joshi",
            "branch": "Gurugram CyberCity Premier"
        },
        "⭐ 5-Star Delight: Outstanding Service & Impeccable Hygiene": {
            "text": "Hands down the best experience in the city! Staff greeted us warmly, our food arrived within 10 minutes hot and bursting with flavor. Pristine cleanliness and courteous team. 10/10!",
            "rating": 5,
            "name": "Aditi Roy",
            "branch": "Bengaluru Indiranagar Center"
        }
    }

    selected_preset = st.selectbox(
        "Choose an Enterprise Test Case or write custom review text:",
        list(presets.keys())
    )

    preset_data = presets[selected_preset]

    p_col1, p_col2 = st.columns([7, 5])

    with p_col1:
        input_text = st.text_area(
            "Customer Review Text:",
            value=preset_data["text"] if preset_data["text"] else "The food was delicious, but the service was remarkably slow and the waiter was rude when we asked for the bill.",
            height=130
        )

    with p_col2:
        in_rating = st.slider("Customer Star Rating:", min_value=1, max_value=5, value=preset_data["rating"])
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            in_name = st.text_input("Customer Name:", value=preset_data["name"])
        with c_sub2:
            in_branch = st.selectbox(
                "Branch Location:",
                [b["name"] for b in DEFAULT_BRANCHES],
                index=0
            )

    c_opt1, c_opt2 = st.columns(2)
    with c_opt1:
        selected_persona = st.selectbox(
            "Brand Response Persona:",
            [p.value for p in BrandPersona],
            index=0
        )
    with c_opt2:
        has_env_key = bool(HUGGINGFACE_API_KEY or GEMINI_API_KEY or OPENAI_API_KEY)
        use_llm_opt = st.checkbox(
            "Enable Optional LLM Generation (Hugging Face Free / Gemini)",
            value=has_env_key,
            help="If unchecked or if no key is provided, Revio uses safe offline deterministic policy templates."
        )
        if has_env_key:
            st.caption("🟢 **API Key Active:** Connected via environment / Streamlit Secrets.")
        else:
            st.caption("ℹ️ **Offline Mode:** No API Key detected. Using safe deterministic policy templates (100% Free / Offline).")

    user_hf_key = None
    user_gemini_key = None
    selected_hf_model = HUGGINGFACE_MODEL

    if use_llm_opt:
        provider_mode = st.radio(
            "Select AI Provider:",
            ["✨ Google Gemini (100% Free Forever, No Credit Card Required)", "🤗 Hugging Face Serverless"],
            index=0,
            horizontal=True
        )
        if "Gemini" in provider_mode:
            user_gemini_key = st.text_input(
                "🔑 Paste Your Free Google Gemini API Key (starts with AIzaSy...):",
                type="password",
                placeholder="Paste your free Gemini key: AIzaSyxxxxxxxxxxxxxxxxxxxxx",
                help="Get a 100% free Gemini API key with 1,500 requests/day at https://aistudio.google.com/app/apikey (Zero cost, no credit card required)."
            )
            st.caption("🚀 **Recommended:** Google Gemini gives 1,500 requests/day for 100% free forever without payment credits. [Get your free key in 30 seconds at Google AI Studio](https://aistudio.google.com/app/apikey).")
        else:
            llm_col1, llm_col2 = st.columns([7, 5])
            with llm_col1:
                user_hf_key = st.text_input(
                    "🤗 Paste Your Hugging Face Token (starts with hf_...):",
                    type="password",
                    placeholder="Paste your active hf_xxxxxxxx token here...",
                    help="Hugging Face User Access Token. Note: HF serverless router requires pre-paid credits on some accounts."
                )
            with llm_col2:
                selected_hf_model = st.selectbox(
                    "Free Open Model:",
                    [
                        "meta-llama/Llama-3.1-8B-Instruct",
                        "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                        "Qwen/Qwen2.5-Coder-7B-Instruct",
                        "google/gemma-3-4b-it"
                    ],
                    index=0,
                    help="Meta Llama 3.1 8B & DeepSeek R1 are the top verified free models hosted on Hugging Face Serverless Router."
                )
            st.caption("ℹ️ *Note: If Hugging Face returns 'No remaining credits', switch to the Google Gemini option above (100% free forever without credits).*")

    if st.button("🚀 Analyze & Generate Governed Response", type="primary", width='stretch'):
        with st.spinner("Decomposing aspects, evaluating risk screening, and applying guardrails..."):
            analysis = analyzer.analyze(input_text, in_rating)
            crisis = crisis_detector.evaluate(input_text, in_rating)
            persona_enum = BrandPersona(selected_persona)
            try:
                resp = response_gen.generate(
                    customer_name=in_name,
                    branch_name=in_branch,
                    analysis=analysis,
                    crisis=crisis,
                    persona=persona_enum,
                    use_llm_if_available=use_llm_opt,
                    custom_gemini_key=user_gemini_key if user_gemini_key else None,
                    custom_hf_key=user_hf_key if user_hf_key else None,
                    hf_model=selected_hf_model
                )
            except TypeError:
                # Defensive fallback: if Streamlit Cloud worker kept a stale engine instance in memory
                fresh_gen = ResponseGenerator()
                resp = fresh_gen.generate(
                    customer_name=in_name,
                    branch_name=in_branch,
                    analysis=analysis,
                    crisis=crisis,
                    persona=persona_enum,
                    use_llm_if_available=use_llm_opt,
                    custom_gemini_key=user_gemini_key if user_gemini_key else None,
                    custom_hf_key=user_hf_key if user_hf_key else None,
                    hf_model=selected_hf_model
                )

            st.markdown("---")

            res_left, res_right = st.columns([6, 6])

            with res_left:
                st.markdown("#### 1. Cognitive NLP Diagnostics")

                # Crisis badge
                badge_class = "badge-low"
                if crisis.crisis_level == CrisisLevel.CRITICAL:
                    badge_class = "badge-critical"
                elif crisis.crisis_level in [CrisisLevel.HIGH, CrisisLevel.MEDIUM]:
                    badge_class = "badge-high"

                st.markdown(f"""
                <div style="display: flex; gap: 0.8rem; align-items: center; margin-bottom: 0.8rem; flex-wrap: wrap;">
                    <span style="font-weight: 700; font-size: 0.9rem;">Overall Sentiment:</span>
                    <span style="background: #E2E8F0; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 0.8rem;">
                        {analysis.overall_sentiment.value} ({analysis.compound_score:+.2f})
                    </span>
                    <span style="font-weight: 700; font-size: 0.9rem; margin-left: 0.5rem;">Risk Tier:</span>
                    <span class="{badge_class}">
                        {crisis.crisis_level.value} ({crisis.risk_score}/100)
                    </span>
                </div>
                """, unsafe_allow_html=True)

                st.caption("ℹ️ *Note: Risk scores are heuristic screening estimates for queue triage, not calibrated probabilities.*")

                st.markdown(f"**Primary Emotion Detected:** `{analysis.primary_emotion}`")
                st.markdown(f"**Root-Cause Driver:** `{analysis.root_cause}`")
                st.markdown(f"**Threat Vectors Identified:** {', '.join(crisis.threat_vectors)}")
                
                st.markdown("**Matched Evidence & Screening Reasons:**")
                for reason in crisis.flag_reasons:
                    st.markdown(f"- 🔍 {reason}")

                st.markdown(f"**Escalation Target & SLA:** `{crisis.sla_window}` ➔ *{crisis.escalation_target}*")

                st.markdown("<br><b>Granular Aspect Extraction (ABSA):</b>", unsafe_allow_html=True)
                if analysis.detected_aspects:
                    for asp in analysis.detected_aspects:
                        pill_class = "aspect-pill-pos" if asp.sentiment.value == "POSITIVE" else ("aspect-pill-neg" if asp.sentiment.value == "NEGATIVE" else "aspect-pill-neu")
                        st.markdown(f"""
                        <div style="background: white; border: 1px solid #E2E8F0; padding: 8px 12px; border-radius: 8px; margin-bottom: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong>{asp.category}</strong>
                                <span class="{pill_class}">{asp.sentiment.value} ({asp.score:+.2f})</span>
                            </div>
                            <div style="font-size: 0.8rem; color: #475569; margin-top: 4px;">
                                Clause context: <em>"{asp.context_snippet}"</em>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No specific operational aspects matched the standard taxonomy (General feedback).")

            with res_right:
                st.markdown("#### 2. Governed Response & Human Approval")

                hitl_badge = "badge-high" if "REQUIRES" in resp.hitl_status else "badge-low"
                ticket_str = f"#{resp.ticket_id} (Simulated)" if resp.ticket_id else "None"

                st.markdown(f"""
                <div style="background: white; border: 1px solid #CBD5E1; border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; flex-wrap: wrap;">
                        <div>
                            <span style="font-size: 0.75rem; text-transform: uppercase; font-weight: bold; color: #64748B;">Routing Workflow:</span>
                            <span class="{hitl_badge}">{resp.hitl_status}</span>
                        </div>
                        <div>
                            <span style="font-size: 0.75rem; color: #64748B;">Internal Case Ref:</span> <code>{ticket_str}</code>
                        </div>
                    </div>
                    <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.4rem;">
                        <strong>Draft Source:</strong> <em>{resp.generation_source}</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if getattr(resp, "llm_error", None):
                    err_text = str(resp.llm_error)
                    if "Gemini" in err_text:
                        tip = "💡 **How to resolve:** Ensure your Google Gemini key (starts with `AIzaSy...`) is active at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey), then click **'🚀 Analyze & Generate Governed Response'**."
                    elif "credits" in err_text.lower():
                        tip = "💡 **How to resolve:** Hugging Face serverless router requires pre-paid credits. Please switch to the **Google Gemini** option above for 100% free generation without credits!"
                    else:
                        tip = "💡 **How to resolve:** Check that your API key is correctly pasted in the box above, then click **'🚀 Analyze & Generate Governed Response'**."
                    st.warning(f"⚠️ **LLM Fallback Activated:** {resp.llm_error}\n\n{tip}")
                elif any(k in resp.generation_source for k in ["Hugging Face", "Gemini", "OpenAI"]):
                    st.success(f"✨ **Live AI Generation Active:** Drafted directly via `{resp.generation_source}`.")

                # Editable response area for Human-in-the-Loop approval
                st.markdown("<br><b>Draft Response (Human Review & Edit):</b>", unsafe_allow_html=True)
                approved_response_text = st.text_area(
                    "You may review or edit the drafted reply before approving:",
                    value=resp.response_text,
                    height=130,
                    key="hitl_draft_area"
                )

                # Guardrail check
                st.markdown("<b>🛡️ Compliance & Anti-Hallucination Guardrails:</b>", unsafe_allow_html=True)
                if resp.guardrail_passed:
                    st.success("✅ **Guardrails Passed:** Zero unauthorized refund promises, fake compensation, or legal liability admissions detected.")
                else:
                    st.warning("⚠️ **Guardrail Sanitized:** Unverified claims or liability terms were stripped and normalized.")
                    for w in resp.guardrail_warnings:
                        st.caption(f"- {w}")

                st.markdown("<b>Internal Workflow Actions:</b>", unsafe_allow_html=True)
                for step in resp.actionable_steps:
                    st.markdown(f"- ⚡ {step}")

                # Human sign-off action buttons
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✅ Approve Response (Sign-off)", width='stretch'):
                        st.success("Response approved by Human Reviewer! Status: APPROVED_FOR_DISPATCH (Simulated)")
                with col_btn2:
                    if st.button("🚀 Simulate Public Post (Google Maps / Yelp)", width='stretch'):
                        st.toast("Simulated API dispatch: Response pushed to mock connector! (No real external requests sent)", icon="📢")


# =============================================================================
# TAB 3: MULTI-LOCATION DEEP-DIVE
# =============================================================================
with tab3:
    st.subheader("Multi-Branch Operational Quality Feed")
    st.caption("Filter and audit location-specific review streams and crisis escalations.")

    b_filter_col1, b_filter_col2 = st.columns([6, 6])
    with b_filter_col1:
        branch_filter = st.selectbox(
            "Filter by Branch:",
            ["All Locations"] + list(set([r["branch_name"] for r in enriched_reviews]))
        )
    with b_filter_col2:
        sentiment_filter = st.selectbox(
            "Filter by Sentiment / Risk:",
            ["All Reviews", "Crisis Only (High & Critical)", "Negative Sentiment", "Positive Sentiment", "Mixed Sentiment"]
        )

    # Filter records
    filtered = enriched_reviews
    if branch_filter != "All Locations":
        filtered = [r for r in filtered if r["branch_name"] == branch_filter]

    if sentiment_filter == "Crisis Only (High & Critical)":
        filtered = [r for r in filtered if r["is_crisis"]]
    elif sentiment_filter == "Negative Sentiment":
        filtered = [r for r in filtered if r["overall_sentiment"] == "NEGATIVE"]
    elif sentiment_filter == "Positive Sentiment":
        filtered = [r for r in filtered if r["overall_sentiment"] == "POSITIVE"]
    elif sentiment_filter == "Mixed Sentiment":
        filtered = [r for r in filtered if r["overall_sentiment"] == "MIXED"]

    st.markdown(f"**Displaying {len(filtered)} reviews matching criteria:**")

    for item in filtered[:15]:
        with st.expander(f"{item.get('customer_name', 'Guest')} ({item.get('star_rating', 3)}★) — {item.get('branch_name', 'Branch')} | Platform: {item.get('platform', 'Direct')}"):
            st.markdown(f"**Customer Review:** *\"{item.get('review_text', '')}\"*")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Sentiment:** `{item.get('overall_sentiment', 'NEUTRAL')}` ({item.get('compound_score', 0.0):+.2f})")
            with c2:
                st.markdown(f"**Screening Risk:** `{item.get('risk_score', 0)}/100` ({item.get('crisis_level', 'LOW')})")
            with c3:
                st.markdown(f"**Primary Emotion:** `{item.get('primary_emotion', 'Neutral')}`")

            if item.get("aspects"):
                st.markdown("**Extracted Aspects:**")
                for a in item["aspects"]:
                    st.markdown(f"- **{a['category']}**: `{a['sentiment']}` ({a['score']:+.2f}) | Keywords: *{', '.join(a['keywords'])}*")


# =============================================================================
# TAB 4: STRATEGIC ARCHITECTURE & REPORTS
# =============================================================================
with tab4:
    st.subheader("Architectural Blueprints, Evaluation & Deliverables")
    st.caption("Complete technical assessment documentation, empirical metrics, and deliverables for Cynbit Leadership.")

    rep_col1, rep_col2, rep_col3 = st.columns(3)
    with rep_col1:
        st.markdown("""
        #### 📄 AI Opportunity Report
        - Business problem & Cynbit company context
        - 4 AI opportunities compared
        - Revio 2.0 selection rationale
        - Expected business value & KPIs
        """)
        try:
            with open("reports/AI_OPPORTUNITY_REPORT.md", "r", encoding="utf-8") as f:
                rep1_text = f.read()
            st.download_button(
                label="📥 Download AI Opportunity Report",
                data=rep1_text,
                file_name="Cynbit_AI_Opportunity_Report_Anurag_Pandey.md",
                mime="text/markdown",
                width='stretch'
            )
        except Exception as e:
            st.error(f"Report not found: {e}")

    with rep_col2:
        st.markdown("""
        #### 🛠️ Technical Approach Report
        - Compound AI System Architecture
        - ABSA & Crisis Screening Design
        - Grounded response generation & fallback
        - Deployment & Security
        """)
        try:
            with open("reports/TECHNICAL_APPROACH_REPORT.md", "r", encoding="utf-8") as f:
                rep2_text = f.read()
            st.download_button(
                label="📥 Download Technical Approach Report",
                data=rep2_text,
                file_name="Cynbit_Technical_Approach_Report_Anurag_Pandey.md",
                mime="text/markdown",
                width='stretch'
            )
        except Exception as e:
            st.error(f"Report not found: {e}")

    with rep_col3:
        st.markdown("""
        #### 📊 Empirical Benchmark Results
        - Labeled test dataset evaluation
        - Real Aspect Precision, Recall, Macro-F1
        - Crisis Precision, Recall, Critical FN
        - Real measured processing latency
        """)
        try:
            with open("reports/evaluation_results.json", "r", encoding="utf-8") as f:
                eval_json = f.read()
            st.download_button(
                label="📥 Download Evaluation Results (JSON)",
                data=eval_json,
                file_name="revio_empirical_evaluation_results.json",
                mime="application/json",
                width='stretch'
            )
        except Exception:
            st.info("Evaluation results will appear after running evaluate.py")

    st.markdown("---")
    st.markdown("### 📊 Actual Measured Evaluation Metrics (Reproducible Benchmark)")
    try:
        with open("reports/evaluation_results.json", "r", encoding="utf-8") as f:
            eval_data = json.load(f)
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Aspect Macro-F1", f"{eval_data['aspect_metrics']['macro_f1']*100:.1f}%")
        with m_col2:
            st.metric("Crisis Recall", f"{eval_data['crisis_metrics']['recall']*100:.1f}%")
        with m_col3:
            st.metric("Critical Safety Misses", f"{eval_data['crisis_metrics']['critical_safety_false_negatives']} / {eval_data['crisis_metrics']['critical_safety_total']}")
        with m_col4:
            st.metric("Mean Latency", f"{eval_data['latency_profile_ms']['mean_ms']:.2f} ms")
        
        st.caption(f"Evaluated on {eval_data['dataset_size']} ground truth reviews covering positive, negative, mixed, negation, Hinglish, and safety crises. Latency methodology: {eval_data['latency_profile_ms']['methodology']}")
    except Exception as e:
        st.info("Run `python evaluate.py` to populate live metrics.")

    st.markdown("---")
    st.markdown("### 🏛️ Revio 2.0 System Component Architecture")
    st.markdown("""
| Component | Implementation Method | Purpose & Rationale | Status in Proof of Concept |
| :--- | :--- | :--- | :--- |
| **Review Ingestion** | Pandas + Schema Validator | CSV upload with validation (`review_text`, `star_rating`, `branch`) | **Fully Implemented** |
| **Aspect-Based Sentiment** | Rule-Based Lexical ABSA | 6 operational categories, contrastive clauses, negation inversion | **Fully Implemented** |
| **Crisis & Urgency Triage** | Weighted Threat Clustering | Health/safety, legal, fraud, abuse, PR screening index (0-100) | **Fully Implemented** |
| **Response Generation** | Grounded Policy Fallback + Optional LLM | Deterministic policy templates + optional Gemini/OpenAI if configured | **Fully Implemented** |
| **Guardrails & Compliance** | Strict Regex Inspection | Prevents unverified refunds, promises, and legal liability admissions | **Fully Implemented** |
| **Human-in-the-Loop** | Streamlit Approval Interface | Enforces human review & edit before public reply sign-off | **Fully Implemented** |
| **External Publishing** | Mock API Connector | Google Maps / Yelp public reply simulation | **Simulated (Clearly Labeled)** |
| **Incident Case Management**| Deterministic ID Generator | Reference tracking for internal manager routing (`#SIM-XXXX`) | **Simulated (Clearly Labeled)** |
    """)

    st.markdown("""
```
                   +-------------------------------------------------------------+
                   |  External Review Sources (Google Maps, Yelp, Zomato, Social) |
                   +-------------------------------------------------------------+
                                                  │
                                                  ▼
                   +-------------------------------------------------------------+
                   |          Revio Ingestion Gateway & Schema Validation        |
                   |       (CSV / JSON, Column Normalization, Row Filtering)     |
                   +-------------------------------------------------------------+
                                                  │
                                                  ▼
              ┌───────────────────────────────────┴───────────────────────────────────┐
              ▼                                                                       ▼
+------------------------------------+                             +------------------------------------+
| Aspect-Based Sentiment Engine      |                             | Crisis & Risk Screening Triage     |
| (6 Categories, Contrastive Clauses,|                             | (Health & Safety, Legal, Fraud,    |
| Negation Inversion, Polarity Score)|                             | Harassment Screening Index 0-100%) |
+------------------------------------+                             +------------------------------------+
              │                                                                       │
              └───────────────────────────────────┬───────────────────────────────────┘
                                                  │
                                                  ▼
                   +-------------------------------------------------------------+
                   |         Persona-Calibrated Response Synthesizer            |
                   |  (Policy Persona Engine + Safe Offline Fallback + LLM Hook) |
                   +-------------------------------------------------------------+
                                                  │
                                                  ▼
                   +-------------------------------------------------------------+
                   |          Compliance & Anti-Hallucination Guardrails         |
                   |   (Intercepts Unverified Refunds & Legal Liability Claims)  |
                   +-------------------------------------------------------------+
                                                  │
                                                  ▼
                   +-------------------------------------------------------------+
                   |               Human-in-the-Loop (HITL) Queue                |
                   |   (Mandatory Review & Edit Before Public Reply Sign-off)    |
                   +-------------------------------------------------------------+
                                                  │
                                                  ▼
                   +-------------------------------------------------------------+
                   |      Simulated Dispatch to Review Channels (Mock Connector) |
                   +-------------------------------------------------------------+
```
    """)
