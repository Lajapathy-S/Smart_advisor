"""
Streamlit Frontend Application
Main interface for the AI Smart Advisor chatbot.
"""

import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import json
import pandas as pd

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / "config" / ".env"

# Load .env if it exists (for local development)
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # For production, load from environment variables directly
    load_dotenv()

# Add parent directory to path
sys.path.append(str(project_root))

from src.core.chatbot import Chatbot
from src.degree_planning.planner import DegreePlanner
from src.career_mentorship.mentor import CareerMentor
from src.skills_analysis.analyzer import SkillsAnalyzer


# Page configuration
st.set_page_config(
    page_title="AI Smart Advisor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for accessibility and styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    /* Accessibility improvements */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    if not os.getenv("OPENAI_API_KEY"):
        st.session_state.chatbot = None
    else:
        try:
            st.session_state.chatbot = Chatbot()
        except Exception as e:
            st.session_state.chatbot = None
    
    st.session_state.messages = []
    st.session_state.user_context = {
        "degree": None,
        "year": None,
        "completed_courses": [],
        "skills": {"technical": [], "soft": []}
    }
    st.session_state.current_tab = "Chat"

# Initialize modules
@st.cache_resource
def get_modules():
    """Initialize and cache modules."""
    try:
        return {
            "degree_planner": DegreePlanner(),
            "career_mentor": CareerMentor(),
            "skills_analyzer": SkillsAnalyzer()
        }
    except Exception as e:
        st.error(f"Error initializing modules: {e}")
        return None

modules = get_modules()

# Sidebar for user context and navigation
with st.sidebar:
    st.title("🎓 AI Smart Advisor")
    st.caption("Your Personalized Student Concierge")
    st.markdown("---")
    
    # Navigation tabs
    tab_option = st.radio(
        "Navigation",
        ["💬 Chat", "📋 Degree Plan", "💼 Career", "🔍 Skills Analysis"],
        key="nav_tabs",
        label_visibility="collapsed"
    )
    st.session_state.current_tab = tab_option
    
    st.markdown("---")
    
    st.subheader("👤 User Profile")
    
    # Degree selection
    degree = st.selectbox(
        "Select Your Degree",
        ["Business Administration", "Information Systems", "Accounting", "Finance", "Marketing"],
        key="degree_select",
        help="Select your degree program"
    )
    st.session_state.user_context["degree"] = degree
    
    # Year selection
    year = st.selectbox(
        "Current Year",
        [1, 2, 3, 4],
        key="year_select",
        help="Select your current academic year"
    )
    st.session_state.user_context["year"] = year
    
    # Completed courses
    with st.expander("📚 Completed Courses"):
        completed_courses_input = st.text_input(
            "Enter course codes (comma-separated)",
            value=",".join(st.session_state.user_context["completed_courses"]),
            help="Enter course codes you have completed, separated by commas",
            label_visibility="collapsed"
        )
        if completed_courses_input:
            st.session_state.user_context["completed_courses"] = [
                c.strip() for c in completed_courses_input.split(",") if c.strip()
            ]
        
        if st.session_state.user_context["completed_courses"]:
            st.write("**Your completed courses:**")
            for course in st.session_state.user_context["completed_courses"]:
                st.write(f"• {course}")
    
    # Skills input
    with st.expander("🛠️ Your Skills"):
        technical_skills = st.text_input(
            "Technical Skills (comma-separated)",
            value=",".join(st.session_state.user_context["skills"]["technical"]),
            help="Enter your technical skills"
        )
        soft_skills = st.text_input(
            "Soft Skills (comma-separated)",
            value=",".join(st.session_state.user_context["skills"]["soft"]),
            help="Enter your soft skills"
        )
        
        if technical_skills:
            st.session_state.user_context["skills"]["technical"] = [
                s.strip() for s in technical_skills.split(",") if s.strip()
            ]
        if soft_skills:
            st.session_state.user_context["skills"]["soft"] = [
                s.strip() for s in soft_skills.split(",") if s.strip()
            ]
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat history cleared!")
        st.rerun()
    
    st.markdown("---")
    st.caption("Data sourced from official JSOM catalog")

# Main content area based on selected tab
if st.session_state.current_tab == "💬 Chat":
    st.markdown('<h1 class="main-header">💬 Chat with AI Advisor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sr-only">AI Smart Advisor chatbot interface for degree planning, career mentorship, and skills gap analysis</p>', unsafe_allow_html=True)
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 Welcome! I'm your AI Smart Advisor. Ask me about:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div class="feature-card">
                    <h3>📋 Degree Planning</h3>
                    <p>Get personalized course recommendations based on your degree requirements</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div class="feature-card">
                    <h3>💼 Career Guidance</h3>
                    <p>Learn about career paths, required skills, and job market insights</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div class="feature-card">
                    <h3>🔍 Skills Analysis</h3>
                    <p>Identify skills gaps and get recommendations for career readiness</p>
                </div>
                """, unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display structured data if available
                if "structured_data" in message:
                    with st.expander("📊 View Structured Data (JSON-LD)"):
                        st.json(message["structured_data"])
    
    # Chat input
    if st.session_state.chatbot:
        user_input = st.chat_input(
            "Ask me about degree planning, career guidance, or skills analysis...",
            key="chat_input"
        )
        
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Process message
            with st.spinner("🤔 Thinking..."):
                try:
                    response = st.session_state.chatbot.process_message(
                        user_input,
                        st.session_state.user_context
                    )
                    
                    # Add assistant response
                    response_text = response.get("answer", "I'm sorry, I couldn't process that request.")
                    
                    # Format response with sources if available
                    if response.get("sources"):
                        response_text += "\n\n**📚 Sources:**"
                        for i, source in enumerate(response.get("sources", [])[:3], 1):
                            response_text += f"\n{i}. {source.page_content[:200]}..."
                    
                    message_to_add = {
                        "role": "assistant",
                        "content": response_text
                    }
                    
                    # Add structured data if available
                    if response.get("structured_data"):
                        message_to_add["structured_data"] = response["structured_data"]
                    
                    st.session_state.messages.append(message_to_add)
                except Exception as e:
                    st.error(f"Error processing message: {e}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "I encountered an error. Please try again or check your configuration."
                    })
            
            st.rerun()
    else:
        st.warning(
            "**Chat is not available** — add your **OPENAI_API_KEY** in Streamlit Cloud "
            "**Settings → Secrets** (or in `config/.env` when running locally) to enable the AI chat. "
            "You can still use **Degree Plan**, **Career**, and **Skills Analysis** tabs."
        )

elif st.session_state.current_tab == "📋 Degree Plan":
    st.markdown('<h1 class="main-header">📋 Degree Planning</h1>', unsafe_allow_html=True)
    
    if modules and st.session_state.user_context["degree"]:
        degree = st.session_state.user_context["degree"]
        year = st.session_state.user_context["year"]
        completed = st.session_state.user_context["completed_courses"]
        
        if st.button("🔄 Generate Degree Plan", type="primary", use_container_width=True):
            with st.spinner("Generating your personalized degree plan..."):
                try:
                    plan = modules["degree_planner"].create_course_path(degree, year, completed)
                    
                    if "error" not in plan:
                        # Display overview
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Degree", plan.get("degree", "N/A"))
                        with col2:
                            st.metric("Current Year", plan.get("current_year", "N/A"))
                        with col3:
                            st.metric("Completed Courses", len(completed))
                        
                        # Display semester plan
                        st.subheader("📅 Semester Plan")
                        for semester in plan.get("semester_plan", []):
                            with st.expander(f"Semester {semester['semester']} ({semester['total_credits']} credits)"):
                                df = pd.DataFrame(semester["courses"])
                                st.dataframe(df[["code", "name", "credits"]], use_container_width=True)
                        
                        # Display recommended path
                        st.subheader("🎯 Recommended Course Path")
                        if plan.get("recommended_path"):
                            df = pd.DataFrame(plan["recommended_path"])
                            st.dataframe(df[["code", "name", "credits"]], use_container_width=True)
                    else:
                        st.error(plan.get("error", "Unknown error"))
                except Exception as e:
                    st.error(f"Error generating degree plan: {e}")
    else:
        st.info("👈 Please select your degree in the sidebar to generate a degree plan.")

elif st.session_state.current_tab == "💼 Career":
    st.markdown('<h1 class="main-header">💼 Career Mentorship</h1>', unsafe_allow_html=True)
    
    if modules:
        job_title = st.text_input("Enter a job title to explore", placeholder="e.g., Business Analyst, Data Analyst")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Get Career Info", use_container_width=True):
                if job_title:
                    with st.spinner("Fetching career information..."):
                        try:
                            career_info = modules["career_mentor"].get_career_info(job_title)
                            
                            if "error" not in career_info:
                                st.subheader(f"📊 {career_info.get('title', job_title)}")
                                st.write(career_info.get('description', ''))
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.write("**Technical Skills:**")
                                    for skill in career_info.get('technical_skills', []):
                                        st.write(f"• {skill}")
                                
                                with col_b:
                                    st.write("**Soft Skills:**")
                                    for skill in career_info.get('soft_skills', []):
                                        st.write(f"• {skill}")
                                
                                if career_info.get('career_path'):
                                    st.subheader("🚀 Career Path")
                                    for i, level in enumerate(career_info['career_path'], 1):
                                        st.write(f"{i}. {level}")
                            else:
                                st.error(career_info.get("error"))
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        with col2:
            if st.button("📈 View Career Trajectory", use_container_width=True):
                if job_title:
                    with st.spinner("Analyzing career trajectory..."):
                        try:
                            trajectory = modules["career_mentor"].get_career_trajectory(job_title)
                            
                            if "error" not in trajectory:
                                st.subheader("Career Trajectory")
                                st.json(trajectory)
                            else:
                                st.error(trajectory.get("error"))
                        except Exception as e:
                            st.error(f"Error: {e}")

elif st.session_state.current_tab == "🔍 Skills Analysis":
    st.markdown('<h1 class="main-header">🔍 Skills Gap Analysis</h1>', unsafe_allow_html=True)
    
    if modules:
        target_job = st.text_input("Enter target job title", placeholder="e.g., Business Analyst")
        
        if st.button("🔍 Analyze Skills Gap", type="primary", use_container_width=True):
            if target_job and st.session_state.user_context["skills"]:
                with st.spinner("Analyzing your skills gap..."):
                    try:
                        student_profile = {
                            "technical_skills": st.session_state.user_context["skills"]["technical"],
                            "soft_skills": st.session_state.user_context["skills"]["soft"]
                        }
                        
                        analysis = modules["skills_analyzer"].analyze_gap(student_profile, target_job)
                        
                        if "error" not in analysis:
                            gap_analysis = analysis.get("gap_analysis", {})
                            
                            # Display metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Technical Coverage", f"{gap_analysis.get('technical_coverage', 0):.1f}%")
                            with col2:
                                st.metric("Soft Skills Coverage", f"{gap_analysis.get('soft_coverage', 0):.1f}%")
                            with col3:
                                st.metric("Overall Readiness", f"{gap_analysis.get('overall_readiness', 0):.1f}%")
                            
                            # Display gaps
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.subheader("❌ Missing Technical Skills")
                                for skill in gap_analysis.get('technical_gap', []):
                                    st.write(f"• {skill}")
                            
                            with col_b:
                                st.subheader("❌ Missing Soft Skills")
                                for skill in gap_analysis.get('soft_gap', []):
                                    st.write(f"• {skill}")
                            
                            # Display recommendations
                            st.subheader("💡 Recommendations")
                            for rec in analysis.get('recommendations', [])[:5]:
                                with st.expander(f"{rec.get('skill', 'Skill')} ({rec.get('priority', 'medium').upper()} priority)"):
                                    st.write(f"**Type:** {rec.get('type', 'N/A')}")
                                    st.write(f"**Estimated Time:** {rec.get('estimated_time', 'N/A')}")
                                    st.write("**Suggestions:**")
                                    for suggestion in rec.get('suggestions', []):
                                        st.write(f"• {suggestion}")
                        else:
                            st.error(analysis.get("error"))
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter a target job title and add your skills in the sidebar.")

# Footer with accessibility information
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>✅ This application adheres to ADA compliance standards. 
    For accessibility assistance, please contact support.</p>
    <p>📚 Data sourced from official JSOM catalog (Source of Truth)</p>
</div>
""", unsafe_allow_html=True)
