"""
Tests for chatbot functionality.
"""

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.core.chatbot import Chatbot


class TestChatbot:
    """Test cases for Chatbot class."""
    
    def test_chatbot_initialization(self):
        """Test chatbot initialization."""
        chatbot = Chatbot()
        assert chatbot is not None
        assert chatbot.rag_engine is not None
    
    def test_intent_classification(self):
        """Test intent classification."""
        chatbot = Chatbot()
        
        assert chatbot._classify_intent("What courses do I need for my degree?") == "degree_planning"
        assert chatbot._classify_intent("What career options are available?") == "career_mentorship"
        assert chatbot._classify_intent("What skills am I missing?") == "skills_analysis"
    
    def test_process_message(self):
        """Test message processing."""
        chatbot = Chatbot()
        response = chatbot.process_message("Hello")
        
        assert "answer" in response
        assert "type" in response
