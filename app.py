"""
Revio 2.0: Autonomous Multi-Agent Reputation & Crisis Intelligence Engine
Interactive Enterprise Dashboard for Cynbit Technologies
"""

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
from src.config import BrandPersona, DEFAULT_BRANCHES, CrisisLevel

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .cynbit-header {
        background: linear-gradient(135deg, #004D53 0%, #006067 50%, #7C3AED 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 1.5rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 96, 103, 0.18);
    }
    
    .metric-card {
        background: white;
        padding: 1.3rem 1.5rem;
        border-radius: 1.2rem;
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
        padding: 2px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
        border: 1px solid #A7F3D0;
    }
    .aspect-pill-neg {
        background-color: #FEF2F2;
        color: #B91C1C;
        padding: 2px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
        border: 1px solid #FECACA;
    }
    
    .ticket-badge {
        font-family: monospace;
        font-weight: bold;
        background: #F1F5F9;
        color: #006067;
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Core Engines
@st.cache_resource
def get_engines():
    analyzer = AspectSentimentAnalyzer()
    crisis_detector = CrisisDetector()
    response_gen = ResponseGenerator()
    analytics_engine = EnterpriseAnalyticsEngine()
    return analyzer, crisis_detector, response_gen, analytics_engine

analyzer, crisis_detector, response_gen, analytics_engine = get_engines()

# Load and process dataset
@st.cache_data
def get_processed_data():
    raw = load_dataset()
    enriched = analytics_engine.process_reviews(raw)
    summary = analytics_engine.generate_executive_summary(enriched)
    return enriched, summary

enriched_reviews, executive_summary = get_processed_data()

# Header Banner
st.markdown("""
<div class="cynbit-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
            <span style="text-transform: uppercase; letter-spacing: 0.25em; font-size: 0.75rem; opacity: 0.85; font-weight: 800;">
                CYNBIT TECHNOLOGIES • ENTERPRISE SAAS SUITE
            </span>
            <h1 style="margin: 0.4rem 0 0.2rem 0; font-size: 2.3rem; font-weight: 900; letter-spacing: -0.03em;">
                Revio 2.0 Intelligence Hub
            </h1>
            <p style="margin: 0; font-size: 0.95rem; opacity: 0.9; max-width: 650px;">
                Autonomous Multi-Agent Reputation Defense, Aspect-Based Sentiment Analysis & Crisis Escalation Engine.
            </p>
        </div>
        <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); padding: 0.8rem 1.4rem; border-radius: 1rem; border: 1px solid rgba(255,255,255,0.25); text-align: right;">
            <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.15em; opacity: 0.8;">CANDIDATE SUBMISSION</div>
            <div style="font-weight: 800; font-size: 1.05rem;">Anurag Pandey</div>
            <div style="font-size: 0.75rem; opacity: 0.85;">AI/ML Engineer Intern Assessment</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Command Center",
    "⚡ Interactive AI Review Lab",
    "🏢 Multi-Location Deep-Dive",
    "📑 Strategic Architecture & Reports"
])


# =============================================================================
# TAB 1: EXECUTIVE COMMAND CENTER
# =============================================================================
with tab1:
    st.subheader("Enterprise Health & Reputation Radar")
    st.caption("Live aggregate metrics across all registered regional branches and external review platforms.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Total Monitored Reviews</div>
            <div style="color: #0F172A; font-size: 2rem; font-weight: 900; margin-top: 0.2rem;">{executive_summary.get('total_reviews', 0)}</div>
            <div style="color: #059669; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">↑ Real-time sync across 4 channels</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        avg_rt = executive_summary.get('avg_rating', 0.0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Network Average Rating</div>
            <div style="color: #0F172A; font-size: 2rem; font-weight: 900; margin-top: 0.2rem;">{avg_rt} ★</div>
            <div style="color: {'#059669' if avg_rt >= 4.0 else '#D97706'}; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">
                Target Benchmark: 4.50 ★
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_sent = executive_summary.get('avg_sentiment', 0.0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Polarity Sentiment Index</div>
            <div style="color: #006067; font-size: 2rem; font-weight: 900; margin-top: 0.2rem;">{avg_sent:+.2f}</div>
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">Scale: -1.0 (Worst) to +1.0 (Best)</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        cr_cnt = executive_summary.get('crisis_count', 0)
        cr_pct = executive_summary.get('crisis_pct', 0.0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Crisis Reviews Intercepted</div>
            <div style="color: #DC2626; font-size: 2rem; font-weight: 900; margin-top: 0.2rem;">{cr_cnt} <span style="font-size: 1rem; color: #64748B;">({cr_pct}%)</span></div>
            <div style="color: #DC2626; font-size: 0.75rem; font-weight: 600; margin-top: 0.2rem;">SLA window: &lt; 15 mins containment</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Section
    c_left, c_right = st.columns([6, 5])

    with c_left:
        st.markdown("##### 📌 Granular Aspect Health Radar")
        st.caption("Net sentiment health scores across key operational facets.")
        aspect_data = executive_summary.get("aspect_health", {})
        if aspect_data:
            aspect_names = list(aspect_data.keys())
            avg_scores = [aspect_data[a]["avg_score"] for a in aspect_names]
            mentions = [aspect_data[a]["mentions"] for a in aspect_names]

            fig_bar = px.bar(
                x=avg_scores,
                y=aspect_names,
                orientation='h',
                labels={'x': 'Net Sentiment Score (-1.0 to +1.0)', 'y': 'Operational Aspect'},
                color=avg_scores,
                color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
                text=[f"{s:+.2f} ({m} mentions)" for s, m in zip(avg_scores, mentions)]
            )
            fig_bar.update_layout(
                margin=dict(l=20, r=20, t=10, b=20),
                height=340,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with c_right:
        st.markdown("##### 🌐 Channel & Sentiment Distribution")
        st.caption("Review volume broken down by platform and emotional polarity.")
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
            st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 🏆 Multi-Branch Comparative Performance Table")
    st.caption("Ranked by average rating and net aspect score to uncover operational bottlenecks.")
    
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
            use_container_width=True
        )


# =============================================================================
# TAB 2: INTERACTIVE AI REVIEW LAB (PLAYGROUND)
# =============================================================================
with tab2:
    st.subheader("Interactive AI Review Analysis & Response Synthesizer")
    st.caption("Test the Aspect-Based Sentiment, Crisis Scoring, and Persona-Calibrated Response pipeline in real time.")

    # Sample Preset Selectors
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
        "⏳ Mixed: Delicious Food but Unbearable 55-Min Waiting Time": {
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
        "Choose an Enterprise Test Case or write your own custom review:",
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

    selected_persona = st.selectbox(
        "Select Brand Response Persona (Multi-Agent Alignment):",
        [p.value for p in BrandPersona],
        index=0
    )

    if st.button("🚀 Analyze & Generate Autonomous Agent Response", type="primary", use_container_width=True):
        with st.spinner("Executing Aspect Decomposition, Risk Calculation & Guardrail Filtering..."):
            analysis = analyzer.analyze(input_text, in_rating)
            crisis = crisis_detector.evaluate(input_text, in_rating)
            persona_enum = BrandPersona(selected_persona)
            resp = response_gen.generate(
                customer_name=in_name,
                branch_name=in_branch,
                analysis=analysis,
                crisis=crisis,
                persona=persona_enum
            )

            st.markdown("---")

            # Result Section
            res_left, res_right = st.columns([6, 6])

            with res_left:
                st.markdown("#### 1. Cognitive NLP Diagnostics")

                # Top Badges
                badge_class = "badge-low"
                if crisis.crisis_level == CrisisLevel.CRITICAL:
                    badge_class = "badge-critical"
                elif crisis.crisis_level in [CrisisLevel.HIGH, CrisisLevel.MEDIUM]:
                    badge_class = "badge-high"

                st.markdown(f"""
                <div style="display: flex; gap: 0.8rem; align-items: center; margin-bottom: 1rem; flex-wrap: wrap;">
                    <span style="font-weight: 700; font-size: 0.9rem;">Overall Sentiment:</span>
                    <span style="background: #E2E8F0; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 0.8rem;">
                        {analysis.overall_sentiment.value} ({analysis.compound_score:+.2f})
                    </span>
                    <span style="font-weight: 700; font-size: 0.9rem; margin-left: 0.5rem;">Crisis Tier:</span>
                    <span class="{badge_class}">
                        {crisis.crisis_level.value} ({crisis.risk_score}%)
                    </span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"**Primary Emotion Detected:** `{analysis.primary_emotion}`")
                st.markdown(f"**Root-Cause Driver:** `{analysis.root_cause}`")
                st.markdown(f"**Threat Vectors Identified:** {', '.join(crisis.threat_vectors)}")
                st.markdown(f"**Escalation SLA Target:** `{crisis.sla_window}` ➔ *{crisis.escalation_target}*")

                st.markdown("<br><b>Granular Aspect Extraction (ABSA):</b>", unsafe_allow_html=True)
                if analysis.detected_aspects:
                    for asp in analysis.detected_aspects:
                        pill_class = "aspect-pill-pos" if asp.sentiment.value == "POSITIVE" else "aspect-pill-neg"
                        st.markdown(f"""
                        <div style="background: white; border: 1px solid #E2E8F0; padding: 8px 12px; border-radius: 8px; margin-bottom: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong>{asp.category}</strong>
                                <span class="{pill_class}">{asp.sentiment.value} ({asp.score:+.2f})</span>
                            </div>
                            <div style="font-size: 0.8rem; color: #475569; margin-top: 4px;">
                                <em>"{asp.context_snippet}"</em>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No specific operational aspects matched standard taxonomy (General feedback).")

            with res_right:
                st.markdown("#### 2. Agentic Context-Aware Response")

                hitl_badge = "badge-low" if resp.hitl_status == "AUTO_APPROVED" else "badge-high"
                ticket_str = f"<span class='ticket-badge'>#{resp.ticket_id}</span>" if resp.ticket_id else "None"

                st.markdown(f"""
                <div style="background: white; border: 1px solid #CBD5E1; border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                        <div>
                            <span style="font-size: 0.75rem; text-transform: uppercase; font-weight: bold; color: #64748B;">Routing Workflow:</span>
                            <span class="{hitl_badge}">{resp.hitl_status}</span>
                        </div>
                        <div>
                            <span style="font-size: 0.75rem; color: #64748B;">Ticket ID:</span> {ticket_str}
                        </div>
                    </div>
                    <div style="background: #F8FAFC; border-left: 4px solid #006067; padding: 12px; border-radius: 6px; font-size: 0.9rem; line-height: 1.5; color: #1E293B;">
                        {resp.response_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br><b>🛡️ Compliance & Safety Guardrails:</b>", unsafe_allow_html=True)
                if resp.guardrail_passed:
                    st.success("✅ **Guardrail Passed:** Zero legal liabilities, unauthorized concessions, or admitted fault phrases detected.")
                else:
                    st.warning("⚠️ **Guardrail Triggered:** Liability clause was sanitized and replaced with safe formal language.")

                st.markdown("<b>Next Actionable Operational Steps:</b>", unsafe_allow_html=True)
                for step in resp.actionable_steps:
                    st.markdown(f"- ⚡ {step}")

                if st.button("Simulate 1-Click Multi-Platform Publish (Google Maps / Yelp)"):
                    st.toast("Success: Response pushed to public platform via Revio API Connector!", icon="🚀")


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
            ["All Locations"] + [b["name"] for b in DEFAULT_BRANCHES]
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
        with st.expander(f"{item['customer_name']} ({item['star_rating']}★) — {item['branch_name']} | Platform: {item['platform']}"):
            st.markdown(f"**Customer Review:** *\"{item['review_text']}\"*")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Sentiment:** `{item['overall_sentiment']}` ({item['compound_score']:+.2f})")
            with c2:
                st.markdown(f"**Crisis Risk Score:** `{item['risk_score']}%` ({item['crisis_level']})")
            with c3:
                st.markdown(f"**Primary Emotion:** `{item['primary_emotion']}`")

            if item["aspects"]:
                st.markdown("**Extracted Aspects:**")
                for a in item["aspects"]:
                    st.markdown(f"- **{a['category']}**: `{a['sentiment']}` ({a['score']:+.2f}) | Keywords: *{', '.join(a['keywords'])}*")


# =============================================================================
# TAB 4: STRATEGIC ARCHITECTURE & SUBMISSION REPORTS
# =============================================================================
with tab4:
    st.subheader("Architectural Blueprint & Assessment Deliverables")
    st.caption("Technical blueprints, system design diagrams, and downloadable candidate reports for Cynbit Leadership.")

    rep_col1, rep_col2 = st.columns(2)
    with rep_col1:
        st.markdown("""
        ### 📄 AI Opportunity Report (Deliverable 1)
        **Core Focus:** Industry analysis of high-value AI opportunities across Cynbit:
        - Revio 2.0 (Reputation & Crisis AI)
        - Cynbit Studio / BitElevate (AI Code Architecture Evaluator)
        - TenantEase (Smart Lease OCR & Risk Engine)
        - Cynbit Nexus (Pre-Sales Architecture Blueprint Agent)
        """)
        try:
            with open("reports/AI_OPPORTUNITY_REPORT.md", "r", encoding="utf-8") as f:
                rep1_text = f.read()
            st.download_button(
                label="📥 Download AI Opportunity Report (Markdown)",
                data=rep1_text,
                file_name="Cynbit_AI_Opportunity_Report_Anurag_Pandey.md",
                mime="text/markdown",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Report not found: {e}")

    with rep_col2:
        st.markdown("""
        ### 🛠️ Technical Approach Report (Deliverable 3)
        **Core Focus:** Comprehensive production roadmap for Revio 2.0:
        - Compound AI System Architecture (ABSA + Crisis Neural Network)
        - Prompt Engineering & Few-Shot Templates
        - Evaluation Metrics (Precision/Recall on Crisis, Macro-F1 on Aspects)
        - Scale & Cloud Deployment on AWS/Azure
        """)
        try:
            with open("reports/TECHNICAL_APPROACH_REPORT.md", "r", encoding="utf-8") as f:
                rep2_text = f.read()
            st.download_button(
                label="📥 Download Technical Approach Report (Markdown)",
                data=rep2_text,
                file_name="Cynbit_Technical_Approach_Report_Anurag_Pandey.md",
                mime="text/markdown",
                use_container_width=True
            )
        except Exception:
            st.info("Technical Approach Report being compiled...")

    st.markdown("---")
    st.markdown("### 🏛️ Revio 2.0 Compound Multi-Agent System Architecture")
    st.markdown("""
```
                   +-------------------------------------------------------------+
                   |  External Review Sources (Google Maps, Yelp, Zomato, Social) |
                   +-------------------------------------------------------------+
                                                 │
                                                 ▼
                   +-------------------------------------------------------------+
                   |          Revio Ingestion Gateway & Pre-Processing           |
                   |      (Normalization, Deduplication, Metadata Enrichment)    |
                   +-------------------------------------------------------------+
                                                 │
                                                 ▼
             ┌───────────────────────────────────┴───────────────────────────────────┐
             ▼                                                                       ▼
+------------------------------------+                             +------------------------------------+
| Aspect-Based Sentiment Engine      |                             | Crisis & Legal Risk Classifier     |
| (6 Granular Categories, Polarity,  |                             | (Health & Safety, Legal, Fraud,    |
| Emotion & Root Cause Extraction)   |                             | PR Viral Threat Vectors, 0-100%)   |
+------------------------------------+                             +------------------------------------+
             │                                                                       │
             └───────────────────────────────────┬───────────────────────────────────┘
                                                 │
                                                 ▼
                   +-------------------------------------------------------------+
                   |           Multi-Agent Contextual Response Synthesizer       |
                   |  (Persona Agent + Brand Knowledge Base + Safety Guardrails) |
                   +-------------------------------------------------------------+
                                                 │
                         ┌───────────────────────┴───────────────────────┐
                         ▼                                               ▼
         [If Low Risk / Auto-Approve]                     [If High Risk / Critical Crisis]
                         │                                               │
                         ▼                                               ▼
     +---------------------------------------+       +---------------------------------------+
     | Instant Multi-Channel Auto-Publishing |       | Human-In-The-Loop (HITL) Queue &      |
     | (Public Review Response via API)      |       | Urgent Ticket (#REV-XXXX) Escalation   |
     +---------------------------------------+       +---------------------------------------+
```
    """)
