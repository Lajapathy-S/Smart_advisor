# Technical Summary – AI Smart Advisor

Answers to: **orchestration**, **hosting**, **vector storage**, **frontend**, and **data scraping**.

---

## 1. Orchestration

**Used: LangChain** (not LlamaIndex).

| What | Where | Purpose |
|------|--------|--------|
| **LangChain** | `src/core/rag_engine.py` | RAG: retrieval + LLM chain |
| **LangChain** | `src/core/chatbot.py` | Uses RAG engine for chat |

**Components:**
- **`langchain`** – text splitter, chains, prompts  
- **`langchain-openai`** – OpenAI embeddings and chat model  
- **`langchain-community`** – vector stores (Chroma, optional Pinecone)  
- **`RecursiveCharacterTextSplitter`** – chunking for RAG  
- **`RetrievalQA`** – chain that retrieves docs and calls the LLM  

LlamaIndex is in `requirements.txt` for optional use but is **not** used in the current code.

---

## 2. Hosting

**Used: Streamlit Cloud** (Option 1).

| What | Details |
|------|--------|
| **Platform** | [Streamlit Community Cloud](https://share.streamlit.io) |
| **How** | Connect GitHub repo → New app → Main file: `src/frontend/app.py` |
| **URL** | `https://<your-app-name>.streamlit.app` |
| **Secrets** | `OPENAI_API_KEY` (and optional Pinecone keys) in **Settings → Secrets** |

**Docs:**  
- `STREAMLIT_CLOUD_DEPLOY.md` – deploy steps  
- `README_DEPLOYMENT.md` – other options (Cloudflare Tunnel, Docker, etc.)

---

## 3. Vector Storage

**Default: ChromaDB.** Pinecone is supported but optional.

| Option | Config | Where |
|--------|--------|--------|
| **ChromaDB** (default) | `config/config.yaml` → `vector_db.type: "chroma"` | `src/core/rag_engine.py` |
| **Pinecone** | Set `vector_db.type: "pinecone"` + API keys | Same file, `_initialize_vector_store()` |

**ChromaDB:**
- **Library:** `langchain_community.vectorstores.Chroma` + `chromadb`
- **Persist path:** `./data/chroma_db` (created automatically)
- **Collection:** `jsom_catalog`
- **Indexed content:** JSOM catalog text (from `data/jsom_catalog/catalog.json`) after running `scripts/initialize_db.py`

**Pinecone:**  
Used only if you set `type: "pinecone"` and provide `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT`; otherwise the app uses ChromaDB.

---

## 4. Frontend

**Used: Streamlit.**

| What | Where |
|------|--------|
| **Framework** | Streamlit |
| **App entry** | `src/frontend/app.py` |
| **UI** | Tabs: Chat, Degree Plan, Career, Skills Analysis; sidebar for profile and actions |

**Features:**
- Chat with the AI advisor (when `OPENAI_API_KEY` is set)
- Degree planning (course path, semester plan)
- Career info and trajectory
- Skills gap analysis
- User profile (degree, year, courses, skills)
- Styling and accessibility considerations

---

## 5. How Data Was Scraped

**Scraping stack: `requests` + BeautifulSoup.** Scrapy is in `requirements.txt` but not used in the code.

### Scraper implementation

| File | Role |
|------|------|
| **`src/data_processing/scraper.py`** | Defines `JSOMCatalogScraper` (and `CareerDataScraper` stub) |
| **`scripts/scrape_catalog.py`** | Calls the scraper and writes `data/jsom_catalog/catalog.json` |

### Flow

1. **Fetch HTML**  
   - `requests.Session().get(JSOM_CATALOG_URL)`  
   - URL default:  
     `https://catalog.utdallas.edu/previous-years/2024-2025/undergraduate/programs/undergraduate-degree-plans`  
   - Overridable via env: `JSOM_CATALOG_URL`

2. **Parse**  
   - `BeautifulSoup(response.content, 'html.parser')`

3. **Extract**  
   - Program blocks: `soup.find_all(['div', 'section'], class_=...)` (class contains `'program'`)  
   - For each: name (h1/h2/h3), description, courses, requirements  
   - Courses: look for elements with `'course'` in class; parse "CODE - Name (N credits)"  
   - Requirements: look for elements with `'requirement'` in class; parse credit totals

4. **Save**  
   - `JSOMCatalogScraper.save_to_json(programs, output_path)`  
   - Writes `data/jsom_catalog/catalog.json` when run via `scripts/scrape_catalog.py`

### Current data in the app

- **Degree/course data:**  
  The app ships with a **manual** `data/jsom_catalog/catalog.json` (sample degrees/courses).  
  So the **live app uses this JSON**, not a fresh scrape, unless you run `scripts/scrape_catalog.py` and then `scripts/initialize_db.py` to refresh the vector DB.

- **Career data:**  
  `data/career_data.json` is **hand-written** (no scraper implemented for it).

### Summary table

| Question | Answer |
|--------|--------|
| **Orchestration** | **LangChain** (RAG: retrieval + QA chain) in `src/core/rag_engine.py`, `src/core/chatbot.py` |
| **Hosting** | **Streamlit Cloud**; deploy via GitHub + `src/frontend/app.py`; see `STREAMLIT_CLOUD_DEPLOY.md` |
| **Vector storage** | **ChromaDB** by default; **Pinecone** optional via config |
| **Frontend** | **Streamlit** – single app in `src/frontend/app.py` |
| **Scraping** | **BeautifulSoup** + **requests** in `src/data_processing/scraper.py`; run `scripts/scrape_catalog.py` to refresh catalog JSON |

---

## Quick reference – main files

| Concern | File(s) |
|--------|---------|
| Orchestration (RAG) | `src/core/rag_engine.py`, `src/core/chatbot.py` |
| Vector store (Chroma/Pinecone) | `src/core/rag_engine.py`, `config/config.yaml` |
| Frontend | `src/frontend/app.py` |
| Scraping | `src/data_processing/scraper.py`, `scripts/scrape_catalog.py` |
| Populate vector DB from catalog | `scripts/initialize_db.py` |
