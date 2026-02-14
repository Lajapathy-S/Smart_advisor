"""
Degree Planning Module
Creates logic-based paths for students to map out courses based on degree requirements.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json


def _project_root() -> Path:
    """Project root (works for Streamlit Cloud and local)."""
    return Path(__file__).resolve().parent.parent.parent


class DegreePlanner:
    """Handles degree planning logic and course recommendations."""
    
    def __init__(self, catalog_data_path: str = None):
        """Initialize degree planner with catalog data."""
        if catalog_data_path is None:
            catalog_data_path = _project_root() / "data" / "jsom_catalog" / "catalog.json"
        self.catalog_data = self._load_catalog_data(str(catalog_data_path))
    
    def _load_catalog_data(self, path: str) -> Dict[str, Any]:
        """Load JSOM catalog data."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_degree_requirements(self, degree_name: str) -> Dict[str, Any]:
        """
        Get degree requirements for a specific degree.
        
        Args:
            degree_name: Name of the degree program
            
        Returns:
            Dictionary with degree requirements
        """
        # Search for degree in catalog
        for degree in self.catalog_data.get('degrees', []):
            if degree_name.lower() in degree.get('name', '').lower():
                return {
                    "degree": degree.get('name'),
                    "total_credits": degree.get('total_credits'),
                    "core_courses": degree.get('core_courses', []),
                    "electives": degree.get('electives', []),
                    "prerequisites": degree.get('prerequisites', {}),
                    "structured_data": self._create_structured_degree_data(degree)
                }
        
        return {"error": f"Degree '{degree_name}' not found in catalog"}
    
    def create_course_path(self, degree_name: str, current_year: int = 1, 
                          completed_courses: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a recommended course path for a student.
        
        Args:
            degree_name: Name of the degree program
            current_year: Current academic year (1-4)
            completed_courses: List of completed course codes
            
        Returns:
            Dictionary with recommended course path
        """
        requirements = self.get_degree_requirements(degree_name)
        
        if "error" in requirements:
            return requirements
        
        completed = set(completed_courses or [])
        remaining_core = [
            course for course in requirements['core_courses']
            if course.get('code') not in completed
        ]
        
        # Logic-based path: prioritize prerequisites and core courses
        recommended_path = self._prioritize_courses(remaining_core, requirements.get('prerequisites', {}))
        
        return {
            "degree": degree_name,
            "current_year": current_year,
            "completed_courses": list(completed),
            "recommended_path": recommended_path,
            "semester_plan": self._create_semester_plan(recommended_path, current_year),
            "structured_data": self._create_structured_path_data(recommended_path)
        }
    
    def _prioritize_courses(self, courses: List[Dict], prerequisites: Dict) -> List[Dict]:
        """Prioritize courses based on prerequisites and dependencies."""
        # Simple topological sort based on prerequisites
        prioritized = []
        remaining = courses.copy()
        added = set()
        
        while remaining:
            # Find courses with no unmet prerequisites
            for course in remaining:
                course_code = course.get('code', '')
                prereqs = prerequisites.get(course_code, [])
                
                if all(prereq in added for prereq in prereqs):
                    prioritized.append(course)
                    added.add(course_code)
                    remaining.remove(course)
                    break
            else:
                # If no course can be added, add remaining courses
                prioritized.extend(remaining)
                break
        
        return prioritized
    
    def _create_semester_plan(self, courses: List[Dict], start_year: int) -> List[Dict]:
        """Create a semester-by-semester plan."""
        semesters = []
        credits_per_semester = 15  # Typical full-time load
        
        current_semester = (start_year - 1) * 2 + 1
        current_credits = 0
        semester_courses = []
        
        for course in courses:
            course_credits = course.get('credits', 3)
            
            if current_credits + course_credits > credits_per_semester and semester_courses:
                semesters.append({
                    "semester": current_semester,
                    "courses": semester_courses,
                    "total_credits": current_credits
                })
                semester_courses = []
                current_credits = 0
                current_semester += 1
            
            semester_courses.append(course)
            current_credits += course_credits
        
        if semester_courses:
            semesters.append({
                "semester": current_semester,
                "courses": semester_courses,
                "total_credits": current_credits
            })
        
        return semesters
    
    def _create_structured_degree_data(self, degree: Dict) -> Dict[str, Any]:
        """Create JSON-LD structured data for degree."""
        return {
            "@context": "https://schema.org",
            "@type": "EducationalOccupationalCredential",
            "credentialCategory": "degree",
            "name": degree.get('name'),
            "educationalLevel": degree.get('level', 'undergraduate'),
            "totalCredits": degree.get('total_credits'),
            "coursePrerequisites": degree.get('prerequisites', {})
        }
    
    def _create_structured_path_data(self, courses: List[Dict]) -> List[Dict[str, Any]]:
        """Create JSON-LD structured data for course path."""
        return [
            {
                "@context": "https://schema.org",
                "@type": "Course",
                "courseCode": course.get('code'),
                "name": course.get('name'),
                "credits": course.get('credits')
            }
            for course in courses
        ]
