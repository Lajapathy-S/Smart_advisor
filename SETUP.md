# Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Copy `config/.env.example` to `config/.env`
   - Add your API keys:
     - `OPENAI_API_KEY`: Required for LLM functionality
     - `PINECONE_API_KEY`: Optional, if using Pinecone
     - `PINECONE_ENVIRONMENT`: Optional, if using Pinecone

3. **Initialize Vector Database**
   ```bash
   python scripts/initialize_db.py
   ```
   This will scrape the JSOM catalog and populate the vector database.

4. **Run the Application**
   ```bash
   streamlit run src/frontend/app.py
   ```

## Detailed Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager
- OpenAI API key (for LLM functionality)

### Step-by-Step Installation

1. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**
   ```bash
   cp config/.env.example config/.env
   ```
   Edit `config/.env` and add your API keys.

4. **Prepare Data**
   - The sample catalog data is already in `data/jsom_catalog/catalog.json`
   - For production, use the scraper to get latest data:
     ```bash
     python scripts/scrape_catalog.py
     ```

5. **Initialize Vector Database**
   ```bash
   python scripts/initialize_db.py
   ```
   This creates embeddings and stores them in ChromaDB (or Pinecone if configured).

6. **Run Application**
   ```bash
   streamlit run src/frontend/app.py
   ```

## Configuration Options

### Vector Database Choice

**ChromaDB (Default)**
- No additional setup required
- Data stored locally in `data/chroma_db/`
- Set `VECTOR_DB_TYPE=CHROMA` in `.env`

**Pinecone**
- Requires Pinecone account and API key
- Set `VECTOR_DB_TYPE=PINECONE` in `.env`
- Configure `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT`

### LLM Configuration

Edit `config/config.yaml` to change:
- Model: `gpt-4-turbo-preview`, `gpt-3.5-turbo`, etc.
- Temperature: Controls randomness (0.0-1.0)
- Max tokens: Maximum response length

## Troubleshooting

### Import Errors
If you encounter import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

### Vector Database Issues
- For ChromaDB: Ensure `data/chroma_db/` directory exists and is writable
- For Pinecone: Verify API keys and index name

### API Key Issues
- Ensure `.env` file exists in `config/` directory
- Verify API keys are correct and have sufficient credits/quota

## Next Steps

- Review `docs/ARCHITECTURE.md` for system design
- Check `README.md` for feature overview
- Explore the codebase starting with `src/core/chatbot.py`
