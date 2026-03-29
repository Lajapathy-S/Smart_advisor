"""
Script to scrape JSOM catalog and update local data.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.data_processing.scraper import JSOMCatalogScraper
from src.data_processing.jsom_programs import PROGRAM_URLS
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / "config" / ".env")


def main():
    """Scrape all configured JSOM program URLs and save catalog JSON."""
    print("Scraping configured JSOM program URLs...")

    scraper = JSOMCatalogScraper()
    programs = scraper.scrape_program_urls(PROGRAM_URLS)

    if programs:
        output_path = Path(__file__).parent.parent / "data" / "jsom_catalog" / "catalog.json"
        scraper.save_to_json(programs, str(output_path))
        print(f"Scraped {len(programs)} program pages into catalog.json")
    else:
        print("No programs scraped. Check URLs/connectivity and parser logic.")


if __name__ == "__main__":
    main()
