import os
import io
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tavily import TavilyClient
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Load environment variables
load_dotenv()

# Retrieve API Keys from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Streamlit Page Config
st.set_page_config(
    page_title="The Briefing Room",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- "EXECUTIVE DOSSIER" DESIGN SYSTEM ---
# Palette:  ink #0A0C10 / surface #12151C / hairline #242A35
#           brass #B8925A (authority accent) / sage #5B9279 (verified/success)
#           parchment #E9E6DE (primary text) / slate #7C8494 (secondary text)
# Type:     Display serif "Fraunces" (dossier authority) + body "IBM Plex Sans"
#           + mono "IBM Plex Mono" for case-file labels, stamps, status codes
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --ink: #0A0C10;
    --surface: #12151C;
    --surface-raised: #171B24;
    --hairline: #242A35;
    --brass: #B8925A;
    --brass-dim: #8A6E45;
    --sage: #5B9279;
    --parchment: #E9E6DE;
    --slate: #7C8494;
}

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

.stApp {
    background:
        radial-gradient(ellipse 900px 500px at 15% -10%, rgba(184,146,90,0.07), transparent),
        var(--ink);
    color: var(--parchment);
}

section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--hairline);
}
section[data-testid="stSidebar"] * { color: var(--parchment); }

/* --- Case-file header block --- */
.dossier-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    border-bottom: 1px solid var(--hairline);
    padding-bottom: 18px;
    margin-bottom: 4px;
}
.dossier-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--brass);
    margin-bottom: 6px;
}
.dossier-title {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 2.5rem;
    line-height: 1.1;
    color: var(--parchment);
    margin: 0;
}
.dossier-title em { font-style: italic; font-weight: 500; color: var(--brass); }
.dossier-sub {
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--slate);
    font-size: 0.95rem;
    margin-top: 8px;
    max-width: 46ch;
}
.stamp {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--brass-dim);
    border: 1px solid var(--brass-dim);
    border-radius: 3px;
    padding: 6px 12px;
    transform: rotate(-2deg);
    white-space: nowrap;
    opacity: 0.85;
}

/* --- Sidebar identity mark --- */
.brand-mark {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.3rem;
    color: var(--parchment);
    padding-top: 4px;
}
.brand-mark span { color: var(--brass); }
.brand-caption {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--slate);
    margin-top: 2px;
    margin-bottom: 22px;
}

/* --- Inputs --- */
div[data-baseweb="input"] > div {
    background-color: var(--surface-raised) !important;
    border: 1px solid var(--hairline) !important;
    border-radius: 4px !important;
}
div[data-baseweb="input"] input {
    color: var(--parchment) !important;
    font-family: 'IBM Plex Sans', sans-serif;
}
div[data-baseweb="input"]:focus-within > div {
    border-color: var(--brass) !important;
    box-shadow: 0 0 0 3px rgba(184,146,90,0.15) !important;
}
label, .stTextInput label { color: var(--slate) !important; }

/* --- Primary action button --- */
.stButton > button {
    background: var(--brass) !important;
    color: var(--ink) !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
    font-family: 'IBM Plex Sans', sans-serif;
    height: 48px !important;
    letter-spacing: 0.02em;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: #cba36c !important;
    box-shadow: 0 4px 18px rgba(184,146,90,0.35) !important;
}

/* --- Download button --- */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--brass) !important;
    border: 1px solid var(--brass-dim) !important;
    border-radius: 4px !important;
    font-weight: 500 !important;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 0.04em;
    height: 46px !important;
}
.stDownloadButton > button:hover {
    border-color: var(--brass) !important;
    color: #cba36c !important;
    background: rgba(184,146,90,0.06) !important;
}

/* --- Folder-tab styled tabs --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    border-bottom: 1px solid var(--hairline);
}
.stTabs [data-baseweb="tab"] {
    height: 44px;
    background-color: transparent;
    border-radius: 6px 6px 0 0;
    border: 1px solid transparent;
    color: var(--slate);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    letter-spacing: 0.03em;
    padding: 0 18px;
}
.stTabs [aria-selected="true"] {
    background: var(--surface) !important;
    border: 1px solid var(--hairline) !important;
    border-bottom: 1px solid var(--surface) !important;
    color: var(--brass) !important;
}

/* --- Report surface (folder page) --- */
.folio {
    background: var(--surface);
    border: 1px solid var(--hairline);
    border-top: none;
    border-radius: 0 0 8px 8px;
    padding: 32px 36px;
}
.folio h3 { font-family: 'Fraunces', serif; color: var(--brass); font-weight: 600; }
.folio strong { color: var(--parchment); }
.folio p, .folio li { color: #C9C6BE; line-height: 1.65; }

/* --- Status line (replaces glowing pill) --- */
.status-line {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: var(--sage);
    display: flex;
    align-items: center;
    gap: 8px;
}
.status-line::before {
    content: "●";
    color: var(--sage);
    font-size: 0.6rem;
}

hr.divider { border: none; border-top: 1px solid var(--hairline); margin: 22px 0; }

/* Text area (raw payload viewer) */
textarea {
    background-color: var(--surface-raised) !important;
    color: var(--slate) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    border: 1px solid var(--hairline) !important;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="dossier-header">
    <div>
        <div class="dossier-eyebrow">Confidential &nbsp;·&nbsp; Prepared on Request</div>
        <h1 class="dossier-title">The Briefing <em>Room</em></h1>
        <p class="dossier-sub">Autonomous market intelligence, operational bottleneck analysis, and an executive-ready pitch — assembled from live web research.</p>
    </div>
    <div class="stamp">Brief No. AI-01</div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar: identity only, no status/architecture panel ---
with st.sidebar:
    st.markdown("""
    <div class="brand-mark">Briefing<span>Room</span></div>
    <div class="brand-caption">Enterprise Research Desk</div>
    """, unsafe_allow_html=True)
    st.markdown(
        "Enter a company name in the main panel and run the analysis. "
        "The desk pulls live sources, then drafts the report and pitch."
    )
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.caption("Every brief is generated fresh from current web sources — nothing is cached or reused between runs.")

# Helper Function: Search Tavily with Error Handling
def fetch_company_research(company: str, api_key: str) -> str:
    if not api_key:
        raise ValueError("Tavily API Key missing in .env file.")
    try:
        tavily = TavilyClient(api_key=api_key)
        query = f"{company} business overview major offerings developments expansion operational challenges real estate construction"
        response = tavily.search(query=query, search_depth="advanced", max_results=5)

        results = response.get('results', [])
        if not results:
            return "No real-time web results found for this target."

        context = "\n\n".join([f"Source: {res['url']}\nContent: {res['content']}" for res in results])
        return context
    except Exception as e:
        raise RuntimeError(f"Tavily Search Failed: {str(e)}")

# Helper Function: Generate Structured Intelligence Report with Groq
def generate_ai_report(company: str, research_context: str, api_key: str) -> str:
    if not api_key:
        raise ValueError("Groq API Key missing in .env file.")

    try:
        llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            groq_api_key=api_key,
            temperature=0.3
        )

        prompt = f"""
        You are an elite Business Strategy & AI Transformation Consultant.
        Analyze the company '{company}' using the provided live search research context.

        LIVE SEARCH RESEARCH CONTEXT:
        {research_context}

        Generate a comprehensive, highly structured Intelligence Report divided strictly into these 5 sections:

        ### 1. Company Overview
        - **What it does**: Brief summary.
        - **Industry**: Sector & primary market niche.
        - **Scale**: Operational size, footprint, or revenue standing.
        - **Geographic Presence**: Primary geographic regions.

        ### 2. Key Business Information
        - **Major Offerings**: Primary products/services.
        - **Recent Developments & Expansion Plans**: Specific recent projects, land acquisitions, or strategic initiatives.

        ### 3. Potential Business Challenges
        Identify 3 realistic operational bottlenecks, sales friction points, or customer experience challenges relevant to {company}'s specific operational model. Explain the reasoning behind each.

        ### 4. Hyper-Specific AI Opportunities
        Suggest 3 actionable AI solutions (e.g., Computer Vision for site progress/quality auditing, LLM automated contract/title document parsing, predictive lead scoring).
        *CRITICAL: Do NOT give generic answers like 'implement an AI chatbot'. Focus on hyper-tailored operational efficiencies for {company}.*

        ### 5. Personalized CEO Pitch
        Draft a concise, high-converting one-page executive pitch addressed to the CEO of {company}. Include:
        - Why you are reaching out
        - Core operational opportunities identified
        - Concrete AI transformation recommendations
        """

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        raise RuntimeError(f"Groq LLM Generation Failed: {str(e)}")

# Helper Function: Export PDF
def generate_pdf(text_data: str) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    body_style = ParagraphStyle('Body', parent=styles['Normal'], spaceAfter=6, fontSize=10, leading=12)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], spaceBefore=12, spaceAfter=6, fontSize=14, leading=16)

    story = []
    lines = text_data.split('\n')

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        if clean_line.startswith("### "):
            header_text = clean_line.replace("### ", "")
            story.append(Paragraph(f"<b>{header_text}</b>", heading_style))
        elif clean_line.startswith("- "):
            bullet_text = clean_line.replace("- ", "• ")
            story.append(Paragraph(bullet_text, body_style))
        else:
            story.append(Paragraph(clean_line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

st.markdown("<br>", unsafe_allow_html=True)

# Main Form Container Layout
with st.container():
    col1, col2 = st.columns([3, 1])

    with col1:
        company_input = st.text_input(
            "Target Enterprise",
            placeholder="e.g., Sobha, Prestige Group, Adani Realty...",
            label_visibility="collapsed"
        )

    with col2:
        generate_btn = st.button("Open the File", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Application Execution Logic
if generate_btn:
    if not company_input.strip():
        st.warning("Enter a target company name before opening a file.")
    elif not GROQ_API_KEY or not TAVILY_API_KEY:
        st.error("Missing API keys — set GROQ_API_KEY and TAVILY_API_KEY in your .env file.")
    else:
        try:
            with st.status(f"Compiling the file on **{company_input}**...", expanded=True) as status:
                st.write("Pulling live sources via Tavily...")
                search_context = fetch_company_research(company_input, TAVILY_API_KEY)

                st.write("Drafting the report and pitch with Groq Llama-3.3-70b...")
                report_markdown = generate_ai_report(company_input, search_context, GROQ_API_KEY)

                status.update(label="File compiled.", state="complete", expanded=False)

            # Tabbed Output View
            tab1, tab2, tab3 = st.tabs(["EXECUTIVE REPORT", "CEO PITCH", "SOURCE CONTEXT"])

            with tab1:
                st.markdown('<div class="folio">', unsafe_allow_html=True)
                st.markdown(report_markdown)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                st.markdown('<div class="folio">', unsafe_allow_html=True)
                if "### 5. Personalized CEO Pitch" in report_markdown:
                    pitch_content = report_markdown.split("### 5. Personalized CEO Pitch")[-1]
                    st.markdown(pitch_content)
                else:
                    st.markdown(report_markdown)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                st.markdown('<div class="folio">', unsafe_allow_html=True)
                st.markdown('<p class="status-line">Live sources retrieved</p>', unsafe_allow_html=True)
                st.text_area("Raw Web Payloads", search_context, height=350, label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)

            # Export PDF Section
            st.markdown("<br>", unsafe_allow_html=True)
            pdf_buffer = generate_pdf(report_markdown)

            st.download_button(
                label="EXPORT FULL REPORT — PDF",
                data=pdf_buffer,
                file_name=f"{company_input.lower().replace(' ', '_')}_ai_report.pdf",
                mime="application/pdf",
                type="primary"
            )

        except RuntimeError as err:
            st.error(f"Execution Error: {str(err)}")
        except Exception as e:
            st.error(f"Unexpected system error: {str(e)}")