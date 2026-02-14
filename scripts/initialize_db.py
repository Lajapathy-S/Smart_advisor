"""
Script to initialize the vector database with JSOM catalog data.
"""

import sys
import os
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.rag_engine import RAGEngine
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent / "config" / ".env")


def load_catalog_data():
    """Load catalog data from JSON file."""
    catalog_path = Path(__file__).parent.parent / "data" / "jsom_catalog" / "catalog.json"
    
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert to text documents
    documents = []
    metadatas = []
    
    for degree in data.get('degrees', []):
        # Create document text
        doc_text = f"Degree: {degree.get('name', '')}\n"
        doc_text += f"Total Credits: {degree.get('total_credits', 0)}\n"
        doc_text += f"Level: {degree.get('level', '')}\n\n"
        
        doc_text += "Core Courses:\n"
        for course in degree.get('core_courses', []):
            doc_text += f"- {course.get('code', '')}: {course.get('name', '')} ({course.get('credits', 0)} credits)\n"
        
        doc_text += "\nPrerequisites:\n"
        for course_code, prereqs in degree.get('prerequisites', {}).items():
            doc_text += f"{course_code} requires: {', '.join(prereqs)}\n"
        
        documents.append(doc_text)
        metadatas.append({
            "degree": degree.get('name'),
            "type": "degree_program",
            "source": "jsom_catalog"
        })
    
    return documents, metadatas


def main():
    """Initialize vector database."""
    print("Initializing vector database...")
    
    try:
        # Initialize RAG engine
        rag_engine = RAGEngine()
        
        # Load catalog data
        print("Loading catalog data...")
        documents, metadatas = load_catalog_data()
        
        print(f"Found {len(documents)} degree programs")
        
        # Add documents to vector store
        print("Adding documents to vector store...")
        rag_engine.add_documents(documents, metadatas)
        
        print("Vector database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
