"""
Career Mentorship Module
Provides qualitative advice on career trajectories and required skills.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json


def _project_root() -> Path:
    """Project root (works for Streamlit Cloud and local)."""
    return Path(__file__).resolve().parent.parent.parent


class CareerMentor:
    """Provides career mentorship and guidance."""
    
    def __init__(self, career_data_path: str = None):
        """Initialize career mentor with career data."""
        if career_data_path is None:
            career_data_path = _project_root() / "data" / "career_data.json"
        self.career_data = self._load_career_data(str(career_data_path))
    
    def _load_career_data(self, path: str) -> Dict[str, Any]:
        """Load career data."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"careers": []}
    
    def get_career_info(self, job_title: str) -> Dict[str, Any]:
        """
        Get information about a specific career/job role.
        
        Args:
            job_title: Name of the job title
            
        Returns:
            Dictionary with career information
        """
        for career in self.career_data.get('careers', []):
            if job_title.lower() in career.get('title', '').lower():
                return {
                    "title": career.get('title'),
                    "description": career.get('description'),
                    "technical_skills": career.get('technical_skills', []),
                    "soft_skills": career.get('soft_skills', []),
                    "career_path": career.get('career_path', []),
                    "salary_range": career.get('salary_range'),
                    "structured_data": self._create_structured_career_data(career)
                }
        
        return {"error": f"Career information for '{job_title}' not found"}
    
    def get_career_trajectory(self, job_title: str) -> Dict[str, Any]:
        """
        Get career trajectory for a specific job role.
        
        Args:
            job_title: Name of the job title
            
        Returns:
            Dictionary with career trajectory information
        """
        career_info = self.get_career_info(job_title)
        
        if "error" in career_info:
            return career_info
        
        return {
            "entry_level": self._get_entry_level_info(job_title),
            "mid_level": self._get_mid_level_info(job_title),
            "senior_level": self._get_senior_level_info(job_title),
            "career_path": career_info.get('career_path', []),
            "structured_data": self._create_structured_trajectory_data(career_info)
        }
    
    def get_required_skills(self, job_title: str) -> Dict[str, Any]:
        """
        Get required skills (technical and soft) for a job role.
        
        Args:
            job_title: Name of the job title
            
        Returns:
            Dictionary with required skills
        """
        career_info = self.get_career_info(job_title)
        
        if "error" in career_info:
            return career_info
        
        return {
            "job_title": job_title,
            "technical_skills": career_info.get('technical_skills', []),
            "soft_skills": career_info.get('soft_skills', []),
            "skill_categories": self._categorize_skills(career_info),
            "structured_data": self._create_structured_skills_data(career_info)
        }
    
    def _get_entry_level_info(self, job_title: str) -> Dict[str, Any]:
        """Get entry-level position information."""
        return {
            "title": f"Junior {job_title}",
            "required_experience": "0-2 years",
            "key_skills": []
        }
    
    def _get_mid_level_info(self, job_title: str) -> Dict[str, Any]:
        """Get mid-level position information."""
        return {
            "title": f"Mid-level {job_title}",
            "required_experience": "3-5 years",
            "key_skills": []
        }
    
    def _get_senior_level_info(self, job_title: str) -> Dict[str, Any]:
        """Get senior-level position information."""
        return {
            "title": f"Senior {job_title}",
            "required_experience": "6+ years",
            "key_skills": []
        }
    
    def _categorize_skills(self, career_info: Dict) -> Dict[str, List[str]]:
        """Categorize skills into different groups."""
        technical = career_info.get('technical_skills', [])
        soft = career_info.get('soft_skills', [])
        
        return {
            "programming": [s for s in technical if any(kw in s.lower() for kw in ['programming', 'language', 'code', 'develop'])],
            "tools": [s for s in technical if any(kw in s.lower() for kw in ['tool', 'software', 'platform', 'framework'])],
            "communication": [s for s in soft if any(kw in s.lower() for kw in ['communication', 'presentation', 'writing'])],
            "leadership": [s for s in soft if any(kw in s.lower() for kw in ['leadership', 'management', 'team'])],
            "other": [s for s in technical + soft if s not in [item for sublist in [
                [s for s in technical if any(kw in s.lower() for kw in ['programming', 'language', 'code', 'develop'])],
                [s for s in technical if any(kw in s.lower() for kw in ['tool', 'software', 'platform', 'framework'])],
                [s for s in soft if any(kw in s.lower() for kw in ['communication', 'presentation', 'writing'])],
                [s for s in soft if any(kw in s.lower() for kw in ['leadership', 'management', 'team'])]
            ] for item in sublist]]
        }
    
    def _create_structured_career_data(self, career: Dict) -> Dict[str, Any]:
        """Create JSON-LD structured data for career."""
        return {
            "@context": "https://schema.org",
            "@type": "Occupation",
            "name": career.get('title'),
            "description": career.get('description'),
            "occupationalCategory": career.get('category'),
            "skills": career.get('technical_skills', []) + career.get('soft_skills', [])
        }
    
    def _create_structured_trajectory_data(self, career_info: Dict) -> Dict[str, Any]:
        """Create JSON-LD structured data for career trajectory."""
        return {
            "@context": "https://schema.org",
            "@type": "CareerPath",
            "occupation": career_info.get('title'),
            "careerPath": career_info.get('career_path', [])
        }
    
    def _create_structured_skills_data(self, career_info: Dict) -> Dict[str, Any]:
        """Create JSON-LD structured data for skills."""
        return {
            "@context": "https://schema.org",
            "@type": "Skill",
            "occupation": career_info.get('title'),
            "technicalSkills": career_info.get('technical_skills', []),
            "softSkills": career_info.get('soft_skills', [])
        }
