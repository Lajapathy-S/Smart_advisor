#!/bin/bash
# Setup script for deployment

echo "Setting up AI Smart Advisor..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/chroma_db
mkdir -p data/jsom_catalog

# Initialize vector database (optional)
# python scripts/initialize_db.py

echo "Setup complete!"
