# Quick Start — Streamlit (JSOM Smart Advisor)

## Run the app

```bash
python run.py
```

or

```bash
streamlit run src/frontend/app.py
```

Custom port:

```bash
streamlit run src/frontend/app.py --server.port 8501
```

## Prerequisites

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `config/.env.example` → `config/.env` and set:
   - **`XAI_API_KEY`** — required for Grok recommendations
   - **`XAI_MODEL`** — optional (default in code is typically `grok-3-mini`)

3. **Optional (RAG only):** run `python scripts/scrape_catalog.py` then `python scripts/initialize_db.py` and set **`OPENAI_API_KEY`** for embeddings.

## What you see in the UI

Single **JSOM Smart Advisor** page:

- **What program are you pursuing?** — dropdown → live scrape of that program’s JSOM page
- **Career path** — dropdown aligned to roadmap-style roles
- **Resume** — PDF or TXT upload
- **Results** — detected skills, skill-gap topics, course recommendations from Grok (or a polite **NO_MATCH** when there is no fit)

There is no separate tabbed “Chat / Degree Plan / Career” flow in the current main entry file; legacy modules live under `src/` for reuse or demos.

## Troubleshooting

- **Streamlit won’t start:** `pip install streamlit`; try another port (`--server.port 8502`)
- **Recommendations fail / ask for key:** verify **`XAI_API_KEY`** in `config/.env` or Streamlit Secrets
- **Module errors:** run from project root; ensure `pip install -r requirements.txt`

## Local URL

- http://localhost:8501

## Tips

- Pick a program and career path that plausibly align for a strong **STATUS: OK** demo; use a mismatched pair to show **NO_MATCH** behavior.
- For optional RAG experiments, see `src/core/chatbot.py` and `docs/TECHNICAL_DOCUMENTATION.md`.
