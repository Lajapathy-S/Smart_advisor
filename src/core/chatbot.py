"""
Main Chatbot Interface
Coordinates between different modules (degree planning, career mentorship, skills analysis).
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from .rag_engine import RAGEngine
import json


class Chatbot:
    """Main chatbot interface that routes queries to appropriate modules."""
    
    def __init__(self, config_path: str = None):
        """Initialize chatbot with RAG engine."""
        self.rag_engine = RAGEngine(config_path)
        self.conversation_history = []
    
    def process_message(self, message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user message and return response.
        
        Args:
            message: User's message
            user_context: Optional user context (degree, year, etc.)
            
        Returns:
            Dictionary with response and metadata
        """
        # Determine intent
        intent = self._classify_intent(message)
        
        # Route to appropriate handler
        if intent == "degree_planning":
            response = self._handle_degree_planning(message, user_context)
        elif intent == "career_mentorship":
            response = self._handle_career_mentorship(message, user_context)
        elif intent == "skills_analysis":
            response = self._handle_skills_analysis(message, user_context)
        else:
            response = self._handle_general_query(message)
        
        # Store in conversation history
        self.conversation_history.append({
            "user_message": message,
            "response": response,
            "intent": intent
        })
        
        return response
    
    def _classify_intent(self, message: str) -> str:
        """
        Classify user intent from message.
        
        Args:
            message: User's message
            
        Returns:
            Intent category: 'degree_planning', 'career_mentorship', 'skills_analysis', or 'general'
        """
        message_lower = message.lower()
        
        degree_keywords = ['degree', 'course', 'requirement', 'curriculum', 'plan', 'semester', 'credit']
        career_keywords = ['career', 'job', 'role', 'position', 'trajectory', 'path', 'profession']
        skills_keywords = ['skill', 'competency', 'gap', 'missing', 'need', 'learn', 'ability']
        
        degree_score = sum(1 for keyword in degree_keywords if keyword in message_lower)
        career_score = sum(1 for keyword in career_keywords if keyword in message_lower)
        skills_score = sum(1 for keyword in skills_keywords if keyword in message_lower)
        
        scores = {
            'degree_planning': degree_score,
            'career_mentorship': career_score,
            'skills_analysis': skills_score
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return 'general'
    
    def _handle_degree_planning(self, message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle degree planning queries."""
        # Use RAG to get relevant degree information
        result = self.rag_engine.query(message)
        
        return {
            "type": "degree_planning",
            "answer": result["answer"],
            "sources": result.get("source_documents", []),
            "structured_data": self._extract_structured_degree_info(result["answer"])
        }
    
    def _handle_career_mentorship(self, message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle career mentorship queries."""
        result = self.rag_engine.query(message)
        
        return {
            "type": "career_mentorship",
            "answer": result["answer"],
            "sources": result.get("source_documents", []),
            "structured_data": self._extract_structured_career_info(result["answer"])
        }
    
    def _handle_skills_analysis(self, message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle skills gap analysis queries."""
        result = self.rag_engine.query(message)
        
        return {
            "type": "skills_analysis",
            "answer": result["answer"],
            "sources": result.get("source_documents", []),
            "structured_data": self._extract_structured_skills_info(result["answer"])
        }
    
    def _handle_general_query(self, message: str) -> Dict[str, Any]:
        """Handle general queries."""
        result = self.rag_engine.query(message)
        
        return {
            "type": "general",
            "answer": result["answer"],
            "sources": result.get("source_documents", [])
        }
    
    def _extract_structured_degree_info(self, answer: str) -> Dict[str, Any]:
        """Extract structured degree information in JSON-LD format."""
        # This would be enhanced with actual parsing logic
        return {
            "@context": "https://schema.org",
            "@type": "EducationalOccupationalCredential",
            "credentialCategory": "degree",
            "description": answer
        }
    
    def _extract_structured_career_info(self, answer: str) -> Dict[str, Any]:
        """Extract structured career information in JSON-LD format."""
        return {
            "@context": "https://schema.org",
            "@type": "Occupation",
            "description": answer
        }
    
    def _extract_structured_skills_info(self, answer: str) -> Dict[str, Any]:
        """Extract structured skills information in JSON-LD format."""
        return {
            "@context": "https://schema.org",
            "@type": "Skill",
            "description": answer
        }
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
