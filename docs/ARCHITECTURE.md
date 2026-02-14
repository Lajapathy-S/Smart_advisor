# Architecture Documentation

## System Overview

The AI Smart Advisor is a chatbot interface built using a RAG (Retrieval-Augmented Generation) architecture to provide personalized student guidance.

## Components

### 1. Core Module (`src/core/`)
- **RAG Engine**: Handles document retrieval and context augmentation
- **Chatbot**: Main interface coordinating between modules

### 2. Degree Planning Module (`src/degree_planning/`)
- Creates logic-based course paths
- Uses JSOM catalog as source of truth
- Generates semester-by-semester plans

### 3. Career Mentorship Module (`src/career_mentorship/`)
- Provides career trajectory information
- Lists required technical and soft skills
- Offers career path guidance

### 4. Skills Analysis Module (`src/skills_analysis/`)
- Compares student profile against job requirements
- Identifies skills gaps
- Generates actionable recommendations

### 5. Data Processing Module (`src/data_processing/`)
- Web scraping using BeautifulSoup
- JSOM catalog data extraction
- Career data aggregation

### 6. Frontend (`src/frontend/`)
- Streamlit-based web interface
- ADA-compliant design
- Real-time chat interface

## Data Flow

1. User inputs query through Streamlit interface
2. Chatbot classifies intent (degree planning, career, skills)
3. Query routed to appropriate module
4. Module uses RAG engine to retrieve relevant information
5. Response generated with structured data (JSON-LD)
6. Response displayed to user with sources

## Vector Database

- Supports both Pinecone and ChromaDB
- Stores JSOM catalog content as embeddings
- Enables semantic search for relevant information

## Structured Data

All responses include JSON-LD structured data using Schema.org vocabulary:
- Educational credentials for degrees
- Occupation data for careers
- Skill assessments for gap analysis

## Accessibility

- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance
