"""
Streamlit Frontend Application
JSOM Smart Advisor - Resume-based course recommendation.
"""

import os
import re
from pathlib import Path
import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pypdf import PdfReader


# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / "config" / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


# Page configuration
st.set_page_config(
    page_title="JSOM Smart Advisor",
    page_icon="🎓",
    layout="centered",
)


# Minimal, accessible styling
st.markdown(
    """
<style>
    .title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.25rem;
        color: #0f172a;
    }
    .subtitle {
        text-align: center;
        font-size: 1rem;
        color: #4b5563;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 0.75rem;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
        border: 1px solid #e5e7eb;
    }
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
    .stButton>button {
        width: 100%;
        border-radius: 999px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)


PROGRAM_URLS = {
    "MS Accounting": "https://accounting.utdallas.edu/ms-accounting-flex/curriculum/",
    "MS Business Analytics": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/business-analytics",
    "MS Information Technology Management": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/information-technology-management",
    "MS Energy Management": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/energy-management",
    "MS Finance": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/finance",
    "MS Financial Technology and Analytics": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/financial-technology-and-analytics",
    "MS Healthcare Leadership and Management": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/healthcare-management#highlight_1",
    "MS International Management Studies": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/international-management-studies",
    "MS Management Science": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/management-science",
    "MS Marketing": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/marketing#course-requirements",
    "MS Supply Chain Management": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/supply-chain-management",
    "MS Systems Engineering and Management": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/supply-chain-management",
    "BS Accounting": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/accounting#highlight_1",
    "BS Business Administration": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/business-administration#business-economics-concentration",
    "BS Business Analytics and AI": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/business-analytics#degree-requirements",
    "BS Computer Information Systems and Technology": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/computer-information-systems-and-technology",
    "BS Cybersecurity and Risk Management": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/cybersecurity-and-risk-management/?hl=Core%20Curriculum%20Requirements:#highlight_1",
    "BS Finance": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/finance",
    "BS Global Business": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/global-business",
    "BS Healthcare Management": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/healthcare-management#highlight_1",
    "BS Human Resource Management": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/human-resource-management",
    "BS Marketing": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/marketing",
    "BS Supply Chain Management and Analytics": "https://catalog.utdallas.edu/2025/undergraduate/programs/jsom/supply-chain-management",
    "MBA": "https://catalog.utdallas.edu/2025/graduate/programs/jsom/business-administration",
}


@st.cache_resource(show_spinner=False)
def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.4,
            openai_api_key=api_key,
        )
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def fetch_program_context() -> str:
    """Fetch and lightly clean text from all JSOM program URLs."""
    parts = []
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; JSOM-Smart-Advisor/1.0)"
    }
    for name, url in PROGRAM_URLS.items():
        try:
            resp = requests.get(url, timeout=20, headers=headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            main = soup.find("main") or soup.body or soup
            text = " ".join(main.stripped_strings)
            # Limit per-program text to keep prompt size reasonable
            text = text[:4000]
            parts.append(f"PROGRAM: {name}\nURL: {url}\n{text}")
        except Exception:
            continue
    return "\n\n".join(parts)


def extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(texts)


def extract_resume_text(uploaded_file) -> str:
    """Extract plain text from uploaded resume (PDF or TXT)."""
    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    # Fallback: treat as text
    try:
        return uploaded_file.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def extract_skills_from_resume(text: str) -> list[str]:
    """Heuristic skill extraction without LLM (looks for 'Skills' section + known keywords)."""
    text_lower = text.lower()

    # Try to find a 'Skills' section
    skills_candidates: list[str] = []
    match = re.search(r"skills\\s*[:\\n]", text_lower)
    if match:
        section = text_lower[match.end() :]
        section = section.split("\\n\\n", 1)[0]
        tokens = re.split(r"[\\n,;•|]", section)
        skills_candidates.extend(t.strip() for t in tokens if t.strip())

    # Known technical/soft skills to look for
    known_skills = [
        "python",
        "sql",
        "excel",
        "tableau",
        "power bi",
        "r",
        "java",
        "c++",
        "c#",
        "javascript",
        "machine learning",
        "deep learning",
        "data analysis",
        "data engineering",
        "cloud",
        "aws",
        "azure",
        "gcp",
        "spark",
        "hadoop",
        "linux",
        "git",
        "docker",
        "kubernetes",
        "statistics",
        "accounting",
        "finance",
        "marketing",
        "supply chain",
        "project management",
        "leadership",
        "communication",
        "presentation",
        "teamwork",
    ]

    for skill in known_skills:
        if skill in text_lower and skill not in skills_candidates:
            skills_candidates.append(skill)

    # Clean up
    final_skills = []
    seen = set()
    for s in skills_candidates:
        s_clean = re.sub(r"[^a-z0-9+#./ ]", "", s.lower()).strip()
        if 2 <= len(s_clean) <= 40 and s_clean not in seen:
            seen.add(s_clean)
            final_skills.append(s_clean)
    return final_skills


def build_recommendation_prompt(skills: list[str], goal: str, programs_context: str) -> str:
    skills_str = ", ".join(skills) if skills else "not clearly specified"
    return f"""
You are the JSOM Smart Advisor at UT Dallas.

Student goal:
- Target role: {goal}
- Current skills: {skills_str}

Below is information about JSOM graduate and undergraduate programs and their course requirements.
Use ONLY this information to recommend specific subjects (courses) from these programs that will
help the student prepare for the target role.

For each recommended course, clearly state:
- Course name (and code if available)
- Which JSOM program it belongs to
- Why it is relevant for the target role

Focus especially on courses that build the missing skills relative to the target role.

JSOM PROGRAMS AND COURSES CONTEXT:
{programs_context}

Now provide a concise, structured recommendation:
1. List the most relevant JSOM programs for this role.
2. Under each program, list 3–8 high-impact courses.
3. Briefly explain why these courses help the student become a strong candidate for the role.
"""


def main():
    llm = get_llm()

    st.markdown('<h1 class="title">JSOM Smart Advisor</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Upload your resume, tell me your target role (e.g., '
        '"Data Engineer"), and I will recommend JSOM subjects that prepare you for that role.</p>',
        unsafe_allow_html=True,
    )

    if not llm:
        st.warning(
            "To enable recommendations, add your **OPENAI_API_KEY** in Streamlit Cloud "
            "**Settings → Secrets** (or in `config/.env` locally)."
        )

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        resume_file = st.file_uploader(
            "Upload your resume",
            type=["pdf", "txt"],
            help="Upload a recent version of your resume (PDF or TXT).",
        )

        target_role = st.text_input(
            "What role are you aiming for?",
            placeholder="e.g., Data Engineer, Business Analyst, Product Manager",
        )

        if st.button("Get JSOM Subject Recommendations"):
            if not resume_file:
                st.warning("Please upload your resume.")
            elif not target_role.strip():
                st.warning("Please enter your target role (for example, 'Data Engineer').")
            elif not llm:
                st.error(
                    "Recommendations are disabled because no OpenAI API key is configured. "
                    "Please set `OPENAI_API_KEY` in Streamlit secrets."
                )
            else:
                with st.spinner("Analyzing your resume and JSOM programs..."):
                    resume_text = extract_resume_text(resume_file)
                    skills = extract_skills_from_resume(resume_text)
                    programs_context = fetch_program_context()

                    prompt = build_recommendation_prompt(skills, target_role, programs_context)

                    try:
                        response = llm.invoke(prompt)
                        answer = response.content if hasattr(response, "content") else str(response)
                    except Exception as e:
                        answer = (
                            "I encountered an error while generating recommendations. "
                            "Please try again or check your API configuration."
                        )
                        st.error(str(e))

                if skills:
                    st.subheader("Skills detected from your resume")
                    st.write(", ".join(skills))

                st.subheader("Recommended JSOM Subjects for Your Goal")
                st.markdown(answer)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        """
<div style="text-align: center; color: #6b7280; font-size: 0.85rem;">
    <p>JSOM Smart Advisor • Uses official JSOM program pages as the source of truth for course information.</p>
</div>
""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
