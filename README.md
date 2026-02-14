# Part A: The AI Smart Advisor (Chatbot Interface)

A functional prototype of a chatbot that acts as a personalized concierge for students, providing degree planning, career mentorship, and skills gap analysis.

## Features

### 1. Degree Planning
- Logic-based paths that help students map out courses based on their specific degree requirements
- Uses official JSOM catalog as the "Source of Truth" to prevent hallucinations
- Structured course recommendations using JSON-LD/Schema format

### 2. Career Mentorship
- Qualitative advice on career trajectories
- Information on technical and soft skills required for various job roles
- Industry-standard career path guidance

### 3. Skills Gap Analysis
- Compares student's current profile against industry-standard requirements
- Identifies missing competencies for specific job titles
- Provides actionable recommendations

## Technology Stack

- **Frontend**: **Streamlit** - Modern, interactive web interface with ADA compliance
- **Orchestration**: LangChain/LlamaIndex (for RAG implementation)
- **Vector Storage**: Pinecone or ChromaDB (to index JSOM web content)
- **Analysis**: BeautifulSoup/Scrapy for web audits and Google Search Console for indexing data

## Project Structure

```
PartA_AI_Smart_Advisor/
├── src/
│   ├── core/              # Core chatbot logic and RAG implementation
│   ├── degree_planning/   # Degree planning module
│   ├── career_mentorship/ # Career mentorship module
│   ├── skills_analysis/   # Skills gap analysis module
│   ├── data_processing/   # Web scraping and data processing
│   └── frontend/          # Streamlit frontend application
├── data/
│   └── jsom_catalog/      # JSOM catalog data (source of truth)
├── config/                # Configuration files
├── tests/                 # Unit and integration tests
└── docs/                  # Documentation

```

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

1. Clone or navigate to this directory:
```bash
cd PartA_AI_Smart_Advisor
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
cp config/.env.example config/.env
```
Edit `config/.env` with your API keys and configuration.

6. Run the Streamlit application:
```bash
# Option 1: Using the run script
python run.py

# Option 2: Direct Streamlit command
streamlit run src/frontend/app.py
```

📖 **See [QUICKSTART.md](QUICKSTART.md) for detailed Streamlit usage guide**

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (for LLM)
- `PINECONE_API_KEY`: Your Pinecone API key (if using Pinecone)
- `PINECONE_ENVIRONMENT`: Pinecone environment
- `CHROMA_PERSIST_DIR`: Directory for ChromaDB persistence (if using ChromaDB)
- `JSOM_CATALOG_URL`: URL to the official JSOM catalog

## Data Sources

- **JSOM Catalog**: Official degree requirements and course information
- **Industry Standards**: Job requirements and skill mappings
- **Career Data**: Career trajectory information

## Accessibility

The web interface adheres to ADA compliance standards:
- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance

## Future Proofing

Content recommendations are structured using:
- JSON-LD format for semantic markup
- Schema.org vocabulary for structured data
- Easy ingestion by future AI models

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
This project follows PEP 8 style guidelines. Use black for formatting:
```bash
black src/
```

## Deployment

The application can be deployed using multiple methods:

### 🚀 Quick Deploy Options

1. **Streamlit Cloud** (Recommended - Free & Easy)
   - See [streamlit-cloud.md](streamlit-cloud.md) for detailed guide
   - Push to GitHub → Deploy on Streamlit Cloud → Done!

2. **Cloudflare Tunnel** (Expose Local App)
   - See [cloudflare-tunnel.md](cloudflare-tunnel.md) for setup
   - Perfect for sharing local development

3. **Docker** (Containerized)
   - Use `Dockerfile` and `docker-compose.yml`
   - Deploy to any cloud platform

4. **Other Platforms**
   - Railway, Render, Heroku supported
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for all options

📖 **Full deployment guide**: [README_DEPLOYMENT.md](README_DEPLOYMENT.md)

## License

[Add your license here]

## Contributors

[Add contributor information here]
