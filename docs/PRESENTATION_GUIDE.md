# Presentation Guide: AI Smart Advisor

## Quick Reference for Team Presentations

This guide helps you explain the AI Smart Advisor project to stakeholders, team members, or evaluators.

---

## 🎯 Project Overview (30 seconds)

**What it is:**
**JSOM Smart Advisor** — one Streamlit page where students pick a **JSOM program**, a **career path**, and upload a **resume**. The app **scrapes** that program’s official page, compares **roadmap-style** skill topics to the resume, and uses **Grok (xAI)** for course recommendations with strict **no-invented-courses** rules.

**Key achievement:**
Grounded recommendations from **live** degree pages plus honest **NO_MATCH** when fit is weak. **`XAI_API_KEY`** is required for the LLM step; scraping and roadmap JSON do not use OpenAI.

**Also in the repo:** standalone degree planner, career mentor, and skills modules, plus an **optional** RAG path (OpenAI + Chroma) — separate from the main demo.

---

## 📋 Requirements vs Implementation (2 minutes)

### ✅ Requirement 1: Degree Planning

**What was asked:** Logic-based paths for course mapping

**What we built:**
- Prerequisite-aware course sequencing
- Semester-by-semester planning
- Personalized recommendations based on completed courses
- Visual course path display

**Technology:** Python algorithms + JSON data structures

---

### ✅ Requirement 2: Career Mentorship

**What was asked:** Qualitative advice on career trajectories and skills

**What we built:**
- Comprehensive job role database
- Career path visualization (entry → mid → senior)
- Technical and soft skills breakdown
- Industry-standard salary information

**Technology:** Structured JSON data + Python processing

---

### ✅ Requirement 3: Skills Gap Analysis

**What was asked:** Compare student profile against job requirements

**What we built:**
- Quantitative gap analysis (percentage-based)
- Missing skills identification
- Prioritized recommendations
- Multi-job comparison capability

**Technology:** Set operations + comparison algorithms

---

## 🔧 Technology Stack (2 minutes)

### Orchestration: **LangChain**

**Why:** Mature ecosystem, works on Streamlit Cloud, supports both **xAI** (`langchain-xai`) and optional **OpenAI** RAG.

**What it does (main app):** **`ChatXAI`** calls Grok with a prompt built from **scraped program HTML**, resume-derived skills, career path, and extracted **course-code lines** when available.

**Optional path:** LCEL RAG in `rag_engine.py` with Chroma + OpenAI embeddings — not required for the live-scrape advisor.

---

### Vector Storage: **ChromaDB** (optional)

**When:** Only if you run **`scripts/initialize_db.py`** after **`scrape_catalog.py`** for the RAG/chat pipeline.

**Why:** Free, local persistence, Pinecone optional in config.

The **JSOM Smart Advisor** page does **not** need Chroma for its primary flow.

---

### Frontend: **Streamlit**

**Why:** Free Cloud hosting, Python-native, fast to iterate.

**What it provides:** Single-page flow (program + career + resume + results), custom CSS/branding, accessible defaults where applicable.

---

### Web Scraping: **BeautifulSoup** + **requests**

**Why:** Straightforward for static degree pages.

**What it does:** **Per-session** scrape of the URL for the selected program; **`scrape_catalog.py`** can refresh **`catalog.json`** for all URLs in **`jsom_programs.py`** for the optional vector pipeline.

---

## 🎨 Key Features (1 minute)

### 1. **Source of Truth Enforcement**
- RAG system uses ONLY JSOM catalog data
- Explicit prompts prevent hallucinations
- Responses cite sources

### 2. **ADA Compliance**
- Screen reader support
- Keyboard navigation
- High contrast design
- Semantic HTML

### 3. **Future-Proof Data**
- All responses include JSON-LD structured data
- Uses Schema.org vocabulary
- Easy for future AI models to ingest

---

## 🚀 Deployment (30 seconds)

**Platform:** Streamlit Cloud (Free)

**URL:** `https://smartadvisor-zkpbruk7azu22m8ffxjlzp.streamlit.app`

**Features:**
- Auto-deploys on git push
- Free hosting
- Public access
- Secure secrets management

---

## 💡 Technical Highlights (1 minute)

### Grounded LLM output
- Context from **one official program URL** per run; **STATUS: OK / NO_MATCH** contract
- Regex-backed **course list** hints when the model under-lists concrete courses

### Clear separation of concerns
- **Heuristic** resume skills; **GitHub roadmap JSON** for gap topics; **Grok** only for synthesis

### Optional RAG stack
- LCEL + Chroma + OpenAI still available for catalog Q&A experiments

---

## 📊 Metrics & Performance

**Response Time:**
- Heuristic skills + roadmap gap steps: typically sub-second (network dependent for GitHub JSON)
- JSOM Smart Advisor (scrape + Grok): ~3–15 seconds (xAI latency + page fetch)
- Optional RAG chat: embedding + retrieval + OpenAI — similar order of seconds

**Accuracy:**
- **JSOM Smart Advisor:** Course suggestions are constrained to scraped program text + STATUS rules; regex can list extracted codes when the model is thin.
- **Planner / career modules (when used):** Catalog JSON and structured career data drive deterministic outputs.

**Scalability:**
- Handles multiple concurrent users
- Free tier sufficient for demo
- Ready to scale with Pinecone if needed

---

## 🎓 How to Demo

### Demo Flow (5 minutes)

1. **Show the App** (30 sec)
   - Open Streamlit URL (**JSOM Smart Advisor**)
   - Single page: program dropdown, career path dropdown, resume upload

2. **Pick program + career** (45 sec)
   - Example: MS Business Analytics + Data Analyst
   - Explain that only that program’s official page is scraped

3. **Upload resume** (30 sec)
   - Show extracted skills and roadmap-based skill gaps

4. **Recommendations** (1 min)
   - Run recommendations; point out course codes when present
   - Optional: show **NO_MATCH** case (e.g. MS Accounting + Frontend) — honest, no invented courses

5. **Technical Overview** (30 sec)
   - Show code structure
   - Explain technologies
   - Highlight compliance features

---

## ❓ Common Questions & Answers

### Q: Why not use LlamaIndex?
**A:** LangChain covers our needs (xAI + optional OpenAI RAG). LlamaIndex is not required for the current paths.

### Q: Why ChromaDB instead of Pinecone?
**A:** ChromaDB is free, works perfectly on Streamlit Cloud, and handles our scale. Pinecone is supported if we need to scale later.

### Q: How do you prevent AI hallucinations?
**A:** For JSOM Smart Advisor: context is scraped from the **selected program URL only**; the model is instructed to use that text and return **NO_MATCH** rather than invent courses when there is no fit. Optional RAG path uses retrieved catalog chunks only.

### Q: Is the data up-to-date?
**A:** The **JSOM Smart Advisor** flow pulls **live** HTML from the official program URLs configured in `app.py`. The separate `scripts/scrape_catalog.py` pipeline can refresh `catalog.json` for the optional RAG path.

### Q: What about costs?
**A:** Hosting on Streamlit Cloud is free; **xAI Grok** usage is billed per your xAI plan (credits / subscription). Roadmap topic JSON is fetched from public GitHub (no key).

### Q: How is it ADA compliant?
**A:** Semantic HTML, ARIA labels, keyboard navigation, screen reader support, high contrast colors.

### Q: Can it scale?
**A:** Yes. Can switch to Pinecone, add caching, implement async processing. Current architecture supports growth.

---

## 📝 Talking Points Summary

**Opening:**
"Today I'll present the JSOM Smart Advisor — it matches a student’s program, career path, and resume to live degree-page content and uses Grok for recommendations, with strict rules so we don’t invent courses."

**Key Message:**
"We use LangChain with xAI on Streamlit, live BeautifulSoup scraping, and roadmap JSON for skill gaps; Chroma and OpenAI are optional for a separate RAG demo path."

**Closing:**
"The application is live, functional, and demonstrates all required capabilities. It's built with scalability and maintainability in mind, following best practices for production systems."

---

## 🎯 Key Selling Points

1. ✅ **Grounded recommendations** - Official program pages + NO_MATCH when needed
2. ✅ **Modern stack** - Streamlit, LangChain, xAI Grok, optional RAG
3. ✅ **Deployable** - Streamlit Cloud with `XAI_API_KEY`
4. ✅ **Free hosting tier** - Streamlit Cloud; xAI usage per your plan
5. ✅ **Accessible UI** - Streamlit + sensible defaults
6. ✅ **Documented** - Technical docs aligned with `app.py`
7. ✅ **Extensible** - Catalog JSON + Chroma path for RAG experiments

---

**Use this guide alongside TECHNICAL_DOCUMENTATION.md for detailed technical explanations.**
