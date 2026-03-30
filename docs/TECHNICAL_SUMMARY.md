# Technical Summary – JSOM Smart Advisor / AI Smart Advisor

Concise reference for **orchestration**, **hosting**, **LLM**, **vector storage**, **frontend**, and **data**.

---

## 1. Orchestration

**LangChain** is used in two places:

| Path | File(s) | What |
|------|---------|------|
| **Primary (Streamlit demo)** | `src/frontend/app.py` | **`langchain_xai.ChatXAI`** (Grok) for final course recommendations; context = scraped JSOM program page + prompt |
| **Optional RAG / chat** | `src/core/rag_engine.py`, `src/core/chatbot.py` | **`langchain_openai`** (embeddings + `ChatOpenAI`), Chroma, LCEL — requires **`OPENAI_API_KEY`** if you run this flow |

**Packages:** `langchain`, `langchain-core`, `langchain-community`, **`langchain-xai`**, `langchain-openai`, `langchain-text-splitters`.

LlamaIndex is **not** used.

---

## 2. Hosting

**Streamlit Community Cloud**

| What | Details |
|------|---------|
| **Entry** | `src/frontend/app.py` |
| **Secrets** | **`XAI_API_KEY`**, optional **`XAI_MODEL`** (e.g. `grok-3-mini`) |
| **Optional** | `OPENAI_API_KEY` only for the separate RAG/chat pipeline |

---

## 3. LLM (production app)

- **Provider:** xAI **Grok** via **`ChatXAI`**
- **Used for:** synthesizing recommendations from scraped program text + resume/skills + career path (not for PDF parsing or keyword skill extraction)
- **Guardrails:** `STATUS: OK` / `STATUS: NO_MATCH`; alignment hints; fallback list from regex-extracted catalog lines if the model returns too few concrete courses

---

## 4. What is *not* LLM-based

- **Resume text:** `pypdf` (PDF) or UTF-8 decode (TXT)
- **Skills from resume:** heuristics + keyword lists in `app.py` (`extract_skills_from_resume`)
- **Skill gaps (UI):** roadmap JSON labels vs resume text (`fetch_roadmap_labels`, `compute_skill_gaps`) — no LLM call for that step
- **Program HTML:** `requests` + `BeautifulSoup` (`fetch_program_context`)
- **Course-code anchors:** regex on scraped text (`extract_course_catalog`)

---

## 5. Vector storage (optional)

| When | What |
|------|------|
| **RAG/chat** | Chroma (or Pinecone) via `rag_engine.py` |
| **Populate** | `python scripts/scrape_catalog.py` → writes `data/jsom_catalog/catalog.json` from **all URLs** in `src/data_processing/jsom_programs.py` → `python scripts/initialize_db.py` embeds into Chroma |

The **JSOM Smart Advisor** main flow does **not** query Chroma; it scrapes the **selected** program URL per request.

---

## 6. Frontend (`src/frontend/app.py`)

| UI | Behavior |
|----|----------|
| **What program are you pursuing?** | Dropdown → maps to internal program key + URL |
| **Career path** | Dropdown (roadmap-aligned names) |
| **Resume** | PDF/TXT |
| **Output** | Skills detected, skill-gap topics, Grok recommendations (or NO_MATCH) |
| **Branding** | Optional logo from `assets/comet-smart-advisor.png` (CSS corner placement) |

Roadmap topic data is loaded from GitHub JSON; the UI no longer shows an extra “explore roadmap.sh” marketing line in results (logic may still use roadmap data internally).

---

## 7. Program URL registry

- **Canonical list:** `src/data_processing/jsom_programs.py` → **`PROGRAM_URLS`**
- **`app.py`** imports it when package resolution works; otherwise uses an inline fallback dict for Streamlit Cloud.

---

## Summary table

| Question | Answer |
|----------|--------|
| **Orchestration (demo)** | LangChain + **`langchain_xai`** + Grok in `src/frontend/app.py` |
| **Orchestration (optional)** | LangChain + OpenAI + Chroma in `src/core/rag_engine.py` |
| **Hosting secrets** | **`XAI_API_KEY`** (+ optional **`XAI_MODEL`**) |
| **Vector DB** | Optional; `scrape_catalog.py` + `initialize_db.py` |
| **JSOM text (demo)** | Live scrape of selected program URL |
| **Skill gaps** | Roadmap JSON topics vs resume (no LLM) |

---

## Quick reference – main files

| Concern | File(s) |
|---------|---------|
| **JSOM Smart Advisor** | `src/frontend/app.py` |
| **Program URLs** | `src/data_processing/jsom_programs.py` |
| **Bulk scrape → JSON** | `src/data_processing/scraper.py`, `scripts/scrape_catalog.py` |
| **Chroma ingest** | `scripts/initialize_db.py`, `src/core/rag_engine.py` |
| **RAG / chat (optional)** | `src/core/rag_engine.py`, `src/core/chatbot.py` |
| **Legacy modules** | `src/degree_planning/`, `src/career_mentorship/`, `src/skills_analysis/` |
