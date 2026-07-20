# 🗂️ The Briefing Room — Enterprise AI Research & Recommendation Agent

An end-to-end automated business intelligence gatherer and executive pitch engine built to conduct real-time web research on target enterprise companies, extract operational bottlenecks, and generate hyper-personalized C-suite pitches.

---

## 1. Approach
To avoid relying on static, outdated LLM parametric memory, this application uses a **Retrieval-Augmented Generation (RAG) agent pipeline**:
1. **Live Web Data Retrieval:** Uses Tavily Search API to fetch real-time financial metrics, recent land/asset acquisitions, expansion plans, and operational news.
2. **Operational Bottleneck Deduction:** Feeds ground-truth search context into Groq's fast reasoning model (`llama-3.3-70b-versatile`) to deduce company-specific operational and sales friction points.
3. **Tailored Solution Mapping:** Maps identified bottlenecks directly to non-generic AI engineering solutions (e.g., Computer Vision site quality checks, automated contract/title parsing, predictive lead scoring).
4. **Multi-Format Export:** Presents structured outputs in an interactive dossier-styled UI and exports printable PDF executive summaries using ReportLab.

---

## 2. System Architecture
```text
[ User Input: Company Name ]
             │
             ▼
   [ Tavily Search API ] ──► Fetches Live Corporate Context
             │
             ▼
  [ Groq Llama-3.3-70b ] ──► Analyzes Operational Challenges & Strategic Fit
             │
             ▼
   [ Streamlit UI Engine ] ──► Renders 3-Tab Interactive Intelligence View
             │
             ▼
  [ ReportLab PDF Engine ] ──► Generates Downloadable Executive Summary
```

---

## 3. AI Tools & Frameworks Used
| Layer | Tool |
|---|---|
| LLM Core Engine | Groq API (`llama-3.3-70b-versatile`) |
| Search Tool | Tavily Web Search API |
| UI Framework | Streamlit (custom "Executive Dossier" theme — brass/ink palette, serif + monospace type) |
| PDF Export Engine | ReportLab |
| Environment Management | python-dotenv |
| AI Development Support | Claude / Gemini |

---

## 4. Setup
```bash
pip install streamlit python-dotenv langchain-groq tavily-python reportlab
```

Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Run the app:
```bash
streamlit run app.py
```