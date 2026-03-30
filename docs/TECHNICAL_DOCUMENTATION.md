# Technical Documentation: AI Smart Advisor

## Executive Summary

This document provides a comprehensive technical overview of the AI Smart Advisor chatbot system, detailing how each component aligns with the project requirements and the technologies used to implement them.

---

## Current application snapshot (final presentation)

**Primary deployed experience:** **`src/frontend/app.py`** — **JSOM Smart Advisor** (single-page Streamlit app).

| Area | Technology |
|------|------------|
| **LLM** | **xAI Grok** via LangChain **`langchain_xai.ChatXAI`** (not OpenAI in this app path). |
| **Secrets** | **`XAI_API_KEY`**; optional **`XAI_MODEL`** (default **`grok-3-mini`**). |
| **Program scope** | User picks a **JSOM degree from a dropdown**; only that program’s official URL is scraped for context. |
| **Catalog data** | **Live fetch** of JSOM catalog / program pages using **`requests`** + **`BeautifulSoup`**. |
| **Skill gaps** | Topic labels from the public **`kamranahmedse/developer-roadmap`** JSON (same content family as roadmap.sh), compared to resume text + extracted skills (no LLM for this step). The results UI does not surface an extra roadmap marketing link. |
| **Program URLs** | Canonical map: **`src/data_processing/jsom_programs.py`** (`PROGRAM_URLS`); `app.py` may use an inline fallback if package imports fail on Streamlit Cloud. |
| **Resume** | PDF/TXT via **`pypdf`**; heuristic skill extraction. |
| **No false courses** | Model must return **`STATUS: NO_MATCH`** with a polite explanation when the degree does not align with the career path or catalog text is insufficient—no invented course lists. |

**Also in the repository (legacy / alternate flows):** `src/core/rag_engine.py`, `src/core/chatbot.py`, degree planner, career mentor, and skills analyzer modules. The **RAG engine** still uses **`langchain_openai`** (OpenAI embeddings + `ChatOpenAI`) **if** you run that chat pipeline and populate Chroma with `OPENAI_API_KEY`. That path is **separate** from the **JSOM Smart Advisor** Streamlit entrypoint above.

---

## 1. Requirements Mapping

### Requirement 1: Degree Planning ✅

**Requirement:** Create logic-based paths that help students map out courses based on their specific degree requirements.

**Implementation:**
- **Module:** `src/degree_planning/planner.py`
- **Technology:** Python with JSON data structures
- **How it works:**
  - Loads degree requirements from `data/jsom_catalog/catalog.json` (JSOM catalog)
  - Implements prerequisite-based topological sorting algorithm
  - Generates semester-by-semester course plans
  - Considers completed courses and current academic year
  - Outputs structured JSON-LD data for future AI model compatibility

**Key Features:**
- Prerequisite dependency resolution
- Credit-hour optimization per semester
- Personalized recommendations based on student progress
- Visual semester breakdown in Streamlit UI

---

### Requirement 2: Career Mentorship ✅

**Requirement:** Provide qualitative advice on career trajectories and the specific skills (technical and soft) required for various job roles.

**Implementation:**
- **Module:** `src/career_mentorship/mentor.py`
- **Technology:** Python with structured JSON data
- **How it works:**
  - Maintains career database in `data/career_data.json`
  - Provides detailed job role information including:
    - Technical skills required
    - Soft skills required
    - Career trajectory paths (entry → mid → senior)
    - Salary ranges
  - Categorizes skills by type (programming, tools, communication, leadership)
  - Generates JSON-LD structured data using Schema.org vocabulary

**Key Features:**
- Multi-level career path visualization
- Skill categorization and recommendations
- Industry-standard job role data
- Structured data output for future AI ingestion

---

### Requirement 3: Skills Gap Analysis ✅

**Requirement:** Develop a feature that compares a student's current profile against industry-standard requirements for specific job titles, identifying missing competencies.

**Implementation:**
- **Module:** `src/skills_analysis/analyzer.py`
- **Technology:** Python with set operations and comparison algorithms
- **How it works:**
  - Takes student profile (technical + soft skills)
  - Retrieves required skills for target job from career database
  - Performs set difference operations to identify gaps
  - Calculates coverage percentages (technical, soft, overall readiness)
  - Generates prioritized recommendations with:
    - Skill development suggestions
    - Estimated time to acquire
    - Priority levels (high/medium)
  - Supports multi-job comparison for career exploration

**Key Features:**
- Quantitative gap analysis (percentage-based)
- Actionable recommendations
- Multi-job comparison capability
- Priority-based skill development roadmap

---

## 2. Technology Stack & Justification

### 2.1 Orchestration: LangChain ✅

**Requirement:** Use LangChain or LlamaIndex for RAG implementation.

**Choice:** **LangChain**

**Why LangChain:**
- **Mature ecosystem:** Well-established with extensive documentation
- **Modular design:** Components can be swapped independently
- **Active community:** Large user base and regular updates
- **Streamlit compatibility:** Works seamlessly with Streamlit Cloud deployment
- **RAG capabilities:** Built-in retrieval-augmented generation support (used in the optional RAG/chat path)

**A) Primary Streamlit app — JSOM Smart Advisor (`src/frontend/app.py`)**

- **`langchain_xai.ChatXAI`** — Grok chat completions for course recommendations ( **`XAI_API_KEY`** ).
- No vector retrieval in this path: context is **scraped program text** + optional **extracted course-code catalog** passed in the prompt.

**B) Optional RAG / chat pipeline (`src/core/rag_engine.py`, `src/core/chatbot.py`)**

- **`langchain_text_splitters.RecursiveCharacterTextSplitter`** — Document chunking
- **`langchain_openai.OpenAIEmbeddings`** — Text embeddings (requires **`OPENAI_API_KEY`** if you use this path)
- **`langchain_openai.ChatOpenAI`** — LLM for generation in that pipeline
- **`langchain_community.vectorstores.Chroma`** — Vector storage
- **`langchain_core.prompts.ChatPromptTemplate`** — Prompt management
- **LCEL (LangChain Expression Language)** — Chain composition

**Architecture (RAG path only):**
```
User Query → Retriever → Document Retrieval → Context Formatting → LLM → Response
```

---

### 2.2 Vector Storage: ChromaDB ✅

**Requirement:** Use Pinecone or ChromaDB to index JSOM web content.

**Choice:** **ChromaDB** (with Pinecone support)

**Why ChromaDB:**
- **Free & Open Source:** No API costs, perfect for academic projects
- **Local persistence:** Data stored in `data/chroma_db/` directory
- **Easy deployment:** Works seamlessly on Streamlit Cloud
- **Lightweight:** Minimal dependencies, fast performance
- **Pinecone alternative:** Code supports Pinecone if needed (configurable)

**Implementation:**
- **File:** `src/core/rag_engine.py` → `_initialize_vector_store()`
- **Storage:** `./data/chroma_db/` (persistent across sessions)
- **Collection:** `jsom_catalog` (contains degree program documents)
- **Embeddings:** OpenAI `text-embedding-3-small` model
- **Configuration:** `config/config.yaml` → `vector_db.type: "chroma"`

**Data Flow:**
1. JSOM catalog data loaded from `data/jsom_catalog/catalog.json`
2. Documents chunked using `RecursiveCharacterTextSplitter`
3. Chunks embedded using OpenAI embeddings
4. Stored in ChromaDB with metadata (degree name, source, type)
5. Retrieved via similarity search during queries

**Pinecone Support:**
- Can be enabled by setting `vector_db.type: "pinecone"` in config
- Requires `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT` in secrets
- Useful for production scaling (not required for this project)

---

### 2.3 Frontend: Streamlit ✅

**Requirement:** Use Streamlit or Power Apps.

**Choice:** **Streamlit**

**Why Streamlit:**
- **Python-native:** Seamless integration with backend code
- **Rapid development:** UI components built with simple Python functions
- **Free hosting:** Streamlit Cloud provides free public app hosting
- **Interactive:** Built-in widgets, chat interface, data visualization
- **Accessibility:** Supports ADA compliance requirements

**Implementation:**
- **File:** `src/frontend/app.py`
- **Features (current JSOM Smart Advisor):**
  - Single focused flow: program dropdown, career-path dropdown, resume upload, recommendations
  - Live JSOM program page scraping for the selected degree
  - Skill detection from resume + roadmap-based skill gap section
  - Custom CSS (title, subtitle, button styling)
  - Polite **no-match** handling when degree and career path do not align

**Other modules (still in repo; not the main single-page flow above):**  
Degree planner, career mentor, and tabbed chat/RAG UI can be wired separately; the **deployed demo** described in this document’s snapshot is the **JSOM Smart Advisor** page.

**Deployment:**
- **Platform:** Streamlit Cloud (free tier)
- **URL:** `https://smartadvisor-zkpbruk7azu22m8ffxjlzp.streamlit.app`
- **Auto-deploy:** Updates automatically on git push

---

### 2.4 Web Scraping: BeautifulSoup ✅

**Requirement:** Use BeautifulSoup/Scrapy for web audits and Google Search Console for indexing data.

**Choice:** **BeautifulSoup** (Scrapy available but not used)

**Why BeautifulSoup:**
- **Simplicity:** Easier to use for straightforward HTML parsing
- **Sufficient:** JSOM catalog is static HTML, doesn't need Scrapy's advanced features
- **Lightweight:** Fewer dependencies than Scrapy
- **Integration:** Works well with `requests` library

**Implementation:**
- **File:** `src/data_processing/scraper.py`
- **Class:** `JSOMCatalogScraper` — legacy single-URL catalog scrape into structured JSON
- **Bulk helper:** `scrape_program_urls()` — iterates **`PROGRAM_URLS`** from `jsom_programs.py`, merges programs into one list, writes **`data/jsom_catalog/catalog.json`**

**Scripts:**
- **`scripts/scrape_catalog.py`** — run to refresh **`catalog.json`** from **all** configured program URLs (used by **`initialize_db.py`** / optional RAG).

**Main app path:** `src/frontend/app.py` uses **`requests`** + **BeautifulSoup** directly on the **single URL** for the user’s selected program (`fetch_program_context`); it does not require `catalog.json` to be present for recommendations.

---

## 3. Data Integrity & Source of Truth ✅

### Requirement: JSOM Catalog as Source of Truth

**Implementation:**

**A) JSOM Smart Advisor (Streamlit):**
- **Primary source:** live HTML from the **selected** official program URL (scraped each run).
- **Grounding aids:** regex extraction of **course code + title** lines from that HTML when present; LLM instructions require **STATUS: NO_MATCH** instead of inventing courses.

**B) Optional RAG pipeline:**
- **Primary data file:** `data/jsom_catalog/catalog.json` (from `scrape_catalog.py`)
- **RAG:** Vector database indexes JSOM-derived documents from that JSON
- **Prompt Engineering:** Explicit instructions to LLM:
  ```
  "Use ONLY the following context from the official JSOM catalog 
  (source of truth) to answer. If the answer is not in the context, 
  say so. Do not make up information."
  ```
- **Hallucination Prevention:**
  - RAG retrieves relevant catalog documents
  - LLM is constrained to use only retrieved context
  - System explicitly states when information is unavailable

**File:** `src/core/rag_engine.py` → `rag_prompt` (system message)

---

## 4. Accessibility (ADA Compliance) ✅

### Requirement: Adhere to ADA compliance standards

**Implementation:**

**HTML Structure:**
- Semantic HTML elements (`<h1>`, `<nav>`, `<main>`, `<section>`)
- Proper heading hierarchy
- Screen reader-friendly labels

**ARIA Support:**
- `aria-label` attributes on interactive elements
- `sr-only` class for screen reader-only content
- Role attributes where appropriate

**Keyboard Navigation:**
- All interactive elements accessible via keyboard
- Tab order follows logical flow
- Focus indicators visible

**Color Contrast:**
- WCAG AA compliant color schemes
- High contrast text/background ratios

**Implementation Files:**
- `src/frontend/app.py` - CSS and HTML structure
- `.streamlit/config.toml` - Streamlit accessibility settings

---

## 5. Future Proofing (Structured Data) ✅

### Requirement: Content recommendations structured (JSON-LD/Schema.org)

**Implementation:**

**JSON-LD Format:**
All responses include structured data using Schema.org vocabulary:

**Degree Planning:**
```json
{
  "@context": "https://schema.org",
  "@type": "EducationalOccupationalCredential",
  "credentialCategory": "degree",
  "name": "Business Administration",
  "totalCredits": 120,
  "coursePrerequisites": {...}
}
```

**Career Information:**
```json
{
  "@context": "https://schema.org",
  "@type": "Occupation",
  "name": "Business Analyst",
  "description": "...",
  "skills": [...]
}
```

**Skills Assessment:**
```json
{
  "@context": "https://schema.org",
  "@type": "SkillAssessment",
  "missingTechnicalSkills": [...],
  "missingSoftSkills": [...],
  "recommendations": [...]
}
```

**Files:**
- `src/degree_planning/planner.py` → `_create_structured_degree_data()`
- `src/career_mentorship/mentor.py` → `_create_structured_career_data()`
- `src/skills_analysis/analyzer.py` → `_create_structured_gap_data()`

**Benefits:**
- Easy ingestion by future AI models
- Search engine optimization (SEO)
- Interoperability with other systems
- Machine-readable metadata

---

## 6. System Architecture

### 6.1 Primary: JSOM Smart Advisor (`src/frontend/app.py`)

```
┌──────────────────────────────────────────────────────────────┐
│  Streamlit — JSOM Smart Advisor (single page)                  │
│  Program dropdown → Career path → Resume (PDF/TXT)           │
└────────────────────────────┬─────────────────────────────────┘
                             │
     ┌───────────────────────┼───────────────────────┐
     ▼                       ▼                       ▼
┌─────────────┐      ┌─────────────────┐     ┌──────────────────┐
│ requests +  │      │ Heuristic       │     │ Roadmap JSON     │
│ BeautifulSoup│     │ skill extract   │     │ (GitHub HTTP)    │
│ (1 program  │      │ (no LLM)        │     │ vs resume gaps   │
│  URL)       │      │                 │     │ (no LLM)         │
└──────┬──────┘      └────────┬────────┘     └────────┬─────────┘
       │                    │                        │
       └────────────────────┴────────────────────────┘
                            ▼
                 ┌──────────────────────┐
                 │ ChatXAI (Grok)       │
                 │ langchain-xai        │
                 │ XAI_API_KEY          │
                 └──────────────────────┘
```

### 6.2 Optional: RAG chat + planner modules

```
Client (Streamlit or script)
        │
        ▼
┌───────────────────┐     ┌─────────────┐ ┌──────────┐ ┌──────────┐
│ chatbot.py        │────►│ RAG Engine  │ │ Planner  │ │ Mentor / │
│ (intent, route)   │     │ + Chroma    │ │ module   │ │ Analyzer │
└───────────────────┘     │ OpenAI emb. │ └──────────┘ └──────────┘
                          └─────────────┘
```

**Optional RAG flow:** question → Chroma retrieval → context → `ChatOpenAI` (needs `OPENAI_API_KEY` and ingested docs).

**Degree planner (module):** `catalog.json` → prerequisite logic → semester plan — not the default `app.py` UI unless integrated separately.

---

## 7. Technical Decisions & Rationale

### 7.1 Why Not LlamaIndex?

**Decision:** Used LangChain instead of LlamaIndex

**Rationale:**
- LangChain has better Streamlit Cloud compatibility
- More mature ecosystem for RAG applications
- Better documentation and community support
- Easier integration with multiple LLM providers (e.g. xAI Grok in the main app; OpenAI in the optional RAG module)
- LlamaIndex added to requirements but not used (kept for future flexibility)

### 7.2 Why ChromaDB Over Pinecone?

**Decision:** ChromaDB as default, Pinecone as optional

**Rationale:**
- **Cost:** ChromaDB is free; Pinecone has usage limits on free tier
- **Deployment:** ChromaDB works seamlessly on Streamlit Cloud
- **Simplicity:** No external API keys required for ChromaDB
- **Performance:** Sufficient for academic project scale
- **Flexibility:** Code supports Pinecone if scaling needed

### 7.3 Why Streamlit Over Power Apps?

**Decision:** Streamlit chosen

**Rationale:**
- **Language:** Python-native (matches backend)
- **Cost:** Free hosting on Streamlit Cloud
- **Development Speed:** Faster to build and iterate
- **Integration:** Seamless with LangChain and Python ecosystem
- **Accessibility:** Built-in support for ADA compliance

### 7.4 Modern LangChain Approach (LCEL)

**Decision:** Used LangChain Expression Language instead of deprecated RetrievalQA

**Rationale:**
- **Future-proof:** LCEL is the modern, recommended approach
- **Flexibility:** Easier to customize and extend
- **Compatibility:** Works with latest LangChain versions
- **Maintainability:** Less deprecated code, better long-term support

**Implementation:**
```python
# Modern LCEL Chain
chain = rag_prompt | llm | StrOutputParser()
answer = chain.invoke({"context": context, "question": question})
```

---

## 8. Deployment Architecture

### 8.1 Hosting: Streamlit Cloud

**Platform:** Streamlit Community Cloud (Free Tier)

**Configuration:**
- **Repository:** GitHub (`Lajapathy-S/Smart_advisor`)
- **Branch:** `main`
- **Main File:** `src/frontend/app.py`
- **Python Version:** 3.13.12 (managed by Streamlit Cloud)
- **Dependencies:** `requirements.txt`

**Environment Variables (Secrets):**
- **`XAI_API_KEY`** — Required for **JSOM Smart Advisor** (Grok) on Streamlit Cloud
- **`XAI_MODEL`** — Optional (default **`grok-3-mini`**)
- **`OPENAI_API_KEY`** — Only if you use the **RAG/chatbot** path with OpenAI embeddings + chat (`rag_engine.py`)
- **`PINECONE_API_KEY`** / **`PINECONE_ENVIRONMENT`** — Optional (if using Pinecone)

**URL:** `https://smartadvisor-zkpbruk7azu22m8ffxjlzp.streamlit.app`

### 8.2 Data Storage

**Local Files:**
- `data/jsom_catalog/catalog.json` - Degree program data
- `data/career_data.json` - Career information
- `data/chroma_db/` - Vector database (created at runtime)

**Persistence:**
- Catalog and career data: Committed to git repository
- Vector database: Created on first run, persists in Streamlit Cloud storage

---

## 9. Key Technical Features

### 9.1 RAG (Retrieval-Augmented Generation)

**Scope:** This subsection describes the **optional** pipeline in `src/core/rag_engine.py`. The **JSOM Smart Advisor** page does **not** use vector retrieval; it grounds Grok on **scraped program HTML** (see §6.1).

**Purpose (RAG path):** Ground LLM answers in retrieved JSOM catalog chunks from Chroma.

**Process:**
1. User query → Embedding vector
2. Similarity search in ChromaDB → Top K relevant documents
3. Documents formatted as context
4. LLM generates answer using context + query
5. Response includes source citations

**Benefits:**
- Accurate information (grounded in source)
- Traceable sources
- Prevents fabrication
- Scalable (can add more documents)

### 9.2 Intent Classification

**Purpose:** Route queries to appropriate modules

**Method:** Keyword-based scoring
- Degree keywords: "degree", "course", "requirement", "curriculum"
- Career keywords: "career", "job", "role", "trajectory"
- Skills keywords: "skill", "gap", "missing", "competency"

**File:** `src/core/chatbot.py` → `_classify_intent()`

### 9.3 Prerequisite Resolution

**Purpose:** Generate valid course sequences

**Algorithm:** Topological sort
- Builds dependency graph from prerequisites
- Ensures prerequisites completed before dependent courses
- Handles circular dependencies gracefully

**File:** `src/degree_planning/planner.py` → `_prioritize_courses()`

---

## 10. Testing & Quality Assurance

### 10.1 Code Structure

**Modular Design:**
- Each feature in separate module
- Clear separation of concerns
- Easy to test and maintain

**Error Handling:**
- Try-except blocks for API calls
- Graceful degradation (app works without API key)
- User-friendly error messages

### 10.2 Data Validation

**Input Validation:**
- User profile data validated
- Course codes normalized
- Skills lists sanitized

**Output Validation:**
- Structured data follows Schema.org format
- JSON-LD syntax validated
- Type checking with Python type hints

---

## 11. Performance Considerations

### 11.1 Optimization

**Caching:**
- Streamlit `@st.cache_resource` for module initialization
- Vector database persists between sessions
- Reduces redundant computations

**Efficiency:**
- Lazy loading of modules
- Efficient similarity search (top-k retrieval)
- Chunked document processing

### 11.2 Scalability

**Current Scale:**
- Suitable for academic project
- Handles multiple concurrent users
- Free tier sufficient for demo

**Future Scaling Options:**
- Switch to Pinecone for larger datasets
- Add caching layer (Redis)
- Implement async processing
- Use more powerful LLM models

---

## 12. Security & Best Practices

### 12.1 API Key Management

**Implementation:**
- Keys stored in Streamlit Cloud Secrets (not in code)
- `.env` file excluded from git (`.gitignore`)
- Environment variables loaded securely

**Files:**
- `config/.env.example` - Template (no real keys)
- `.gitignore` - Excludes `.env` files

### 12.2 Data Privacy

**Student Data:**
- No persistent storage of user conversations (session-based)
- No external data sharing
- All processing local to application

**Compliance:**
- FERPA considerations (no PII stored)
- Data sourced from public JSOM catalog

---

## 13. Future Enhancements

### 13.1 Potential Improvements

1. **Enhanced Scraping:**
   - Implement Scrapy for more complex catalog structures
   - Add Google Search Console integration
   - Automated catalog updates

2. **Advanced RAG:**
   - Multi-query retrieval
   - Re-ranking of results
   - Context compression

3. **User Features:**
   - Save degree plans
   - Export to PDF
   - Email notifications
   - Progress tracking

4. **Analytics:**
   - Usage statistics
   - Popular queries tracking
   - Performance metrics

---

## 14. Conclusion

The AI Smart Advisor successfully implements all required features using modern, scalable technologies:

✅ **Degree Planning** - Logic-based course path generation  
✅ **Career Mentorship** - Comprehensive career guidance  
✅ **Skills Gap Analysis** - Quantitative gap identification  
✅ **LangChain Orchestration** - Modern RAG implementation  
✅ **ChromaDB Vector Storage** - Efficient document retrieval  
✅ **Streamlit Frontend** - Interactive, accessible UI  
✅ **BeautifulSoup Scraping** - Web data extraction  
✅ **JSOM Catalog as Source of Truth** - Prevents hallucinations  
✅ **ADA Compliance** - Accessible design  
✅ **JSON-LD Structured Data** - Future-proof format  

The system is production-ready, well-documented, and follows best practices for maintainability and scalability.

---

## Appendix: File Structure

```
PartA_AI_Smart_Advisor/
├── src/
│   ├── core/
│   │   ├── rag_engine.py          # RAG implementation (LangChain LCEL)
│   │   └── chatbot.py              # Main chatbot coordinator
│   ├── degree_planning/
│   │   └── planner.py              # Degree planning logic
│   ├── career_mentorship/
│   │   └── mentor.py               # Career guidance module
│   ├── skills_analysis/
│   │   └── analyzer.py              # Skills gap analysis
│   ├── data_processing/
│   │   └── scraper.py              # Web scraping (BeautifulSoup)
│   └── frontend/
│       └── app.py                   # Streamlit UI
├── data/
│   ├── jsom_catalog/
│   │   └── catalog.json            # JSOM catalog data (source of truth)
│   └── career_data.json             # Career information
├── config/
│   ├── config.yaml                  # Application configuration
│   └── .env.example                 # Environment variables template
├── scripts/
│   ├── initialize_db.py            # Vector DB initialization
│   └── scrape_catalog.py           # Catalog scraping script
├── docs/
│   ├── TECHNICAL_DOCUMENTATION.md   # This file
│   ├── TECHNICAL_SUMMARY.md         # Quick reference
│   └── ARCHITECTURE.md              # System architecture
└── requirements.txt                 # Python dependencies
```

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Author:** Development Team
