"""
Script to scrape JSOM catalog and update local data.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.data_processing.scraper import JSOMCatalogScraper
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / "config" / ".env")


def main():
    """Scrape JSOM catalog."""
    print("Scraping JSOM catalog...")
    
    scraper = JSOMCatalogScraper()
    programs = scraper.scrape_degree_programs()
    
    if programs:
        output_path = Path(__file__).parent.parent / "data" / "jsom_catalog" / "catalog.json"
        scraper.save_to_json(programs, str(output_path))
        print(f"Scraped {len(programs)} degree programs")
    else:
        print("No programs found. Check the catalog URL and HTML structure.")


if __name__ == "__main__":
    main()
