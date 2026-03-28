# Technical Summary – JSOM Smart Advisor / AI Smart Advisor

Answers to: **orchestration**, **hosting**, **LLM**, **vector storage**, **frontend**, and **data scraping**.

---

## 1. Orchestration

**LangChain** is used in two places:

| Path | File(s) | What |
|------|---------|------|
| **Primary (deployed demo)** | `src/frontend/app.py` | **`langchain_xai.ChatXAI`** (Grok) for recommendations; context = scraped JSOM pages + prompt |
| **Optional RAG / chat** | `src/core/rag_engine.py`, `src/core/chatbot.py` | **`langchain_openai`** (embeddings + `ChatOpenAI`), Chroma, LCEL — requires **`OPENAI_API_KEY`** if you run this flow |

**Packages (see `requirements.txt`):** `langchain`, `langchain-core`, `langchain-community`, **`langchain-xai`**, `langchain-openai`, `langchain-text-splitters`.

LlamaIndex is **not** used in the current code paths described above.

---

## 2. Hosting

**Streamlit Community Cloud**

| What | Details |
|------|---------|
| **Platform** | [Streamlit Community Cloud](https://share.streamlit.io) |
| **Entry file** | `src/frontend/app.py` |
| **Secrets** | **`XAI_API_KEY`**, optional **`XAI_MODEL`** (e.g. `grok-3-mini`) |
| **Optional** | `OPENAI_API_KEY` only if using the separate RAG/chat pipeline |

**Docs:** `STREAMLIT_CLOUD_DEPLOY.md`, `README_DEPLOYMENT.md`

---

## 3. LLM (production app)

- **Provider:** xAI (**Grok**)
- **LangChain:** `ChatXAI`
- **Config:** env / Streamlit Secrets — **`XAI_API_KEY`**, **`XAI_MODEL`** (default `grok-3-mini` in code)

---

## 4. Vector storage

**Default in config:** ChromaDB for the **optional** RAG path (`rag_engine.py`).

| Option | When |
|--------|------|
| **ChromaDB** | RAG pipeline + `scripts/initialize_db.py` |
| **Pinecone** | Optional via `config.yaml` |

The **JSOM Smart Advisor** page does **not** require Chroma for its main recommendations (scraped text goes straight into the Grok prompt).

---

## 5. Frontend

**Streamlit — `src/frontend/app.py`**

| Feature | Description |
|---------|-------------|
| **Program** | Dropdown → maps to one JSOM program URL |
| **Career path** | Dropdown (roadmap.sh–aligned role names) |
| **Resume** | PDF/TXT upload |
| **Output** | Skills detected, roadmap-based gaps, Grok recommendations or **NO_MATCH** polite message |

---

## 6. How JSOM data is loaded (main app)

1. **`PROGRAM_URLS`** in `app.py` — official URLs per degree.
2. **`requests.get`** + **`BeautifulSoup`** — scrape selected program page(s).
3. Optional **regex** extraction of course codes for grounding the LLM.
4. **Skill gaps:** fetch roadmap JSON from **`kamranahmedse/developer-roadmap`** (same content family as [roadmap.sh](https://roadmap.sh/)), extract topic labels, compare to resume.

**Separate pipeline (catalog JSON + vector DB):** `src/data_processing/scraper.py`, `scripts/scrape_catalog.py`, `scripts/initialize_db.py` — used for the RAG/catalog path, not required for the live-scrape advisor flow.

---

## Summary table

| Question | Answer |
|----------|--------|
| **Orchestration (demo)** | LangChain + **`langchain_xai`** + Grok in `src/frontend/app.py` |
| **Orchestration (optional)** | LangChain + OpenAI + Chroma in `src/core/rag_engine.py` |
| **Hosting** | Streamlit Cloud; secrets **`XAI_API_KEY`** |
| **Vector storage** | Chroma (optional RAG); not used for main scrape→Grok flow |
| **Frontend** | Streamlit single-page JSOM Smart Advisor |
| **JSOM source (demo)** | Live scrape of program URLs in `app.py` |
| **Skill gaps** | roadmap.sh–style JSON from developer-roadmap GitHub |

---

## Quick reference – main files

| Concern | File(s) |
|---------|---------|
| **JSOM Smart Advisor (demo)** | `src/frontend/app.py` |
| **RAG / chat (optional)** | `src/core/rag_engine.py`, `src/core/chatbot.py` |
| **Degree / career / analyzer modules** | `src/degree_planning/`, `src/career_mentorship/`, `src/skills_analysis/` |
| **Config** | `config/config.yaml`, `config/.env` / Streamlit Secrets |
| **Catalog scrape (JSON pipeline)** | `src/data_processing/scraper.py`, `scripts/scrape_catalog.py` |
