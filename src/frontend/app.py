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
from langchain_xai import ChatXAI
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
    """
    Return Grok (xAI) model if XAI_API_KEY is set.
    """
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        return None
    model = os.getenv("XAI_MODEL", "grok-3-mini")
    try:
        return ChatXAI(
            model=model,
            temperature=0.4,
            max_retries=2,
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


def infer_target_role_skills(target_role: str) -> list[str]:
    """
    Return expected baseline skills for common target roles.
    Uses keyword matching so we can estimate skill gaps without another model call.
    """
    role = target_role.lower()

    role_skill_map = {
        "data engineer": [
            "python",
            "sql",
            "data engineering",
            "spark",
            "cloud",
            "aws",
            "docker",
            "linux",
            "git",
        ],
        "data analyst": [
            "sql",
            "excel",
            "tableau",
            "power bi",
            "statistics",
            "data analysis",
            "communication",
            "presentation",
        ],
        "business analyst": [
            "sql",
            "excel",
            "data analysis",
            "communication",
            "presentation",
            "project management",
        ],
        "product manager": [
            "communication",
            "leadership",
            "data analysis",
            "project management",
            "presentation",
            "teamwork",
        ],
        "software engineer": [
            "python",
            "java",
            "c++",
            "javascript",
            "git",
            "linux",
            "docker",
        ],
        "machine learning engineer": [
            "python",
            "machine learning",
            "deep learning",
            "statistics",
            "sql",
            "cloud",
            "gcp",
        ],
        "finance analyst": [
            "finance",
            "excel",
            "sql",
            "statistics",
            "communication",
            "presentation",
        ],
    }

    for role_key, skills in role_skill_map.items():
        if role_key in role:
            return skills

    # Generic fallback if role is not matched
    return [
        "sql",
        "excel",
        "communication",
        "presentation",
        "data analysis",
    ]


def compute_skill_gaps(resume_skills: list[str], target_role: str) -> tuple[list[str], list[str]]:
    """
    Compare extracted resume skills with target-role expected skills.
    Returns (matched_skills, missing_skills).
    """
    expected = infer_target_role_skills(target_role)
    resume_set = {s.lower().strip() for s in resume_skills}
    matched = [s for s in expected if s in resume_set]
    missing = [s for s in expected if s not in resume_set]
    return matched, missing


def extract_course_catalog(programs_context: str) -> str:
    """
    Extract course code + title pairs from scraped program text.
    This helps ground the LLM output in authentic catalog entries.
    """
    # Capture course codes like BUAN 6398, MIS 6324, ACCT6301
    code_pattern = re.compile(r"\b([A-Z]{2,5}\s?\d{4})\b")

    entries: list[str] = []
    seen = set()
    current_program = "Unknown Program"

    for line in programs_context.splitlines():
        if line.startswith("PROGRAM:"):
            current_program = line.replace("PROGRAM:", "", 1).strip() or "Unknown Program"
            continue

        for match in code_pattern.finditer(line):
            code = match.group(1).replace("  ", " ").strip()
            # Try to infer a nearby title from the text right after the code
            remainder = line[match.end() :].strip(" -:|,")
            title = ""
            if remainder:
                # Keep a short phrase for readability and avoid giant fragments
                title = re.split(r"[.;|]|  ", remainder)[0].strip()
                title = re.sub(r"\s+", " ", title)
                if len(title) > 90:
                    title = title[:90].rsplit(" ", 1)[0]

            if not title:
                continue

            key = (code, title.lower(), current_program)
            if key in seen:
                continue
            seen.add(key)
            entries.append(f"- {code} {title} ({current_program})")

    # Keep prompt concise while still giving enough grounded options
    return "\n".join(entries[:250])


def _infer_program_level(pursuing: str) -> str:
    text = pursuing.lower()
    if any(k in text for k in ["master", "masters", "ms ", "m.s", "mba", "graduate"]):
        return "graduate"
    if any(k in text for k in ["bachelor", "bachelors", "bs ", "b.s", "undergraduate"]):
        return "undergraduate"
    return "unknown"


def filter_program_context_by_pursuit(programs_context: str, pursuing: str) -> str:
    """
    Filter scraped program blocks based on user's pursuit.
    Example: Masters/MS -> keep MS/MBA programs, exclude BS programs.
    """
    if not programs_context.strip():
        return programs_context

    level = _infer_program_level(pursuing)
    blocks = programs_context.split("\n\nPROGRAM: ")
    normalized_blocks = []
    for idx, block in enumerate(blocks):
        # First block may already start with PROGRAM:
        if idx == 0 and block.startswith("PROGRAM: "):
            normalized_blocks.append(block)
        elif idx == 0:
            # Skip unexpected preamble content
            continue
        else:
            normalized_blocks.append("PROGRAM: " + block)

    if level == "unknown":
        return programs_context

    filtered = []
    for block in normalized_blocks:
        first_line = block.splitlines()[0].lower()
        if level == "graduate":
            if first_line.startswith("program: ms ") or first_line.startswith("program: mba"):
                filtered.append(block)
        elif level == "undergraduate":
            if first_line.startswith("program: bs "):
                filtered.append(block)

    # Fallback to original context if filter becomes too restrictive
    return "\n\n".join(filtered) if filtered else programs_context


def build_recommendation_prompt(
    pursuing: str,
    skills: list[str],
    goal: str,
    programs_context: str,
    course_catalog: str,
) -> str:
    skills_str = ", ".join(skills) if skills else "not clearly specified"
    return f"""
You are the JSOM Smart Advisor at UT Dallas.

Student goal:
- What they are pursuing: {pursuing}
- Target role: {goal}
- Current skills: {skills_str}

Below is information about JSOM graduate and undergraduate programs and their course requirements.
Use ONLY this information to recommend specific subjects (courses) from these programs that will
help the student prepare for the target role.

IMPORTANT – Course codes are required:
- For EVERY recommended course you MUST include the official course code (e.g. ACCT 6301, OPRE 6366, MIS 6324, MKT 6301).
- Prefer course code + title pairs found in the extracted catalog list below.
- Format each course as: COURSE_CODE Course Title (example: BUAN 6398 Prescriptive Analytics).
- If the context does not list a code for a course, use the closest match or state "[Code from catalog: check program page]".
- Recommend courses only from programs aligned to the user's pursuit level.
  - If pursuing indicates Masters/MS/MBA, DO NOT include BS courses.
  - If pursuing indicates BS/Bachelor, DO NOT include MS/MBA courses.

For each recommended course, clearly state:
1. Course code (required, e.g. ACCT 6301, OPRE 6366)
2. Course name
3. Which JSOM program it belongs to
4. Why it is relevant for the target role

Focus especially on courses that build the missing skills relative to the target role.

EXTRACTED COURSE CATALOG (code + title from JSOM pages):
{course_catalog}

JSOM PROGRAMS AND COURSES CONTEXT:
{programs_context}

Now provide a concise, structured recommendation:
1. List the most relevant JSOM programs for this role.
2. Under each program, list 3–8 high-impact courses.
3. Each course line MUST be in this exact style: BUAN 6398 Prescriptive Analytics
4. Briefly explain why these courses help the student become a strong candidate for the role.
"""


def main():
    llm = get_llm()

    st.markdown('<h1 class="title">JSOM Smart Advisor</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Tell us what you’re pursuing, upload your resume, and we’ll recommend '
        'JSOM subjects that prepare you for your goal.</p>',
        unsafe_allow_html=True,
    )

    if not llm:
        st.warning(
            "To enable recommendations, add **XAI_API_KEY** (Grok) in Streamlit Cloud "
            "**Settings → Secrets**, or in `config/.env` locally."
        )

    with st.container():

        pursuing = st.text_input(
            "What are you pursuing?",
            placeholder="e.g., Masters in Business Analytics, MS in Data Science, MBA, BS in Finance",
            help="Degree or program you’re interested in (e.g., Masters in Business Analytics).",
        )

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
            if not pursuing.strip():
                st.warning("Please specify what you’re pursuing (e.g., Masters in Business Analytics).")
            elif not resume_file:
                st.warning("Please upload your resume.")
            elif not target_role.strip():
                st.warning("Please enter your target role (for example, 'Data Engineer').")
            elif not llm:
                st.error(
                    "Recommendations are disabled. Set **XAI_API_KEY** (Grok) in Streamlit secrets or config/.env."
                )
            else:
                with st.spinner("Analyzing your resume and JSOM programs..."):
                    resume_text = extract_resume_text(resume_file)
                    skills = extract_skills_from_resume(resume_text)
                    matched_skills, missing_skills = compute_skill_gaps(
                        skills, target_role.strip()
                    )
                    programs_context = fetch_program_context()
                    filtered_context = filter_program_context_by_pursuit(
                        programs_context, pursuing.strip()
                    )
                    course_catalog = extract_course_catalog(filtered_context)

                    prompt = build_recommendation_prompt(
                        pursuing.strip(),
                        skills,
                        target_role.strip(),
                        filtered_context,
                        course_catalog,
                    )

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
                else:
                    st.subheader("Skills detected from your resume")
                    st.write("No clear skills were detected from the uploaded resume.")

                st.subheader("Skill gaps for your target role")
                if missing_skills:
                    st.write(", ".join(missing_skills))
                else:
                    st.write("No major skill gaps detected for the mapped baseline of this role.")

                if matched_skills:
                    st.caption("Skills already aligned with your target role: " + ", ".join(matched_skills))

                st.subheader("Recommended JSOM Subjects for Your Goal")
                st.markdown(answer)

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
