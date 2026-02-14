"""
Skills Gap Analysis Module
Compares student's current profile against industry-standard requirements.
"""

from typing import List, Dict, Any, Optional
from ..career_mentorship.mentor import CareerMentor


class SkillsAnalyzer:
    """Analyzes skills gaps between student profile and job requirements."""
    
    def __init__(self):
        """Initialize skills analyzer."""
        self.career_mentor = CareerMentor()
    
    def analyze_gap(self, student_profile: Dict[str, Any], target_job: str) -> Dict[str, Any]:
        """
        Analyze the gap between student's skills and target job requirements.
        
        Args:
            student_profile: Dictionary with student's current skills and experience
            target_job: Target job title
            
        Returns:
            Dictionary with gap analysis results
        """
        # Get required skills for target job
        required_skills = self.career_mentor.get_required_skills(target_job)
        
        if "error" in required_skills:
            return required_skills
        
        student_skills = {
            "technical": set(student_profile.get('technical_skills', [])),
            "soft": set(student_profile.get('soft_skills', []))
        }
        
        required_technical = set(required_skills.get('technical_skills', []))
        required_soft = set(required_skills.get('soft_skills', []))
        
        # Calculate gaps
        technical_gap = required_technical - student_skills['technical']
        soft_gap = required_soft - student_skills['soft']
        
        # Calculate coverage
        technical_coverage = len(student_skills['technical'] & required_technical) / len(required_technical) * 100 if required_technical else 0
        soft_coverage = len(student_skills['soft'] & required_soft) / len(required_soft) * 100 if required_soft else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            technical_gap, soft_gap, student_profile
        )
        
        return {
            "target_job": target_job,
            "student_profile": student_profile,
            "required_skills": required_skills,
            "gap_analysis": {
                "technical_gap": list(technical_gap),
                "soft_gap": list(soft_gap),
                "technical_coverage": round(technical_coverage, 2),
                "soft_coverage": round(soft_coverage, 2),
                "overall_readiness": round((technical_coverage + soft_coverage) / 2, 2)
            },
            "recommendations": recommendations,
            "structured_data": self._create_structured_gap_data(
                technical_gap, soft_gap, recommendations
            )
        }
    
    def _generate_recommendations(self, technical_gap: set, soft_gap: set, 
                                 student_profile: Dict) -> List[Dict[str, Any]]:
        """Generate actionable recommendations to fill skills gaps."""
        recommendations = []
        
        # Technical skills recommendations
        for skill in technical_gap:
            recommendations.append({
                "type": "technical",
                "skill": skill,
                "priority": "high",
                "suggestions": self._get_skill_development_suggestions(skill, "technical"),
                "estimated_time": "3-6 months"
            })
        
        # Soft skills recommendations
        for skill in soft_gap:
            recommendations.append({
                "type": "soft",
                "skill": skill,
                "priority": "medium",
                "suggestions": self._get_skill_development_suggestions(skill, "soft"),
                "estimated_time": "6-12 months"
            })
        
        # Prioritize recommendations
        recommendations.sort(key=lambda x: (
            0 if x['priority'] == 'high' else 1,
            len(x['suggestions'])
        ))
        
        return recommendations
    
    def _get_skill_development_suggestions(self, skill: str, skill_type: str) -> List[str]:
        """Get suggestions for developing a specific skill."""
        suggestions = {
            "technical": {
                "python": [
                    "Take Python programming courses",
                    "Complete coding challenges on LeetCode",
                    "Build personal projects using Python"
                ],
                "sql": [
                    "Complete SQL tutorials and exercises",
                    "Practice with real databases",
                    "Take database management courses"
                ],
                "data analysis": [
                    "Learn pandas and numpy libraries",
                    "Complete data analysis projects",
                    "Take statistics and data science courses"
                ]
            },
            "soft": {
                "communication": [
                    "Join public speaking clubs",
                    "Take communication courses",
                    "Practice presenting to groups"
                ],
                "leadership": [
                    "Take on leadership roles in student organizations",
                    "Complete leadership training programs",
                    "Mentor other students"
                ],
                "teamwork": [
                    "Participate in group projects",
                    "Join team-based activities",
                    "Collaborate on open-source projects"
                ]
            }
        }
        
        skill_lower = skill.lower()
        for key, value in suggestions.get(skill_type, {}).items():
            if key in skill_lower:
                return value
        
        return [
            f"Research and study {skill}",
            f"Take courses related to {skill}",
            f"Practice {skill} in real-world scenarios"
        ]
    
    def compare_multiple_jobs(self, student_profile: Dict[str, Any], 
                             job_titles: List[str]) -> Dict[str, Any]:
        """
        Compare student profile against multiple job titles.
        
        Args:
            student_profile: Dictionary with student's current skills
            job_titles: List of job titles to compare against
            
        Returns:
            Dictionary with comparison results for each job
        """
        comparisons = {}
        
        for job_title in job_titles:
            gap_analysis = self.analyze_gap(student_profile, job_title)
            comparisons[job_title] = {
                "readiness_score": gap_analysis.get('gap_analysis', {}).get('overall_readiness', 0),
                "technical_gap_count": len(gap_analysis.get('gap_analysis', {}).get('technical_gap', [])),
                "soft_gap_count": len(gap_analysis.get('gap_analysis', {}).get('soft_gap', []))
            }
        
        # Sort by readiness score
        sorted_jobs = sorted(
            comparisons.items(),
            key=lambda x: x[1]['readiness_score'],
            reverse=True
        )
        
        return {
            "student_profile": student_profile,
            "comparisons": comparisons,
            "best_match": sorted_jobs[0][0] if sorted_jobs else None,
            "recommendations": self._get_cross_job_recommendations(comparisons)
        }
    
    def _get_cross_job_recommendations(self, comparisons: Dict) -> List[str]:
        """Get recommendations that apply across multiple jobs."""
        all_gaps = set()
        
        for job_data in comparisons.values():
            # This would need access to full gap analysis
            pass
        
        return [
            "Focus on developing core technical skills that are in high demand",
            "Build soft skills through real-world experiences",
            "Consider internships or projects that align with your target roles"
        ]
    
    def _create_structured_gap_data(self, technical_gap: set, soft_gap: set,
                                    recommendations: List[Dict]) -> Dict[str, Any]:
        """Create JSON-LD structured data for gap analysis."""
        return {
            "@context": "https://schema.org",
            "@type": "SkillAssessment",
            "missingTechnicalSkills": list(technical_gap),
            "missingSoftSkills": list(soft_gap),
            "recommendations": [
                {
                    "@type": "LearningResource",
                    "name": rec.get('skill'),
                    "description": ", ".join(rec.get('suggestions', []))
                }
                for rec in recommendations
            ]
        }
