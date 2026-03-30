# Part A: AI Smart Advisor (JSOM)

**Primary product:** **JSOM Smart Advisor** — a single-page **Streamlit** app that matches a student’s **program**, **career path**, and **resume** to **live-scraped** JSOM degree pages and **Grok (xAI)** recommendations, with **roadmap-style** skill-gap topics and strict **no-hallucination** rules (`STATUS: OK` / `STATUS: NO_MATCH`).

**Also in the repo:** degree planning, career mentorship, and skills modules under `src/`, plus an **optional** RAG/chat stack (Chroma + OpenAI embeddings) for catalog-grounded Q&A — not required to run the main advisor.

## Features (JSOM Smart Advisor — `src/frontend/app.py`)

- **Program selection** — Dropdown maps to official JSOM URLs (`src/data_processing/jsom_programs.py`, with inline fallback in `app.py` for some deploy environments).
- **Live catalog context** — `requests` + **BeautifulSoup** scrape the selected program page; optional regex extraction of **course code + title** lines to anchor the LLM.
- **Resume** — PDF/TXT; **heuristic** skill extraction (no LLM for parsing).
- **Skill gaps** — Topics from public **developer-roadmap** JSON on GitHub, compared to resume text.
- **Recommendations** — **LangChain** **`langchain_xai.ChatXAI`** (Grok); responses must follow catalog alignment rules; optional fallback merge from extracted catalog lines.

## Legacy / optional modules

| Area | Location | Role |
|------|----------|------|
| Degree planning | `src/degree_planning/` | Prerequisite-aware plans from `catalog.json` |
| Career mentorship | `src/career_mentorship/` | Structured career JSON |
| Skills analysis | `src/skills_analysis/` | Gap analysis vs job DB |
| RAG chat | `src/core/rag_engine.py`, `chatbot.py` | Chroma + OpenAI if enabled |

## Technology stack

- **Frontend:** Streamlit (`src/frontend/app.py`)
- **LLM (main app):** xAI Grok via **`langchain-xai`**
- **Optional RAG:** LangChain + **OpenAI** embeddings + Chroma (or Pinecone)
- **Scraping:** BeautifulSoup + requests (`scraper.py`, in-app fetch)

## Project structure

```
PartA_AI_Smart_Advisor/
├── src/
│   ├── core/              # Optional RAG + chatbot
│   ├── degree_planning/
│   ├── career_mentorship/
│   ├── skills_analysis/
│   ├── data_processing/ # scraper, jsom_programs (PROGRAM_URLS)
│   └── frontend/        # JSOM Smart Advisor (main entry)
├── data/jsom_catalog/   # catalog.json (optional RAG / planner)
├── scripts/             # scrape_catalog.py, initialize_db.py
├── config/
├── tests/
└── docs/
```

## Setup

1. `cd PartA_AI_Smart_Advisor`
2. `python -m venv venv` and activate it
3. `pip install -r requirements.txt`
4. Copy `config/.env.example` → `config/.env` and set **`XAI_API_KEY`** (and optional **`XAI_MODEL`**).
5. Run: `python run.py` or `streamlit run src/frontend/app.py`

See **[QUICKSTART.md](QUICKSTART.md)** and **[SETUP.md](SETUP.md)** for detail. Optional: `python scripts/scrape_catalog.py` then `python scripts/initialize_db.py` for the RAG path (**`OPENAI_API_KEY`** required for embeddings in that path).

## Configuration (environment)

| Variable | When |
|----------|------|
| **`XAI_API_KEY`** | **Required** for Grok recommendations in the main app |
| **`XAI_MODEL`** | Optional (e.g. `grok-3-mini`) |
| **`OPENAI_API_KEY`** | Only if using `initialize_db.py` / RAG with OpenAI embeddings |
| **`PINECONE_*`**, **`CHROMA_PERSIST_DIR`** | Optional RAG / vector DB |

## Data sources

- **Live:** Selected JSOM program URLs from `PROGRAM_URLS`
- **Bulk JSON:** `scripts/scrape_catalog.py` → `data/jsom_catalog/catalog.json`
- **Roadmap topics:** GitHub `kamranahmedse/developer-roadmap` JSON (HTTP)

## Accessibility

Streamlit + custom CSS; aim for keyboard use and readable contrast. See `docs/` for presentation notes.

## Development

```bash
pytest tests/
black src/   # optional formatting
```

## Deployment

**Streamlit Cloud:** set secrets **`XAI_API_KEY`** (and optional **`XAI_MODEL`**). Main file: `src/frontend/app.py`.

Guides: [STREAMLIT_CLOUD_DEPLOY.md](STREAMLIT_CLOUD_DEPLOY.md), [streamlit-cloud.md](streamlit-cloud.md), [README_DEPLOYMENT.md](README_DEPLOYMENT.md), [DEPLOYMENT.md](DEPLOYMENT.md).

## License / contributors

Add as needed.
