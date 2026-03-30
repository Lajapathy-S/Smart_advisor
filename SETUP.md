# Setup Guide

## Quick start (JSOM Smart Advisor)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment**
   - Copy `config/.env.example` to `config/.env`
   - Set **`XAI_API_KEY`** (required for recommendations in `src/frontend/app.py`)
   - Optional: **`XAI_MODEL`** (e.g. `grok-3-mini`)

3. **Run the app**
   ```bash
   streamlit run src/frontend/app.py
   ```
   Or: `python run.py`

No vector database is required for the main advisor flow (it scrapes the selected program URL per session).

---

## Optional: catalog JSON + vector DB (RAG path)

Use this only if you want **`src/core/rag_engine.py`** / chatbot retrieval over `catalog.json`.

1. **Scrape all program URLs** into one JSON file:
   ```bash
   python scripts/scrape_catalog.py
   ```
   URLs come from **`src/data_processing/jsom_programs.py`** (`PROGRAM_URLS`).

2. **Embed into Chroma** (requires **`OPENAI_API_KEY`** in `config/.env` for default embeddings):
   ```bash
   python scripts/initialize_db.py
   ```

3. Configure **`vector_db`** in `config/config.yaml` and optional Pinecone vars if not using Chroma.

---

## Prerequisites

- Python 3.9+
- **`XAI_API_KEY`** for the primary Streamlit experience
- **`OPENAI_API_KEY`** only for the optional RAG ingest / OpenAI chat path

---

## Troubleshooting

- **Import errors:** `pip install -r requirements.txt --upgrade`
- **“Add API key” in app:** set **`XAI_API_KEY`** (not OpenAI) for the JSOM Smart Advisor page
- **Chroma / RAG:** ensure `data/chroma_db/` is writable and `OPENAI_API_KEY` is set if using `initialize_db.py`

## Next steps

- **`docs/ARCHITECTURE.md`** — primary vs optional pipelines
- **`docs/TECHNICAL_SUMMARY.md`** — one-page technical reference
- **`src/frontend/app.py`** — main application entry
