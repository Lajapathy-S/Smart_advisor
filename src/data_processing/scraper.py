"""
Web Scraping Module
Scrapes JSOM catalog and other data sources using BeautifulSoup/Scrapy.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import json
import os
from urllib.parse import urljoin, urlparse


class JSOMCatalogScraper:
    """Scraper for JSOM catalog data."""
    
    def __init__(self, base_url: str = None):
        """Initialize scraper with base URL."""
        self.base_url = base_url or os.getenv(
            'JSOM_CATALOG_URL',
            'https://catalog.utdallas.edu/previous-years/2024-2025/undergraduate/programs/undergraduate-degree-plans'
        )
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_degree_programs(self) -> List[Dict[str, Any]]:
        """
        Scrape degree programs from JSOM catalog.
        
        Returns:
            List of degree program dictionaries
        """
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            programs = []
            
            # Extract degree program information
            # This is a template - actual selectors depend on the catalog structure
            program_elements = soup.find_all(['div', 'section'], class_=lambda x: x and 'program' in x.lower())
            
            for element in program_elements:
                program_data = self._extract_program_data(element)
                if program_data:
                    programs.append(program_data)
            
            return programs
        
        except Exception as e:
            print(f"Error scraping catalog: {e}")
            return []
    
    def _extract_program_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract program data from HTML element."""
        try:
            # Extract program name
            name_elem = element.find(['h1', 'h2', 'h3'], class_=lambda x: x and 'title' in str(x).lower())
            name = name_elem.get_text(strip=True) if name_elem else None
            
            # Extract description
            desc_elem = element.find(['p', 'div'], class_=lambda x: x and 'description' in str(x).lower())
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract courses
            courses = self._extract_courses(element)
            
            # Extract requirements
            requirements = self._extract_requirements(element)
            
            if name:
                return {
                    "name": name,
                    "description": description,
                    "courses": courses,
                    "requirements": requirements,
                    "structured_data": self._create_structured_program_data(name, courses, requirements)
                }
        
        except Exception as e:
            print(f"Error extracting program data: {e}")
        
        return None
    
    def _extract_courses(self, element) -> List[Dict[str, Any]]:
        """Extract course information from element."""
        courses = []
        
        # Look for course listings
        course_elements = element.find_all(['li', 'div', 'tr'], class_=lambda x: x and 'course' in str(x).lower())
        
        for course_elem in course_elements:
            course_text = course_elem.get_text(strip=True)
            
            # Try to parse course code and name
            # Format typically: "CS 2305 - Course Name (3 credits)"
            parts = course_text.split('-', 1)
            if len(parts) == 2:
                code = parts[0].strip()
                name_and_credits = parts[1].strip()
                
                # Extract credits
                credits = 3  # Default
                if '(' in name_and_credits:
                    credit_part = name_and_credits.split('(')[-1].split(')')[0]
                    try:
                        credits = int(credit_part.split()[0])
                    except:
                        pass
                
                courses.append({
                    "code": code,
                    "name": name_and_credits.split('(')[0].strip(),
                    "credits": credits
                })
        
        return courses
    
    def _extract_requirements(self, element) -> Dict[str, Any]:
        """Extract degree requirements."""
        requirements = {
            "total_credits": None,
            "core_credits": None,
            "elective_credits": None,
            "prerequisites": {}
        }
        
        # Look for requirements section
        req_elements = element.find_all(['div', 'section'], class_=lambda x: x and 'requirement' in str(x).lower())
        
        for req_elem in req_elements:
            text = req_elem.get_text()
            
            # Extract credit requirements
            if 'total' in text.lower() and 'credit' in text.lower():
                try:
                    credits = int(''.join(filter(str.isdigit, text.split('total')[1].split()[0])))
                    requirements["total_credits"] = credits
                except:
                    pass
        
        return requirements
    
    def _create_structured_program_data(self, name: str, courses: List[Dict], 
                                        requirements: Dict) -> Dict[str, Any]:
        """Create JSON-LD structured data for program."""
        return {
            "@context": "https://schema.org",
            "@type": "EducationalOccupationalCredential",
            "credentialCategory": "degree",
            "name": name,
            "totalCredits": requirements.get("total_credits"),
            "courseCode": [course.get("code") for course in courses]
        }
    
    def save_to_json(self, data: List[Dict], output_path: str):
        """Save scraped data to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"degrees": data}, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {output_path}")


class CareerDataScraper:
    """Scraper for career and job market data."""
    
    def __init__(self):
        """Initialize career data scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_job_requirements(self, job_title: str) -> Dict[str, Any]:
        """
        Scrape job requirements from job boards.
        
        Args:
            job_title: Job title to search for
            
        Returns:
            Dictionary with job requirements
        """
        # This would integrate with job board APIs or scrape job postings
        # For now, return a template structure
        return {
            "title": job_title,
            "technical_skills": [],
            "soft_skills": [],
            "experience_required": None,
            "education_required": None
        }
    
    def aggregate_skills(self, job_titles: List[str]) -> Dict[str, List[str]]:
        """Aggregate skills across multiple job postings."""
        all_technical = set()
        all_soft = set()
        
        for job_title in job_titles:
            requirements = self.scrape_job_requirements(job_title)
            all_technical.update(requirements.get('technical_skills', []))
            all_soft.update(requirements.get('soft_skills', []))
        
        return {
            "technical_skills": list(all_technical),
            "soft_skills": list(all_soft)
        }
