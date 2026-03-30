# Architecture Documentation

## System overview

The repository contains **two related architectures**:

1. **JSOM Smart Advisor (primary Streamlit app)** — single-page tool: program + career dropdowns, resume upload, live scrape of one JSOM program page, heuristic skills + roadmap-topic gaps, **Grok** for final recommendations.
2. **Optional RAG chatbot stack** — Chroma + OpenAI embeddings + LangChain LCEL for catalog-grounded Q&A (`src/core/rag_engine.py`, `src/core/chatbot.py`).

---

## Primary path: JSOM Smart Advisor (`src/frontend/app.py`)

```
User → Streamlit UI
  → Resume: pypdf / text decode → extract_skills_from_resume (rules)
  → Career path → roadmap_slug → fetch_roadmap_labels (HTTP JSON) → compute_skill_gaps
  → Program choice → PROGRAM_URLS → fetch_program_context (requests + BeautifulSoup)
  → extract_course_catalog (regex)
  → build_recommendation_prompt → ChatXAI (Grok) → parse + optional fallback list
  → Markdown output
```

**Source of truth for courses (this path):** the **official program URL** scraped at request time, plus regex-extracted code/title lines when present.

---

## Optional path: RAG chatbot

```
User query → chatbot intent → RAGEngine
  → Chroma retriever → context string → ChatOpenAI → answer
```

**Source of truth (this path):** documents built from `data/jsom_catalog/catalog.json` (populated by `scripts/scrape_catalog.py` + `scripts/initialize_db.py`).

---

## Components (repository layout)

### `src/core/`
- **RAG Engine** — retrieval + OpenAI chat (optional pipeline)
- **Chatbot** — coordinates optional chat flow

### `src/degree_planning/`, `src/career_mentorship/`, `src/skills_analysis/`
- Standalone modules aligned with original project requirements; **not** the main Streamlit page flow unless wired separately.

### `src/data_processing/`
- **`jsom_programs.py`** — shared `PROGRAM_URLS` registry
- **`scraper.py`** — `JSOMCatalogScraper` (legacy catalog page scrape + **`scrape_program_urls`** for all configured program URLs)

### `scripts/`
- **`scrape_catalog.py`** — scrape all `PROGRAM_URLS` → `data/jsom_catalog/catalog.json`
- **`initialize_db.py`** — load JSON → build text docs → `RAGEngine.add_documents` → Chroma

### `src/frontend/`
- **`app.py`** — JSOM Smart Advisor UI and orchestration

---

## Vector database

- **ChromaDB** (default) or **Pinecone** (config) for the **RAG** path only.
- Persist directory: `data/chroma_db/` (see `config/config.yaml`).

---

## Accessibility & structured data

- Streamlit UI uses semantic structure where applicable; custom CSS for branding.
- Original modules may emit JSON-LD-style structures; the main advisor page focuses on human-readable recommendations.
