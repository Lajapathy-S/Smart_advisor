"""
Streamlit Frontend Application
JSOM Smart Advisor - Resume-based course recommendation.
"""

import base64
import html
import io
import json
import os
import re
from pathlib import Path
from typing import Any

import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from pypdf import PdfReader

try:
    from src.data_processing.jsom_programs import PROGRAM_URLS
except Exception:
    # Streamlit Cloud can run app.py without package-style imports in some setups.
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
    :root{
        --advisor-green: #154734;
        --advisor-green-2: #0d3528;
        --advisor-orange: #E87500;
        --advisor-orange-2: #c96600;
        --advisor-muted-green: #3D6B58;
        --advisor-peach: #FFF5EE;
        --advisor-bg: #F8F9F9;
        --advisor-text: #0f172a;
        --advisor-muted: #6b7280;
    }
    /* Overall page tone */
    .stApp {
        background: var(--advisor-bg);
        color: var(--advisor-text);
    }
    /* UTD-style top bar */
    .jsom-app-header {
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        box-sizing: border-box;
        background: linear-gradient(90deg, var(--advisor-green) 0%, var(--advisor-green-2) 100%);
        color: #ffffff;
        padding: 14px 22px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.12);
        z-index: 1001;
    }
    .jsom-app-header-inner {
        max-width: 900px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        flex-wrap: wrap;
    }
    .jsom-header-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 0;
    }
    .jsom-logo-tile {
        flex-shrink: 0;
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: rgba(255,255,255,0.12);
        border: 2px solid rgba(232, 117, 0, 0.55);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.72rem;
        letter-spacing: 0.04em;
        line-height: 1.1;
        text-align: center;
    }
    .jsom-header-title {
        font-size: 1.35rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.2;
        color: #ffffff;
    }
    .jsom-header-sub {
        font-size: 0.82rem;
        opacity: 0.92;
        margin: 2px 0 0 0;
        line-height: 1.3;
    }
    .jsom-header-pill {
        flex-shrink: 0;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(232, 117, 0, 0.5);
        padding: 8px 14px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.82rem;
    }
    .jsom-header-pill .jsom-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: var(--advisor-orange);
        box-shadow: 0 0 0 3px rgba(232, 117, 0, 0.25);
    }
    /* Welcome strip (green + orange accent) */
    .jsom-welcome-banner {
        position: relative;
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid rgba(61, 107, 88, 0.22);
        margin: 0 0 1.25rem 0;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
    }
    .jsom-welcome-accent {
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 6px;
        background: linear-gradient(180deg, var(--advisor-green), var(--advisor-orange));
    }
    .jsom-welcome-inner {
        padding: 14px 16px 14px 22px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .jsom-welcome-inner p {
        margin: 0;
        font-size: 0.95rem;
        color: #374151;
        line-height: 1.45;
    }
    .jsom-welcome-ai {
        flex-shrink: 0;
        background: var(--advisor-green);
        color: #fff;
        font-weight: 800;
        font-size: 0.72rem;
        padding: 5px 9px;
        border-radius: 8px;
        letter-spacing: 0.06em;
    }
    .corner-logo {
        position: fixed;
        top: 5.5rem;
        left: 0.75rem;
        width: 120px;
        z-index: 998;
        border-radius: 999px;
        background: #ffffff;
        padding: 4px;
        box-shadow: 0 4px 10px rgba(15, 23, 42, 0.15);
        border: 2px solid rgba(232, 117, 0, 0.45);
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
    /* Main: pill options (white + green border); sidebar: orange CTA */
    section.main .stButton > button,
    section[data-testid="stMain"] .stButton > button {
        width: 100%;
        border-radius: 999px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        background: #ffffff !important;
        color: var(--advisor-green) !important;
        border: 2px solid var(--advisor-muted-green) !important;
    }
    section.main .stButton > button:hover,
    section[data-testid="stMain"] .stButton > button:hover {
        background: var(--advisor-peach) !important;
        border-color: var(--advisor-orange) !important;
        color: var(--advisor-green) !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 999px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        background: var(--advisor-orange) !important;
        color: #ffffff !important;
        border: 2px solid rgba(232, 117, 0, 0.35) !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: var(--advisor-orange-2) !important;
        color: #ffffff !important;
    }
    /* Headings / section labels */
    .stSubheader {
        color: var(--advisor-green);
        font-weight: 800;
    }
    /* Alerts (st.info / st.warning / st.error) */
    .stAlert {
        border-radius: 14px !important;
    }
    .stAlert > div {
        border-left: 6px solid var(--advisor-orange);
        padding-left: 14px;
    }
    /* Green accents on inputs (select/upload) */
    div[data-testid="stSelectbox"] div[role="combobox"],
    div[data-testid="stFileUploader"] section {
        border-radius: 14px !important;
    }
    div[data-testid="stSelectbox"] div[role="combobox"]{
        border: 1px solid rgba(61, 107, 88, 0.35);
        box-shadow: 0 1px 0 rgba(21, 71, 52, 0.06);
    }
    div[data-testid="stSelectbox"] div[role="combobox"]:focus-within{
        border-color: rgba(21, 71, 52, 0.55);
        box-shadow: 0 0 0 3px rgba(61, 107, 88, 0.2);
    }
    div[data-testid="stFileUploader"] section{
        border: 1px dashed rgba(61, 107, 88, 0.4);
        background: rgba(21, 71, 52, 0.04);
    }
    /* Divider */
    hr{
        height: 2px;
        border: 0;
        background: linear-gradient(90deg, rgba(21, 71, 52, 0.9), rgba(232, 117, 0, 0.85));
        border-radius: 999px;
        opacity: 0.9;
    }
    /* Main recommendation card */
    .answer-card{
        background: linear-gradient(180deg, var(--advisor-green) 0%, var(--advisor-green-2) 100%);
        color: #ffffff;
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 10px 24px rgba(21, 71, 52, 0.22);
        border: 1px solid rgba(255,255,255,0.12);
        line-height: 1.45;
        white-space: normal;
        overflow-wrap: anywhere;
    }
    /* Skill Metrics — roadmap alignment bar */
    .skill-metric-wrap {
        border: 1px solid rgba(61, 107, 88, 0.25);
        border-radius: 14px;
        padding: 12px 14px;
        background: #ffffff;
        margin: 0.5rem 0 1rem 0;
    }
    .skill-metric-label {
        font-weight: 800;
        font-size: 1.05rem;
        margin-bottom: 6px;
    }
    .skill-metric-bar {
        height: 12px;
        border-radius: 999px;
        background: #e5e7eb;
        overflow: hidden;
    }
    .skill-metric-fill {
        height: 100%;
        border-radius: 999px;
        transition: width 0.35s ease;
    }
    .skill-metric-caption {
        font-size: 0.82rem;
        color: #6b7280;
        margin-top: 8px;
        line-height: 1.35;
    }
    /* Semester flowchart (recommended courses) */
    .semester-flow {
        display: flex;
        flex-direction: row;
        flex-wrap: nowrap;
        align-items: flex-start;
        justify-content: flex-start;
        overflow-x: auto;
        gap: 0;
        padding: 12px 4px 20px 4px;
        margin: 8px 0 16px 0;
        -webkit-overflow-scrolling: touch;
    }
    .semester-col {
        flex: 0 0 auto;
        min-width: 132px;
        max-width: 168px;
    }
    .semester-title {
        font-weight: 800;
        font-size: 0.78rem;
        color: var(--advisor-green);
        text-align: center;
        margin-bottom: 8px;
        padding: 4px 6px;
        background: rgba(21, 71, 52, 0.08);
        border-radius: 8px;
        border: 1px solid rgba(61, 107, 88, 0.25);
    }
    .semester-arrow {
        flex: 0 0 auto;
        align-self: center;
        padding: 0 6px;
        font-size: 1.35rem;
        color: var(--advisor-orange);
        font-weight: 700;
        user-select: none;
    }
    .course-box {
        border: 2px solid var(--advisor-green);
        border-radius: 10px;
        padding: 8px 6px;
        margin: 0 0 8px 0;
        background: #ffffff;
        font-size: 0.72rem;
        line-height: 1.25;
        text-align: center;
        color: #0f172a;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.06);
    }
    .course-box.empty {
        border-style: dashed;
        opacity: 0.55;
        color: #6b7280;
    }
    /* Chatbot layout */
    /* Chat bubbles (Streamlit) */
    [data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 1px solid rgba(61, 107, 88, 0.32) !important;
        border-radius: 16px !important;
        padding: 6px 10px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
    }
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
        border-radius: 12px;
    }
    .chat-shell {
        max-width: 760px;
        margin: 0 auto 1.25rem auto;
        border: 1px solid rgba(61, 107, 88, 0.22);
        border-radius: 16px;
        padding: 12px 14px 16px 14px;
        background: #ffffff;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }
    p.chat-option-hint {
        font-size: 0.9rem;
        color: #374151;
        margin: 0.5rem 0 0.75rem 0;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)

logo_path = project_root / "assets" / "comet-smart-advisor.png"
if logo_path.exists():
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
    st.markdown(
        f'<img src="data:image/png;base64,{logo_b64}" class="corner-logo" alt="Comet Smart Advisor logo" />',
        unsafe_allow_html=True,
    )

PURSUIT_OPTIONS = [
    "MS Accounting",
    "MS Business Analytics",
    "MS ITM",
    "Master of Science in Energy Management",
    "Master of Science in Finance",
    "Master of Science in Financial Technology and Analytics",
    "Master of Science in Healthcare Leadership and Management",
    "Master of Science in International Management Studies",
    "Master of Science in Management Science",
    "Master of Science in Marketing",
    "Master of Science in Supply Chain Management",
    "MS in Systems Engineering and Management",
    "Bachelor of Science in Accounting",
    "Bachelor of Science in Business Administration",
    "Bachelor of Science in Business Analytics and Artificial Intelligence",
    "Bachelor of Science in Computer Information Systems and Technology",
    "Bachelor of Science in Cybersecurity and Risk Management",
    "Bachelor of Science in Finance",
    "Bachelor of Science in Healthcare Management",
    "Bachelor of Science in Human Resource Management",
    "Bachelor of Science in Marketing",
    "Bachelor of Science in Supply Chain Management and Analytics",
    "Master of Business Administration",
]

# Display text -> program key in PROGRAM_URLS
PURSUIT_TO_PROGRAM = {
    "MS Accounting": "MS Accounting",
    "MS Business Analytics": "MS Business Analytics",
    "MS ITM": "MS Information Technology Management",
    "Master of Science in Energy Management": "MS Energy Management",
    "Master of Science in Finance": "MS Finance",
    "Master of Science in Financial Technology and Analytics": "MS Financial Technology and Analytics",
    "Master of Science in Healthcare Leadership and Management": "MS Healthcare Leadership and Management",
    "Master of Science in International Management Studies": "MS International Management Studies",
    "Master of Science in Management Science": "MS Management Science",
    "Master of Science in Marketing": "MS Marketing",
    "Master of Science in Supply Chain Management": "MS Supply Chain Management",
    "MS in Systems Engineering and Management": "MS Systems Engineering and Management",
    "Bachelor of Science in Accounting": "BS Accounting",
    "Bachelor of Science in Business Administration": "BS Business Administration",
    "Bachelor of Science in Business Analytics and Artificial Intelligence": "BS Business Analytics and AI",
    "Bachelor of Science in Computer Information Systems and Technology": "BS Computer Information Systems and Technology",
    "Bachelor of Science in Cybersecurity and Risk Management": "BS Cybersecurity and Risk Management",
    "Bachelor of Science in Finance": "BS Finance",
    "Bachelor of Science in Healthcare Management": "BS Healthcare Management",
    "Bachelor of Science in Human Resource Management": "BS Human Resource Management",
    "Bachelor of Science in Marketing": "BS Marketing",
    "Bachelor of Science in Supply Chain Management and Analytics": "BS Supply Chain Management and Analytics",
    "Master of Business Administration": "MBA",
}

CAREER_PATH_OPTIONS = [
    "frontend",
    "Devops",
    "AI engineer",
    "Android",
    "IOS",
    "Software architect",
    "Technical writer",
    "MLops",
    "Developer relations",
    "Backend",
    "Devsecops",
    "AI and data scientist",
    "Machine learning",
    "Blockcchain",
    "Cybersecurity",
    "Game Developer",
    "Product Manager",
    "BI Analyst",
    "Full stack",
    "Data Analyst",
    "Data Engineer",
    "PostgreSQL",
    "QA",
    "UX Design",
    "server side game developer",
    "Engineering Manager",
]


@st.cache_resource(show_spinner=False)
def get_llm():
    """
    Return Claude (Anthropic) model if ANTHROPIC_API_KEY is set.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    # Claude 3.5 Sonnet IDs were retired (see Anthropic model deprecations); default to current Sonnet.
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    try:
        return ChatAnthropic(
            model=model,
            temperature=0.4,
            max_retries=2,
            anthropic_api_key=api_key,
        )
    except Exception:
        return None


# Community roadmaps (developer-roadmap JSON on GitHub)
ROADMAP_JSON_BASE = (
    "https://raw.githubusercontent.com/kamranahmedse/developer-roadmap/master/"
    "src/data/roadmaps/{slug}/{slug}.json"
)

# Labels in the JSON include many curriculum / spreadsheet leaf nodes — drop those for skill gaps.
ROADMAP_LABEL_DROP_EXACT = frozenset(
    {
        "optional",
        "pick a language",
        "learn the basics",
        "learn basics",
        "version control systems",
        "what is",
        "roadmap",
        "roadmap.sh",
        # Stats / spreadsheet function noise common on data-analyst style roadmaps
        "mean",
        "median",
        "mode",
        "range",
        "variance",
        "skewness",
        "kurtosis",
        "dispersion",
        "trim",
        "concat",
        "count",
        "datedif",
        "min",
        "max",
        "min / max",
        "min/max",
        "naive byes",
        # Generic section / viz UI labels
        "heatmap",
        "charting",
        "histogram",
        "histograms",
        "pie charts",
        "pie chart",
        "introduction",
        "exploration",
        "visualisation",
        "visualization",
        "libraries",
        "frameworks",
        "collection",
        "cleanup",
        "web scraping",
        "chart",
        "charts",
    }
)


def _normalize_roadmap_label_key(raw: str) -> str:
    t = raw.strip().lower()
    t = re.sub(r"\s+", " ", t)
    t = t.replace("min/max", "min / max")
    return t


def _is_noisy_roadmap_label(label: str) -> bool:
    """True if this JSON node label is too generic to show as a skill gap."""
    key = _normalize_roadmap_label_key(label)
    if not key or len(key) < 2:
        return True
    if "roadmap.sh" in key or key.endswith(".sh"):
        return True
    if key in ROADMAP_LABEL_DROP_EXACT:
        return True
    if key.startswith("what is ") or key.startswith("learn ") or key.startswith("pick "):
        return True
    # Single generic token (e.g. COUNT, Range) — already in DROP_EXACT for most
    tokens = [w for w in re.findall(r"[a-z0-9]+", key) if len(w) > 1]
    if len(tokens) == 1 and tokens[0] in ROADMAP_LABEL_DROP_EXACT:
        return True
    return False


# Catalog pages often have a very long faculty block before "Course Requirements"; a small
# slice misses almost all course codes and the model (or fallback) can only see one course.
_COURSE_SECTION_MARKERS = (
    "Course Requirements",
    "Course requirements",
    "Degree Requirements",
    "degree requirements",
    "Required courses:",
    "Core Courses:",
    "Core courses:",
)
_PROGRAM_PAGE_MAX_CHARS = 52000


def _clip_program_page_text(raw: str, max_chars: int = _PROGRAM_PAGE_MAX_CHARS) -> str:
    """Prefer text from degree/course sections so scraping isn't dominated by faculty lists."""
    if not raw or len(raw) <= max_chars:
        return raw[:max_chars] if len(raw) > max_chars else raw
    best_start = -1
    for marker in _COURSE_SECTION_MARKERS:
        idx = raw.find(marker)
        if idx >= 0 and (best_start < 0 or idx < best_start):
            best_start = idx
    if best_start > 1500:
        raw = raw[best_start:]
    return raw[:max_chars]


@st.cache_resource(show_spinner=False)
def fetch_program_context(program_subset: dict[str, str] | None = None) -> str:
    """
    Fetch and lightly clean text from JSOM program URLs.
    If program_subset is provided, only those (name -> url) are fetched.
    """
    mapping = program_subset if program_subset is not None else PROGRAM_URLS
    parts = []
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; JSOM-Smart-Advisor/1.0)"
    }
    for name, url in mapping.items():
        try:
            resp = requests.get(url, timeout=20, headers=headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            main = soup.find("main") or soup.body or soup
            text = " ".join(main.stripped_strings)
            text = _clip_program_page_text(text, _PROGRAM_PAGE_MAX_CHARS)
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


def _first_course_code_token(text: str) -> str | None:
    m = re.search(r"\b([A-Z]{2,5})\s*(\d{4})\b", (text or "").upper())
    if not m:
        return None
    return f"{m.group(1)} {m.group(2)}"


_TRANSCRIPT_CODE_RE = re.compile(r"\b([A-Z]{2,5})\s*(\d{4})\b")


def _pick_richer_course_title(a: str, b: str) -> str:
    """Prefer the longer, more complete title (transcript vs catalog); ties favor catalog."""
    a = _truncate_title_at_extra_course_listing((a or "").strip())
    b = _truncate_title_at_extra_course_listing((b or "").strip())
    if not a:
        return b
    if not b:
        return a
    if len(b) > len(a):
        return b
    if len(a) > len(b):
        return a
    return b


_DEGREE_PAGE_PROSE_TAIL = re.compile(
    r"\.\s+(In addition|Students who|Students must|Prerequisite|Prerequisites|Knowledge of|"
    r"This course|For students|Note that|Approval of|Concurrent enrollment|"
    r"May be used to satisfy)",
    re.I,
)


def _strip_elective_requirements_noise(tit: str) -> str:
    """
    Catalog HTML often concatenates a course title with degree-plan prose on one line, e.g.
    '...Data Science Elective Courses: 18 semester credit hours Students may choose any course
    with a BUAN prefix'. Strip that tail so search/transcript titles stay clean and core courses
    are not mis-tagged as electives by substring heuristics.
    """
    t = (tit or "").strip()
    if not t:
        return t
    low = t.lower()
    cut = low.find("elective courses:")
    if cut > 8:
        t = t[:cut].rstrip(" -,;:|/")
    low = t.lower()
    cut = low.find("students may choose")
    if cut > 12:
        t = t[:cut].rstrip(" -,;:|/")
    low = t.lower()
    # Credit-hour boilerplate without an "Elective Courses:" header (merged table cells)
    m = re.search(
        r"\s+\d{1,2}\s+semester credit hours?\s+students may choose\b",
        low,
    )
    if m and m.start() > 12:
        t = t[: m.start()].rstrip(" -,;:|/")
    return t.strip()


def _clean_advisor_answer_for_display(text: str) -> str:
    """Remove catalog degree-plan tails from lines that contain a subject code (LLM may echo them)."""
    if not (text or "").strip():
        return text or ""
    code_in_line = re.compile(r"\b[A-Z]{2,5}\s*\d{4}\b")
    out: list[str] = []
    for line in text.splitlines():
        if code_in_line.search(line):
            out.append(_strip_elective_requirements_noise(line))
        else:
            out.append(line)
    return "\n".join(out)


def _strip_catalog_prose_suffix(tit: str) -> str:
    """Cut degree-page boilerplate that often follows a course name on one HTML line."""
    t = (tit or "").strip()
    m = _DEGREE_PAGE_PROSE_TAIL.search(t)
    if m and m.start() > 12:
        t = t[: m.start() + 1].strip()
    return _strip_elective_requirements_noise(t)


def _truncate_title_at_extra_course_listing(title: str) -> str:
    """
    If a title string still contains another SUBJECT #### token (e.g. merged HTML line),
    cut before the first extra listing. Keeps lone references like “prerequisite CS 6310”
    when only one token appears and the prefix is short.
    """
    t = (title or "").strip()
    if not t:
        return ""
    matches = list(_TRANSCRIPT_CODE_RE.finditer(t.upper()))
    if len(matches) >= 2:
        return t[: matches[0].start()].rstrip(" -,;:|/")
    if len(matches) == 1:
        prefix = t[: matches[0].start()].strip()
        if len(prefix) >= 18:
            return prefix.rstrip(" -,;:|/")
    return t


def _title_fragment_after_code_on_line(remainder: str) -> str:
    """Title text from the rest of a program-page or catalog line after a course code match."""
    if not remainder or not remainder.strip():
        return ""
    rem = remainder.strip()
    # Same line often lists several courses; never include text after the next code.
    nm = _TRANSCRIPT_CODE_RE.search(rem.upper())
    if nm:
        rem = rem[: nm.start()].rstrip(" -:|,")
    for stop in (" (", " — ", "\t", "|", ";"):
        if stop in rem:
            rem = rem.split(stop)[0]
    tit = re.sub(r"\s+", " ", rem).strip()
    if len(tit) > 140:
        tit = tit[:140].rsplit(" ", 1)[0]
    tit = _strip_catalog_prose_suffix(tit)
    return _truncate_title_at_extra_course_listing(tit)


def _infer_title_from_transcript_tail(tail: str) -> str:
    """Best-effort course title from text after a course code on a transcript line.

    PDF extractors often use wide spacing between columns. Do not take only the first
    whitespace-delimited “column” after the code — that yields a single word. Keep the
    full remainder and strip trailing credits and grade fields only.
    """
    if not tail or not tail.strip():
        return ""
    s = tail.strip()
    s = re.sub(r"^[\-–—:\|]\s*", "", s)
    # Whole remainder can be a lone credits cell — reject
    if re.fullmatch(r"\d{1,2}\.\d{2,4}|[A-F][+-]?|P|CR|W|I|IP", s, re.I):
        return ""
    # Strip trailing tabular junk: repeated passes for credit hours + letter grade etc.
    while True:
        prev = s
        s = re.sub(r"\s+\d{1,2}\.\d{2,4}\s*[A-F][+-]?\s*$", "", s, flags=re.I)
        s = re.sub(r"\s+\d{1,2}\.\d{2,4}\s*$", "", s)
        s = re.sub(r"\s+[A-F][+-]?\s*$", "", s, flags=re.I)
        s = re.sub(r"\s+(?:P|CR|NC|W|I|IP|S|U)\s*$", "", s, flags=re.I)
        if s == prev:
            break
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > 160:
        s = s[:160].rsplit(" ", 1)[0]
    s = _strip_catalog_prose_suffix(s)
    return _truncate_title_at_extra_course_listing(s)


def parse_transcript_course_entries(text: str) -> list[tuple[str, str]]:
    """
    Extract unique (course code, title) pairs from transcript text, in first-seen order.
    Title is parsed from the remainder of the same line; may be empty if not detected.
    """
    if not (text or "").strip():
        return []
    titles: dict[str, str] = {}
    order: list[str] = []
    for line in text.splitlines():
        line_r = line.rstrip()
        if not line_r.strip():
            continue
        lu = line_r.upper()
        for m in _TRANSCRIPT_CODE_RE.finditer(lu):
            code = f"{m.group(1)} {m.group(2)}"
            tail = line_r[m.end() :]
            nm = _TRANSCRIPT_CODE_RE.search(tail.upper())
            if nm:
                tail = tail[: nm.start()]
            title = _infer_title_from_transcript_tail(tail)
            if code not in titles:
                titles[code] = title
                order.append(code)
            elif title and not (titles.get(code) or "").strip():
                titles[code] = title
    return [(c, titles[c]) for c in order]


def supplement_titles_from_program_text(
    programs_context: str, entries: list[tuple[str, str]]
) -> list[tuple[str, str]]:
    """
    Merge transcript titles with CODE/title fragments from scraped JSOM program context.
    Prefers the longer, more complete string so short PDF fragments (e.g. “Database”)
    are replaced by full catalog-style titles when available.
    """
    if not entries:
        return entries
    from_lines: dict[str, str] = {}
    pat = re.compile(r"\b([A-Z]{2,5})\s*(\d{4})\b")
    for line in programs_context.splitlines():
        for m in pat.finditer(line):
            code_u = f"{m.group(1)} {m.group(2)}".upper()
            rem = line[m.end() :].strip(" -:|,")
            tit = _title_fragment_after_code_on_line(rem) if rem else ""
            if tit and code_u not in from_lines:
                from_lines[code_u] = tit
    if not from_lines:
        return entries
    out: list[tuple[str, str]] = []
    for code, tit in entries:
        sup = from_lines.get(code.upper(), "")
        merged = _pick_richer_course_title(tit, sup)
        out.append((code, merged))
    return out


def merge_transcript_titles_with_course_catalog_blob(
    course_catalog: str, entries: list[tuple[str, str]]
) -> list[tuple[str, str]]:
    """
    Refine titles using `extract_course_catalog` lines: ``- CODE Full Title (Program)``.
    Picks the richer of transcript vs catalog per code.
    """
    if not (course_catalog or "").strip() or not entries:
        return entries
    from_cat: dict[str, str] = {}
    for line in course_catalog.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        rest = line[2:].strip()
        if not rest.endswith(")"):
            continue
        inner = rest[:-1]
        idx = inner.rfind(" (")
        if idx == -1:
            continue
        head = inner[:idx].strip()
        m = re.match(r"^([A-Z]{2,5})\s+(\d{4})\s+(.+)$", head)
        if not m:
            continue
        code_u = f"{m.group(1)} {m.group(2)}".upper()
        tit = (m.group(3) or "").strip()
        tit = _strip_catalog_prose_suffix(tit)
        tit = _truncate_title_at_extra_course_listing(tit)
        if tit and code_u not in from_cat:
            from_cat[code_u] = tit
    if not from_cat:
        return entries
    return [
        (c, _pick_richer_course_title(t, from_cat.get(c.upper(), ""))) for c, t in entries
    ]


def extract_completed_courses_from_transcript(text: str) -> list[str]:
    """
    Parse transcript text and return completed course code tokens (e.g., BUAN 6320).
    """
    return [c for c, _ in parse_transcript_course_entries(text)]


def estimate_completed_semesters_from_transcript(
    transcript_text: str, completed_courses: list[str]
) -> int:
    """
    Estimate semesters completed using explicit 'Term:' markers; fallback to course-count heuristic.
    """
    t = transcript_text or ""
    markers = re.findall(r"\bterm\s*:", t, flags=re.IGNORECASE)
    if markers:
        return max(0, len(markers))
    # Fallback heuristic: roughly 4 completed courses per term.
    return max(0, len(completed_courses) // 4)


def looks_like_transcript_text(text: str) -> bool:
    """
    Heuristic guard to catch resume files uploaded in transcript step.
    """
    t = (text or "").strip()
    if not t:
        return False
    upper = t.upper()
    code_count = len(
        {f"{m.group(1)} {m.group(2)}" for m in _TRANSCRIPT_CODE_RE.finditer(upper)}
    )
    transcript_kw = len(
        re.findall(
            r"\b(transcript|term|semester|gpa|grade|credit|credits|coursework|completed|enrolled)\b",
            t,
            flags=re.IGNORECASE,
        )
    )
    resume_kw = len(
        re.findall(
            r"\b(experience|skills|summary|objective|project|intern|linkedin)\b",
            t,
            flags=re.IGNORECASE,
        )
    )

    if code_count >= 3:
        return True
    if code_count >= 2 and transcript_kw >= 2:
        return True
    if code_count >= 1 and transcript_kw >= 3 and resume_kw == 0:
        return True
    return False


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
        "pandas",
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


SKILLS_LLM_MAX_RESUME_CHARS = 14_000


def _skill_dedupe_key(s: str) -> str:
    return re.sub(r"[^a-z0-9+#./ ]", "", (s or "").lower()).strip()


def skill_evidence_in_resume(skill: str, resume_text: str) -> bool:
    """True if the resume text plausibly supports this skill (anti-hallucination for LLM path)."""
    s = (skill or "").strip()
    if not s or len(s) > 80:
        return False
    lower = resume_text.lower()
    sl = s.lower().strip()
    if not sl:
        return False
    if len(sl) >= 4 and sl in lower:
        return True
    compact_r = re.sub(r"[^a-z0-9]", "", lower)
    compact_s = re.sub(r"[^a-z0-9]", "", sl)
    if len(compact_s) >= 4 and compact_s in compact_r:
        return True
    try:
        return (
            re.search(rf"(?<![a-z0-9]){re.escape(sl)}(?![a-z0-9])", lower)
            is not None
        )
    except re.error:
        return sl in lower


def _extract_first_json_array(text: str) -> str | None:
    start = text.find("[")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _parse_json_skill_array(raw: str) -> list[str]:
    text = (raw or "").strip()
    if not text:
        return []
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    chunk = _extract_first_json_array(text)
    if not chunk:
        return []
    try:
        data = json.loads(chunk)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    out: list[str] = []
    for item in data:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def extract_skills_from_resume_llm(llm: Any, resume_text: str) -> list[str]:
    """LLM pass: JSON skill list, kept only when grounded in resume text."""
    if not llm or not (resume_text or "").strip():
        return []
    clip = resume_text[:SKILLS_LLM_MAX_RESUME_CHARS]
    prompt = f"""You extract professional skills from a resume. Use ONLY the resume text below.

Rules:
- Include tools, languages, platforms, methods, and soft skills clearly supported by the text (stated or clearly implied by named work, tools, metrics, or responsibilities).
- Use short canonical labels (e.g. "Python", "SQL", "Agile", "Stakeholder communication").
- Do NOT list employers, schools, or cities as skills. Do NOT invent skills with no support in the text.
- At most 35 skills; prefer precision over quantity.

Output ONLY a JSON array of strings. No markdown fences, no object wrapper, no commentary.

RESUME TEXT:
{clip}
"""
    try:
        response = llm.invoke(prompt)
        raw = response.content if hasattr(response, "content") else str(response)
    except Exception:
        return []
    candidates = _parse_json_skill_array(raw)
    merged_raw: list[str] = []
    seen_raw: set[str] = set()
    for c in candidates:
        if not skill_evidence_in_resume(c, resume_text):
            continue
        key = _skill_dedupe_key(c)
        if not key or len(key) < 2:
            continue
        if key not in seen_raw:
            seen_raw.add(key)
            merged_raw.append(c)
    final_skills: list[str] = []
    seen = set()
    for s in merged_raw:
        s_clean = re.sub(r"[^a-z0-9+#./ ]", "", s.lower()).strip()
        if 2 <= len(s_clean) <= 40 and s_clean not in seen:
            seen.add(s_clean)
            final_skills.append(s_clean)
    return final_skills


def extract_skills_hybrid(llm: Any | None, resume_text: str) -> list[str]:
    """Heuristic keyword/skill-section extraction, merged with LLM extraction when llm is available."""
    heuristic = extract_skills_from_resume(resume_text)
    if llm is None:
        return heuristic
    llm_skills = extract_skills_from_resume_llm(llm, resume_text)
    if not llm_skills:
        return heuristic
    keys = {_skill_dedupe_key(s) for s in heuristic}
    out = list(heuristic)
    for s in llm_skills:
        k = _skill_dedupe_key(s)
        if k and k not in keys:
            keys.add(k)
            out.append(s)
    return out


def _infer_program_level(pursuing: str) -> str:
    text = pursuing.lower()
    if any(k in text for k in ["master", "masters", "ms ", "m.s", "mba", "graduate"]):
        return "graduate"
    if any(k in text for k in ["bachelor", "bachelors", "bs ", "b.s", "undergraduate"]):
        return "undergraduate"
    return "unknown"


def match_pursuing_to_programs(pursuing: str) -> tuple[dict[str, str], str | None]:
    """
    Map free-text pursuit to the closest single JSOM program in PROGRAM_URLS.
    Returns {program_name: url} with one entry when confident, plus optional warning.
    """
    raw = (pursuing or "").strip()
    if not raw:
        return dict(PROGRAM_URLS), "Add a clearer program name to scope results to one degree."

    # Direct mapping from dropdown option to a single JSOM program
    if raw in PURSUIT_TO_PROGRAM:
        program_name = PURSUIT_TO_PROGRAM[raw]
        return {program_name: PROGRAM_URLS[program_name]}, None

    level = _infer_program_level(raw)
    p = raw.lower()

    candidates: list[tuple[str, str]] = []
    for name, url in PROGRAM_URLS.items():
        if level == "graduate":
            if not (name.startswith("MS ") or name == "MBA"):
                continue
        elif level == "undergraduate":
            if not name.startswith("BS "):
                continue
        candidates.append((name, url))

    if not candidates:
        candidates = list(PROGRAM_URLS.items())

    # MBA-only shortcut
    if level == "graduate" and re.search(r"\bmba\b", p):
        other_signals = bool(
            re.search(
                r"\b(analytics|finance|marketing|accounting|supply|itm|technology|fintech|healthcare|energy)\b",
                p,
            )
        )
        if not other_signals:
            return {"MBA": PROGRAM_URLS["MBA"]}, None

    stop = frozenset(
        {
            "in",
            "of",
            "the",
            "a",
            "an",
            "and",
            "or",
            "to",
            "for",
            "program",
            "programs",
            "degree",
            "degrees",
            "master",
            "masters",
            "msc",
            "ms",
            "mba",
            "bs",
            "bsc",
            "bachelor",
            "bachelors",
            "undergraduate",
            "graduate",
            "at",
            "ut",
            "dallas",
            "jsom",
            "utd",
            "university",
        }
    )
    pursuit_tokens = {t for t in re.findall(r"[a-z0-9]+", p) if t not in stop and len(t) > 1}

    best_score = -1
    best: list[tuple[str, str]] = []

    for name, url in candidates:
        core = re.sub(r"^(MS|BS)\s+", "", name, flags=re.I).strip()
        if name == "MBA":
            core = "mba"
        name_tokens = {
            t
            for t in re.findall(r"[a-z0-9]+", core.lower())
            if t not in stop and len(t) > 1
        }
        score = len(name_tokens & pursuit_tokens)
        if score > best_score:
            best_score = score
            best = [(name, url)]
        elif score == best_score and score >= 0:
            best.append((name, url))

    if best_score <= 0:
        warn = (
            "Could not match your text to a specific JSOM program. "
            "Try wording closer to the catalog (e.g. 'MS Business Analytics'). "
            "Using all programs at your level for now."
        )
        return dict(candidates), warn

    if len(best) > 1:
        compact = re.sub(r"[^a-z0-9]", "", p)
        exact = [pair for pair in best if re.sub(r"[^a-z0-9]", "", pair[0].lower()) in compact]
        if len(exact) == 1:
            best = exact
        else:
            best = sorted(best, key=lambda x: (-len(x[0]), x[0]))[:1]

    name, url = best[0]
    return {name: url}, None


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


def roadmap_slug_for_target_role(target_role: str) -> str | None:
    """Map user target role to a roadmap.sh / developer-roadmap slug."""
    role = target_role.lower().strip()
    pairs: list[tuple[str, str]] = [
        ("data engineer", "data-engineer"),
        ("data engineering", "data-engineer"),
        ("data analyst", "data-analyst"),
        ("business intelligence", "bi-analyst"),
        ("bi analyst", "bi-analyst"),
        ("business analyst", "data-analyst"),
        ("machine learning", "machine-learning"),
        ("mlops", "mlops"),
        ("ai and data scientist", "ai-data-scientist"),
        ("ml engineer", "machine-learning"),
        ("ai engineer", "ai-engineer"),
        ("software engineer", "backend"),
        ("software architect", "software-architect"),
        ("backend developer", "backend"),
        ("backend", "backend"),
        ("full stack", "full-stack"),
        ("frontend", "frontend"),
        ("devops", "devops"),
        ("devsecops", "devsecops"),
        ("developer relations", "devrel"),
        ("technical writer", "technical-writer"),
        ("android", "android"),
        ("ios", "ios"),
        ("game developer", "game-developer"),
        ("server side game developer", "server-side-game-developer"),
        ("blockcchain", "blockchain"),
        ("cyber security", "cyber-security"),
        ("cybersecurity", "cyber-security"),
        ("product manager", "product-manager"),
        ("engineering manager", "engineering-manager"),
        ("postgresql", "postgresql"),
        ("qa", "qa"),
        ("ux design", "ux-design"),
        ("cloud", "aws"),
        ("aws", "aws"),
    ]
    for needle, slug in pairs:
        if needle in role:
            return slug
    return None


def _collect_roadmap_labels(obj: Any, out: set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("label", "name", "title") and isinstance(v, str):
                t = v.strip()
                if t:
                    out.add(t)
            else:
                _collect_roadmap_labels(v, out)
    elif isinstance(obj, list):
        for item in obj:
            _collect_roadmap_labels(item, out)


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_roadmap_labels(roadmap_slug: str) -> list[str]:
    """Load topic labels from the public developer-roadmap JSON behind roadmap.sh."""
    url = ROADMAP_JSON_BASE.format(slug=roadmap_slug)
    try:
        resp = requests.get(
            url,
            timeout=25,
            headers={"User-Agent": "Mozilla/5.0 (compatible; JSOM-Smart-Advisor/1.0)"},
        )
        resp.raise_for_status()
        data = json.loads(resp.text)
    except Exception:
        return []

    found: set[str] = set()
    _collect_roadmap_labels(data, found)

    cleaned: list[str] = []
    for s in found:
        sl = s.lower().strip()
        if len(sl) < 3 or len(s) > 85 or _is_noisy_roadmap_label(s):
            continue
        cleaned.append(s)

    # De-dupe case-insensitively while keeping readable capitalization
    seen: set[str] = set()
    out: list[str] = []
    for s in sorted(cleaned, key=len):
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out[:220]


def compute_skill_gaps(
    resume_text: str,
    resume_skills: list[str],
    target_role: str,
) -> tuple[list[str], list[str], str | None, str]:
    """
    Compare resume against roadmap.sh topic labels when possible.
    Returns (matched_topics, missing_topics, roadmap_slug | None, source_note).
    """
    slug = roadmap_slug_for_target_role(target_role)
    if slug:
        topics = fetch_roadmap_labels(slug)
    else:
        topics = []

    if not topics:
        expected = infer_target_role_skills(target_role)
        resume_set = {s.lower().strip() for s in resume_skills}
        matched = [s for s in expected if s in resume_set]
        missing = [s for s in expected if s not in resume_set]
        return (
            matched,
            missing,
            None,
            "Using a built-in topic baseline for this role. Pick a career path that has a detailed topic checklist for richer gaps.",
        )

    blob = f"{(resume_text or '')} {' '.join(resume_skills)}".lower()
    matched_topics: list[str] = []
    missing_topics: list[str] = []

    for lab in topics:
        ln = lab.lower()
        words = [w for w in re.findall(r"[a-z0-9]+", ln) if len(w) > 2]
        if not words:
            continue
        if ln in blob:
            matched_topics.append(lab)
            continue
        hits = sum(1 for w in words if w in blob)
        need = max(1, min(2, (len(words) + 1) // 2))
        if hits >= need:
            matched_topics.append(lab)
        else:
            missing_topics.append(lab)

    # Keep UI readable
    missing_topics = missing_topics[:40]
    matched_topics = matched_topics[:35]
    note = (
        f"Compared your resume to the public role-topic checklist "
        f"`{slug}` (open-source JSON, developer-roadmap project)."
    )
    return matched_topics, missing_topics, slug, note


def skill_metrics_alignment(
    matched: list[str],
    missing: list[str],
    roadmap_slug: str | None,
) -> dict[str, Any]:
    """
    Skill Alignment Metrics: how much the resume aligns with expected roadmap-style topics
    (same topic lists used in Skill gaps). Returns percent 0–100 and RAG-style zone color.
    """
    m_count = len(matched or [])
    miss_count = len(missing or [])
    total = m_count + miss_count
    if total == 0:
        return {
            "percent": None,
            "color": "#6b7280",
            "zone": "na",
            "label": "No topics compared",
            "source": "roadmap" if roadmap_slug else "baseline",
        }
    pct = int(round(100.0 * m_count / total))
    if pct >= 55:
        color, zone = "#16a34a", "high"
    elif pct >= 30:
        color, zone = "#ca8a04", "mid"
    else:
        color, zone = "#dc2626", "low"
    return {
        "percent": pct,
        "color": color,
        "zone": zone,
        "label": f"{pct}% aligned",
        "matched": m_count,
        "missing": miss_count,
        "source": "roadmap" if roadmap_slug else "baseline",
    }


def render_skill_metrics_block(
    metrics: dict[str, Any],
    *,
    transcript_uploaded: bool = False,
    transcript_course_entries: list[tuple[str, str]] | None = None,
    completed_semesters: int = 0,
) -> None:
    """Streamlit + HTML: color-coded alignment bar (Skill Alignment Metrics)."""
    st.subheader("Skill Alignment Metrics")
    pct = metrics.get("percent")
    color = metrics.get("color", "#6b7280")
    src = metrics.get("source", "roadmap")
    if pct is None:
        st.markdown(
            f"""
<div class="skill-metric-wrap">
  <div class="skill-metric-label" style="color:{html.escape(color)};">{html.escape(metrics.get("label", "—"))}</div>
  <p class="skill-metric-caption">Run with a career path that loads a roadmap topic list to see a red / yellow / green alignment score.</p>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        src_note = (
            "Compared against the public developer-roadmap JSON for this role (same topic family as roadmap.sh)."
            if src == "roadmap"
            else "Compared against a small built-in skill baseline for this role (no roadmap JSON loaded)."
        )
        st.markdown(
            f"""
<div class="skill-metric-wrap">
  <div class="skill-metric-label" style="color:{html.escape(color)};">{html.escape(metrics.get("label", ""))}</div>
  <div class="skill-metric-bar"><div class="skill-metric-fill" style="width:{int(pct)}%;background:{html.escape(color)};"></div></div>
  <p class="skill-metric-caption">{html.escape(src_note)} Green ≥55%, yellow 30–54%, red &lt;30% (of topics checked vs your resume).</p>
</div>
""",
            unsafe_allow_html=True,
        )

    entries = list(transcript_course_entries or [])
    if transcript_uploaded:
        st.markdown("##### Courses detected from your transcript")
        st.caption(
            "Course codes are parsed from the file; titles come from the transcript line when "
            "possible, otherwise from the JSOM program page text when the code appears there. "
            "Confirm against your official record."
        )
        if entries:
            lines: list[str] = []
            for code, title in entries:
                title = (title or "").strip()
                if title:
                    lines.append(
                        f"- **{html.escape(code)}** — {html.escape(title)}"
                    )
                else:
                    lines.append(
                        f"- **{html.escape(code)}** — "
                        f"*title not detected—verify on your transcript*"
                    )
            st.markdown("\n".join(lines))
            st.caption(
                f"Heuristic estimate of completed semesters: **{completed_semesters}** "
                f"({len(entries)} course(s))."
            )
        else:
            st.info(
                "No course codes in that form were found, so recommendations will not filter "
                "out completed courses."
            )


def extract_course_catalog(programs_context: str) -> str:
    """
    Extract course code + title pairs from scraped program text.
    This helps ground the LLM output in authentic catalog entries.
    """
    # Course codes: BUAN 6398, MIS 6324, BUAN6398 (catalog HTML varies)
    code_pattern = re.compile(
        r"\b([A-Z]{2,5})\s*(\d{4})\b"
    )

    entries: list[str] = []
    seen = set()
    current_program = "Unknown Program"

    for line in programs_context.splitlines():
        if line.startswith("PROGRAM:"):
            current_program = line.replace("PROGRAM:", "", 1).strip() or "Unknown Program"
            continue

        for match in code_pattern.finditer(line):
            code = f"{match.group(1)} {match.group(2)}"
            remainder = line[match.end() :].strip(" -:|,")
            title = _title_fragment_after_code_on_line(remainder) if remainder else ""

            if not title:
                # Code present but no title fragment (common in dense HTML) — still ground the LLM
                title = "course (title on program page — verify exact wording)"

            key = (code, title.lower(), current_program)
            if key in seen:
                continue
            seen.add(key)
            entries.append(f"- {code} {title} ({current_program})")

    # Keep prompt concise while still giving enough grounded options
    return "\n".join(entries[:250])


DEFAULT_NO_COURSE_MESSAGE = (
    "Thanks for your selections. We couldn’t load enough text from the JSOM program page. "
    "Please try again later or open the official program page from the UT Dallas catalog."
)


def career_program_alignment_hint(program_name: str, career: str) -> str:
    """
    Explicit alignment hints so the model does not return NO_MATCH for obvious fits
    (e.g. MS Business Analytics + Data Analyst) when HTML scraping omits course-code patterns.
    """
    p = program_name.lower()
    c = career.lower()
    # Analytics / data careers + analytics degrees
    if "business analytics" in p and any(
        x in c for x in ("data analyst", "data engineer", "bi analyst", "analytics")
    ):
        return (
            "ALIGNMENT: STRONG. This degree is intended for analytics and data-informed roles. "
            "You MUST respond with STATUS: OK. List individual courses as **CODE Title** lines "
            "(e.g. BUAN 6398 …) from the PROGRAM CONTEXT — not generic elective/track descriptions."
        )
    if "financial technology" in p or "fintech" in p:
        if any(x in c for x in ("data", "analyst", "engineer", "python", "sql")):
            return (
                "ALIGNMENT: STRONG. Use STATUS: OK and recommend from context."
            )
    if "information technology" in p or "itm" in p:
        if any(x in c for x in ("data", "software", "engineer", "developer", "devops", "backend")):
            return "ALIGNMENT: STRONG. Use STATUS: OK and recommend from context."
    # Clear mismatch examples only
    if "accounting" in p and not any(x in c for x in ("account", "audit", "tax", "cpa", "finance")):
        if any(x in c for x in ("frontend", "android", "ios", "game developer")):
            return (
                "ALIGNMENT: WEAK for this combination. Prefer STATUS: NO_MATCH unless the PROGRAM CONTEXT "
                "clearly lists electives that support the career path."
            )
    return ""


def build_recommendation_prompt(
    pursuing: str,
    skills: list[str],
    goal: str,
    programs_context: str,
    course_catalog: str,
    program_key: str,
    completed_courses: list[str] | None = None,
) -> str:
    skills_str = ", ".join(skills) if skills else "not clearly specified"
    completed_courses_str = (
        ", ".join(completed_courses)
        if completed_courses
        else "none provided"
    )
    hint = career_program_alignment_hint(program_key, goal)
    catalog_note = ""
    if not (course_catalog or "").strip():
        catalog_note = (
            "Note: The auto-extracted course-code list below may be empty because catalog HTML "
            "does not always match our parser—still use the full PROGRAM CONTEXT for course titles and codes."
        )
    else:
        catalog_note = "Use the extracted lines below as high-confidence anchors when available."

    return f"""
You are the JSOM Smart Advisor at UT Dallas.

Student goal:
- What they are pursuing: {pursuing}
- JSOM program (internal): {program_key}
- Target career path: {goal}
- Current skills: {skills_str}
- Completed JSOM courses from transcript (do NOT recommend again): {completed_courses_str}

{hint}

Below is information from the JSOM program page(s) the student selected (see PROGRAM lines).
Use ONLY this information to recommend specific subjects (courses) that will help the student
prepare for the target career path.

CRITICAL – When to use STATUS: NO_MATCH (only these cases):
- The PROGRAM CONTEXT below is empty or essentially useless (no course or requirement text), OR
- The alignment hint says WEAK and the page truly offers no reasonable path to the career.

Do NOT use NO_MATCH just because the “extracted catalog” block is empty—the full page text still counts.

If STATUS: NO_MATCH:
- First line exactly: STATUS: NO_MATCH
- Then 2–4 short polite paragraphs. No invented course codes.

If STATUS: OK (default for strong degree/career pairs like MS Business Analytics + Data Analyst):
- First line exactly: STATUS: OK

IMPORTANT – Scope (when STATUS: OK):
- Recommend courses ONLY from the program(s) listed in the context below.
- Do NOT recommend courses from other JSOM degrees.

IMPORTANT – Output format (when STATUS: OK) — follow exactly:
- Do NOT write generic “tracks,” “elective categories,” or high-level summaries (bad examples to avoid:
  “Electives in Data Science,” “Core courses for foundation in tools,” “Flex Program” bullets without course codes).
- You MUST list concrete courses as separate lines. Each line MUST look like:
  BUAN 6398 Prescriptive Analytics (subject code + short title as in the catalog text).
- When the EXTRACTED COURSE CATALOG block below is non-empty, **prioritize those lines** and include the same codes in your answer.
- When codes appear anywhere in PROGRAM CONTEXT, copy them — do not paraphrase the degree into tracks.
- Recommend **5–10 specific courses** when the context lists that many; otherwise as many as are clearly named with codes in the text.
- Do NOT include any course whose code appears in the student's completed-course list above.
- After the course list, add 1 short paragraph tying choices to the target career path (data analyst skills: SQL, visualization, statistics, etc.).

{catalog_note}

EXTRACTED COURSE CATALOG (regex — use these first when present):
{course_catalog}

JSOM PROGRAMS AND COURSES CONTEXT:
{programs_context}

Output rules:
- Start with exactly STATUS: NO_MATCH or STATUS: OK on the first line (no other text on that line).
- If STATUS: OK, second line blank, then your course list (one course per line, CODE + title), then the short paragraph.
"""


def parse_llm_recommendation(raw: str) -> tuple[str, bool]:
    """
    Parse Grok output that starts with STATUS: OK or STATUS: NO_MATCH.
    Returns (display_text, is_no_match).
    """
    text = (raw or "").strip()
    if not text:
        return DEFAULT_NO_COURSE_MESSAGE, True

    first_line, _, rest = text.partition("\n")
    first = first_line.strip()
    def _strip_course_bold_markers(s: str) -> str:
        # LLMs sometimes return Markdown bold around course lines (e.g., **BUAN 6312 ...**).
        # Keep plain text output for cleaner UI rendering.
        return re.sub(r"\*\*\s*([A-Z]{2,5}\s*\d{4}[^*]*)\s*\*\*", r"\1", s)

    if first == "STATUS: NO_MATCH":
        body = rest.strip()
        body = _strip_course_bold_markers(body)
        return (body if body else DEFAULT_NO_COURSE_MESSAGE), True
    if first == "STATUS: OK":
        cleaned = _strip_course_bold_markers(rest.strip() if rest.strip() else text)
        return cleaned, False

    # Model omitted status line — show full response
    return _strip_course_bold_markers(text), False


def count_course_lines(text: str) -> int:
    """Count lines that look like concrete course entries (e.g., BUAN 6398 ...)."""
    if not text:
        return 0
    course_line_re = re.compile(
        r"^\s*(?:[-*•]\s*|\d+\.\s*)?(?:[A-Z]{2,5}\s*\d{4}\b)"
    )
    n = 0
    for line in text.splitlines():
        norm = re.sub(r"[*_`#]+", "", line)
        if course_line_re.search(norm):
            n += 1
    return n


def extract_course_lines_from_recommendation(text: str) -> list[str]:
    """Pull lines that contain a subject code (e.g. BUAN 6398) from model or fallback output."""
    if not (text or "").strip():
        return []
    course_line_re = re.compile(
        r"^\s*(?:[-*•]\s*|\d+\.\s*)?(?:[A-Z]{2,5}\s*\d{4}\b)"
    )
    out: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        norm = re.sub(r"[*_`#]+", "", line).strip()
        if not norm or norm.upper().startswith("STATUS:"):
            continue
        if not course_line_re.search(norm):
            continue
        norm = re.sub(r"^[-*•]+\s*", "", norm).strip()
        norm = re.sub(r"^\d+\.\s*", "", norm).strip()
        norm = _strip_elective_requirements_noise(norm)
        key = norm.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(norm)
    return out


def semester_count_for_degree(program_key: str, pursuing_display: str) -> int:
    """
    Typical JSOM pacing: master's ~2 years (4 semesters), bachelor's ~4 years (8 semesters).
    """
    pk = (program_key or "").strip()
    pd = (pursuing_display or "").lower()
    if pk.startswith("BS ") or "bachelor" in pd:
        return 8
    return 4


_FOUNDATION_HINTS = (
    "foundation",
    "fundamental",
    "intro",
    "introduction",
    "principles",
    "basic",
    "basics",
    "core",
    "survey",
    "essentials",
)
_ADVANCED_HINTS = (
    "advanced",
    "applied",
    "capstone",
    "thesis",
    "seminar",
    "special topics",
    "independent study",
    "practicum",
    "internship",
    "strategy",
    "architect",
)


def _course_level_bucket(course_line: str) -> int:
    """
    Bucket courses for sequencing:
    0=fundamental, 1=intermediate/default, 2=advanced/specialized.
    """
    t = (course_line or "").lower()
    if any(h in t for h in _FOUNDATION_HINTS):
        return 0
    if any(h in t for h in _ADVANCED_HINTS):
        return 2
    # Numeric heuristic: 63xx often foundational-to-mid, 64xx/65xx often advanced.
    m = re.search(r"\b[A-Z]{2,5}\s*(\d{4})\b", (course_line or "").upper())
    if m:
        num = int(m.group(1))
        if num <= 6339:
            return 0
        if num >= 6400:
            return 2
    return 1


def order_courses_for_semesters(courses: list[str]) -> list[str]:
    """Order likely foundational courses earlier and advanced courses later."""
    indexed = list(enumerate(courses))
    indexed.sort(key=lambda it: (_course_level_bucket(it[1]), it[0]))
    return [c for _, c in indexed]


def distribute_courses_to_semesters(
    courses: list[str], n_semesters: int
) -> dict[int, list[str]]:
    """Spread courses across semesters as evenly as possible (first semesters get extras)."""
    n_semesters = max(1, int(n_semesters))
    if not courses:
        return {s: [] for s in range(1, n_semesters + 1)}
    ordered = order_courses_for_semesters(courses)
    n = len(ordered)
    base, extra = divmod(n, n_semesters)
    plan: dict[int, list[str]] = {}
    idx = 0
    for sem in range(1, n_semesters + 1):
        take = base + (1 if sem <= extra else 0)
        plan[sem] = ordered[idx : idx + take]
        idx += take
    return plan


_ELECTIVE_HINTS = (
    "elective",
    "special topics",
    "independent study",
    "internship",
    "practicum",
    "seminar",
)


def _is_likely_elective(course_line: str) -> bool:
    line = _strip_elective_requirements_noise((course_line or "").strip()).lower()
    return any(h in line for h in _ELECTIVE_HINTS)


def _format_course_for_semester_box(course_line: str) -> str:
    """
    Mark likely core courses with square brackets so users can distinguish
    core-looking recommendations from likely electives at a glance.
    """
    c = _strip_elective_requirements_noise((course_line or "").strip())
    if not c:
        return (course_line or "").strip()
    if _is_likely_elective(c):
        return c
    return f"{c} *"


def render_semester_plan_flowchart(
    program_key: str,
    pursuing_display: str,
    answer_text: str,
    completed_semesters: int = 0,
) -> None:
    """
    Flowchart: semester columns, square course boxes, arrows between semesters.
    Only call when recommendations include at least one coded course line.
    """
    courses = extract_course_lines_from_recommendation(answer_text)
    if not courses:
        return
    n_sem_total = semester_count_for_degree(program_key, pursuing_display)
    completed_sem = max(0, int(completed_semesters))
    remaining_sem = max(1, n_sem_total - completed_sem)
    plan = distribute_courses_to_semesters(courses, remaining_sem)
    pace = (
        "four-year (8 semesters)"
        if n_sem_total == 8
        else "two-year (4 semesters)"
    )

    st.subheader("Illustrative semester plan")
    st.caption(
        f"Courses spread across the **remaining {remaining_sem} semesters** "
        f"(of {n_sem_total} total; {completed_sem} completed, {pace} typical). "
        "Ordering is a planning aid only—not official prerequisites or term offerings. "
        "Confirm with the JSOM catalog and your advisor."
    )

    parts: list[str] = ['<div class="semester-flow" role="group" aria-label="Semester course plan">']
    for i in range(remaining_sem):
        sem = completed_sem + i + 1
        if i > 0:
            parts.append('<div class="semester-arrow" aria-hidden="true">&#8594;</div>')
        parts.append('<div class="semester-col">')
        parts.append(
            f'<div class="semester-title">{html.escape(f"Semester {sem}")}</div>'
        )
        sem_courses = plan.get(i + 1, [])
        if sem_courses:
            for c in sem_courses:
                parts.append(
                    f'<div class="course-box">{html.escape(_format_course_for_semester_box(c))}</div>'
                )
        else:
            parts.append(
                '<div class="course-box empty">Electives / plan with advisor</div>'
            )
        parts.append("</div>")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)
    st.caption(
        "* indicates likely core courses; unlabeled courses are likely electives."
    )


def build_fallback_course_list_from_catalog(
    course_catalog: str, program_name: str, target_role: str, max_items: int = 10
) -> str:
    """
    Build a deterministic recommendation block from scraped catalog lines when
    the model returns too few concrete courses.
    """
    lines = [ln.strip() for ln in (course_catalog or "").splitlines() if ln.strip()]
    cleaned: list[str] = []
    seen = set()
    for ln in lines:
        # expected format: "- BUAN 6398 Prescriptive Analytics (MS Business Analytics)"
        item = ln.lstrip("-").strip()
        # remove trailing "(Program)" note for cleaner display
        item = re.sub(r"\s+\([^)]*\)\s*$", "", item).strip()
        if item.lower() in seen:
            continue
        seen.add(item.lower())
        cleaned.append(item)

    if not cleaned:
        return ""

    selected = cleaned[:max_items]
    bullet_list = "\n".join(f"- {item}" for item in selected)
    return (
        f"Using the official JSOM catalog text for **{program_name}**, here are concrete courses "
        f"that align with **{target_role}**:\n\n"
        f"{bullet_list}\n\n"
        "These are extracted from the selected program page. You can prioritize foundations first "
        "(statistics, data management, analytics methods) and then advanced analytics/prescriptive topics."
    )


def coursera_suggestions_for_target_role(target_role: str) -> list[tuple[str, str]]:
    """
    Curated Coursera professional certificates / specializations by career keyword.
    Used only when JSOM returns no concrete course list (no_match). Links are public pages.
    """
    r = (target_role or "").lower().strip()
    # (substring in role, display title, coursera URL)
    catalog: list[tuple[str, str, str]] = [
        (
            "data analyst",
            "Google Data Analytics Professional Certificate",
            "https://www.coursera.org/professional-certificates/google-data-analytics",
        ),
        (
            "bi analyst",
            "Google Data Analytics Professional Certificate",
            "https://www.coursera.org/professional-certificates/google-data-analytics",
        ),
        (
            "data engineer",
            "IBM Data Engineering Professional Certificate",
            "https://www.coursera.org/professional-certificates/ibm-data-engineering",
        ),
        (
            "machine learning",
            "Machine Learning Specialization (Stanford / DeepLearning.AI)",
            "https://www.coursera.org/specializations/machine-learning-introduction",
        ),
        (
            "ai engineer",
            "IBM AI Engineering Professional Certificate",
            "https://www.coursera.org/professional-certificates/ibm-ai-engineering",
        ),
        (
            "ai and data scientist",
            "IBM Data Science Professional Certificate",
            "https://www.coursera.org/professional-certificates/ibm-data-science",
        ),
        (
            "cybersecurity",
            "Google Cybersecurity Professional Certificate",
            "https://www.coursera.org/professional-certificates/google-cybersecurity",
        ),
        (
            "devsecops",
            "Google Cybersecurity Professional Certificate",
            "https://www.coursera.org/professional-certificates/google-cybersecurity",
        ),
        (
            "devops",
            "DevOps, Cloud, and Agile Foundations Specialization",
            "https://www.coursera.org/specializations/devops-cloud-and-agile-foundations",
        ),
        (
            "mlops",
            "Machine Learning Engineering for Production (MLOps) Specialization",
            "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops",
        ),
        (
            "frontend",
            "Meta Front-End Developer Professional Certificate",
            "https://www.coursera.org/professional-certificates/meta-front-end-developer",
        ),
        (
            "full stack",
            "IBM Full Stack Software Developer Professional Certificate",
            "https://www.coursera.org/professional-certificates/ibm-full-stack-cloud-developer",
        ),
        (
            "backend",
            "Java Programming and Software Engineering Fundamentals Specialization",
            "https://www.coursera.org/specializations/java-programming",
        ),
        (
            "android",
            "Android App Development Specialization",
            "https://www.coursera.org/specializations/android-app-development",
        ),
        (
            "ios",
            "iOS App Development with Swift Specialization",
            "https://www.coursera.org/specializations/ios-app-development-swift",
        ),
        (
            "ux design",
            "Google UX Design Professional Certificate",
            "https://www.coursera.org/professional-certificates/google-ux-design",
        ),
        (
            "product manager",
            "Digital Product Management Specialization",
            "https://www.coursera.org/specializations/digital-product-management",
        ),
        (
            "postgresql",
            "PostgreSQL for Everybody Specialization",
            "https://www.coursera.org/specializations/postgresql-for-everybody",
        ),
        (
            "qa",
            "Software Testing and Automation Specialization",
            "https://www.coursera.org/specializations/software-testing-automation",
        ),
        (
            "blockcchain",
            "Blockchain Specialization",
            "https://www.coursera.org/specializations/blockchain",
        ),
        (
            "game developer",
            "Game Design and Development Specialization",
            "https://www.coursera.org/specializations/game-design",
        ),
        (
            "software architect",
            "Software Design and Architecture Specialization",
            "https://www.coursera.org/specializations/software-design-architecture",
        ),
        (
            "engineering manager",
            "Leading People and Teams Specialization",
            "https://www.coursera.org/specializations/leading-people-teams",
        ),
        (
            "technical writer",
            "Writing in the Sciences",
            "https://www.coursera.org/learn/sciwrite",
        ),
    ]
    picked: list[tuple[str, str]] = []
    seen_url: set[str] = set()
    for needle, title, url in catalog:
        if needle in r and url not in seen_url:
            seen_url.add(url)
            picked.append((title, url))
        if len(picked) >= 4:
            break
    if not picked:
        picked = [
            (
                "Google Data Analytics Professional Certificate",
                "https://www.coursera.org/professional-certificates/google-data-analytics",
            ),
            (
                "Python for Everybody Specialization",
                "https://www.coursera.org/specializations/python",
            ),
        ]
    return picked[:5]


def _resume_file_from_bytes(data: bytes, filename: str) -> io.BytesIO:
    """BytesIO wrapper so extract_resume_text sees a .name for PDF vs TXT."""
    buf = io.BytesIO(data)
    buf.name = filename
    return buf


def run_jsom_advisor_pipeline(
    llm: Any,
    pursuing: str,
    target_role: str,
    resume_bytes: bytes,
    resume_filename: str,
    transcript_bytes: bytes | None = None,
    transcript_filename: str | None = None,
) -> dict[str, Any]:
    """Run scrape → gaps → Grok recommendation. Returns a dict for UI rendering."""
    resume_file = _resume_file_from_bytes(resume_bytes, resume_filename)
    resume_text = extract_resume_text(resume_file)
    transcript_text = ""
    if transcript_bytes and transcript_filename:
        transcript_file = _resume_file_from_bytes(transcript_bytes, transcript_filename)
        transcript_text = extract_resume_text(transcript_file)

    skills = extract_skills_hybrid(llm, resume_text)
    matched_skills, missing_skills, roadmap_slug, gap_source_note = (
        compute_skill_gaps(resume_text, skills, target_role.strip())
    )
    program_map, pursuit_warning = match_pursuing_to_programs(pursuing.strip())
    programs_context = fetch_program_context(program_map)

    transcript_course_entries: list[tuple[str, str]] = []
    completed_courses: list[str] = []
    completed_semesters = 0
    if transcript_text.strip():
        transcript_course_entries = parse_transcript_course_entries(transcript_text)
        transcript_course_entries = supplement_titles_from_program_text(
            programs_context, transcript_course_entries
        )
        completed_courses = [c for c, _ in transcript_course_entries]
        completed_semesters = estimate_completed_semesters_from_transcript(
            transcript_text, completed_courses
        )

    course_catalog = extract_course_catalog(programs_context)
    if transcript_text.strip() and transcript_course_entries:
        transcript_course_entries = merge_transcript_titles_with_course_catalog_blob(
            course_catalog, transcript_course_entries
        )
        completed_courses = [c for c, _ in transcript_course_entries]

    program_key = PURSUIT_TO_PROGRAM.get(pursuing.strip(), pursuing.strip())
    err_msg: str | None = None

    if not programs_context.strip():
        answer = DEFAULT_NO_COURSE_MESSAGE
        no_match = True
    else:
        prompt = build_recommendation_prompt(
            pursuing.strip(),
            skills,
            target_role.strip(),
            programs_context,
            course_catalog,
            program_key,
            completed_courses,
        )
        try:
            response = llm.invoke(prompt)
            raw_answer = (
                response.content
                if hasattr(response, "content")
                else str(response)
            )
            answer, no_match = parse_llm_recommendation(raw_answer)
            hint_txt = career_program_alignment_hint(
                program_key, target_role.strip()
            )
            if no_match and "MUST respond with STATUS: OK" in hint_txt:
                retry_prompt = f"""Your previous answer used STATUS: NO_MATCH, but this pairing is a strong fit.

Career path: {target_role.strip()}
Program: {program_key}

Use ONLY the text below. Reply with:
Line 1: STATUS: OK
Line 2: (blank)
Lines 3+: One course per line in this exact pattern: CODE Title
Example: BUAN 6398 Prescriptive Analytics
Do NOT use generic track names or "Electives in …" without a subject code on each line.
Pull every course line you can find that matches a subject code (like BUAN 6398) in the text.

PROGRAM CONTEXT:
{programs_context[:min(len(programs_context), 48000)]}
"""
                response = llm.invoke(retry_prompt)
                raw_answer = (
                    response.content
                    if hasattr(response, "content")
                    else str(response)
                )
                answer, no_match = parse_llm_recommendation(raw_answer)
            if not no_match and count_course_lines(answer) < 4:
                fallback = build_fallback_course_list_from_catalog(
                    course_catalog,
                    program_key,
                    target_role.strip(),
                )
                if fallback:
                    answer = fallback
            if completed_courses and not no_match:
                completed_set = {c.upper() for c in completed_courses}
                filtered_lines: list[str] = []
                removed = 0
                for line in answer.splitlines():
                    code = _first_course_code_token(
                        re.sub(r"[*_`#]+", "", (line or "")).strip()
                    )
                    if code and code.upper() in completed_set:
                        removed += 1
                        continue
                    filtered_lines.append(line)
                answer = "\n".join(filtered_lines).strip()
                if removed > 0 and not answer:
                    answer = (
                        "Great progress — your transcript indicates you have already completed the "
                        "currently matched course list from this program. Upload an updated transcript "
                        "or try a different target role for additional recommendations."
                    )
        except Exception as e:
            answer = (
                "I encountered an error while generating recommendations. "
                "Please try again or check your API configuration."
            )
            no_match = True
            err_msg = str(e)

    return {
        "answer": answer,
        "no_match": no_match,
        "skills": skills,
        "missing_skills": missing_skills,
        "matched_skills": matched_skills,
        "gap_source_note": gap_source_note,
        "pursuit_warning": pursuit_warning,
        "roadmap_slug": roadmap_slug,
        "pursuing": pursuing,
        "target_role": target_role,
        "program_key": program_key,
        "completed_courses": completed_courses,
        "completed_semesters": completed_semesters,
        "transcript_course_entries": transcript_course_entries,
        "transcript_uploaded": bool(transcript_bytes and transcript_filename),
        "error": err_msg,
    }


def render_advisor_results(bundle: dict[str, Any]) -> None:
    """Skills, gaps, metrics, recommendations card, semester flow, Coursera (if no_match)."""
    if bundle.get("error"):
        st.error(bundle["error"])

    if bundle.get("pursuit_warning"):
        st.info(bundle["pursuit_warning"])

    skills = bundle.get("skills") or []
    if skills:
        st.subheader("Skills detected from your resume")
        st.write(", ".join(skills))
    else:
        st.subheader("Skills detected from your resume")
        st.write("No clear skills were detected from the uploaded resume.")

    st.subheader("Skill gaps for your target role")
    st.caption(bundle.get("gap_source_note", ""))
    missing_skills = bundle.get("missing_skills") or []
    if missing_skills:
        st.write(", ".join(missing_skills))
    else:
        st.write("No major gaps detected against the selected topic list for this role.")

    transcript_uploaded = bool(bundle.get("transcript_uploaded"))
    transcript_course_entries = list(bundle.get("transcript_course_entries") or [])
    if transcript_uploaded and not transcript_course_entries and bundle.get("completed_courses"):
        transcript_course_entries = [
            (c, "") for c in (bundle.get("completed_courses") or [])
        ]
    completed_semesters = int(bundle.get("completed_semesters") or 0)
    if not transcript_uploaded:
        st.info(
            "Transcript file upload was skipped. Recommendations are generated without "
            "completed-course filtering."
        )

    _sm = skill_metrics_alignment(
        bundle.get("matched_skills") or [],
        missing_skills,
        bundle.get("roadmap_slug"),
    )
    render_skill_metrics_block(
        _sm,
        transcript_uploaded=transcript_uploaded,
        transcript_course_entries=transcript_course_entries,
        completed_semesters=completed_semesters,
    )

    no_match = bool(bundle.get("no_match"))
    answer = bundle.get("answer") or ""
    pursuing = bundle.get("pursuing") or ""
    target_role = bundle.get("target_role") or ""

    st.subheader("Recommended JSOM Subjects for Your Goal")
    if no_match:
        st.info(
            "No course list is suggested for this program + career path combination "
            "(or catalog data wasn’t enough). Read the note below."
        )
    answer_display = _clean_advisor_answer_for_display(answer)
    answer_html = html.escape(answer_display).replace("\n", "<br/>")
    st.markdown(
        f"<div class='answer-card'>{answer_html}</div>",
        unsafe_allow_html=True,
    )
    pk = PURSUIT_TO_PROGRAM.get(pursuing.strip(), pursuing.strip())
    if not no_match:
        render_semester_plan_flowchart(
            pk,
            pursuing.strip(),
            answer_display,
            completed_semesters=completed_semesters,
        )
    if no_match:
        st.markdown("---")
        st.subheader("Suggested Coursera paths for your goal")
        st.caption(
            "Shown only when no JSOM course list was returned above. "
            "These are external resources—check prerequisites and your degree plan with JSOM advising."
        )
        for ctitle, curl in coursera_suggestions_for_target_role(target_role.strip()):
            st.markdown(f"- [{ctitle}]({curl})")


def init_chat_session_state() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_phase" not in st.session_state:
        st.session_state.chat_phase = "pick_program"
    if "chat_pursuing" not in st.session_state:
        st.session_state.chat_pursuing = None
    if "chat_target_role" not in st.session_state:
        st.session_state.chat_target_role = None
    if "chat_resume_bytes" not in st.session_state:
        st.session_state.chat_resume_bytes = None
    if "chat_resume_filename" not in st.session_state:
        st.session_state.chat_resume_filename = None
    if "chat_resume_fingerprint" not in st.session_state:
        st.session_state.chat_resume_fingerprint = None
    if "chat_transcript_bytes" not in st.session_state:
        st.session_state.chat_transcript_bytes = None
    if "chat_transcript_filename" not in st.session_state:
        st.session_state.chat_transcript_filename = None
    if "chat_transcript_fingerprint" not in st.session_state:
        st.session_state.chat_transcript_fingerprint = None
    if "chat_result_bundle" not in st.session_state:
        st.session_state.chat_result_bundle = None
    if "chat_welcomed" not in st.session_state:
        st.session_state.chat_welcomed = False
    if "chat_upload_key" not in st.session_state:
        st.session_state.chat_upload_key = 0


def reset_chat_conversation() -> None:
    st.session_state.chat_messages = []
    st.session_state.chat_phase = "pick_program"
    st.session_state.chat_pursuing = None
    st.session_state.chat_target_role = None
    st.session_state.chat_resume_bytes = None
    st.session_state.chat_resume_filename = None
    st.session_state.chat_resume_fingerprint = None
    st.session_state.chat_transcript_bytes = None
    st.session_state.chat_transcript_filename = None
    st.session_state.chat_transcript_fingerprint = None
    st.session_state.chat_result_bundle = None
    st.session_state.chat_welcomed = False
    st.session_state.chat_upload_key = int(st.session_state.chat_upload_key) + 1


def main():
    llm = get_llm()
    init_chat_session_state()

    st.markdown(
        """
<div class="jsom-app-header" role="banner">
  <div class="jsom-app-header-inner">
    <div class="jsom-header-brand">
      <span class="jsom-logo-tile" aria-hidden="true">UT<br/>Dallas</span>
      <div>
        <h1 class="jsom-header-title">JSOM Smart Advisor</h1>
        <p class="jsom-header-sub">Naveen Jindal School of Management · The University of Texas at Dallas</p>
      </div>
    </div>
    <div class="jsom-header-pill"><span class="jsom-dot" aria-hidden="true"></span> AI Advisor Active</div>
  </div>
</div>
<div class="jsom-welcome-banner">
  <div class="jsom-welcome-accent" aria-hidden="true"></div>
  <div class="jsom-welcome-inner">
    <span class="jsom-welcome-ai">AI</span>
    <p>Welcome — use the chat below and tap each step’s options. We’ll suggest JSOM courses aligned to your resume and career goal.</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Conversation")
        if st.button("Start new conversation", use_container_width=True):
            reset_chat_conversation()
            st.rerun()

    if not llm:
        st.warning(
            "To enable recommendations, add **ANTHROPIC_API_KEY** (Claude) in Streamlit Cloud "
            "**Settings → Secrets**, or in `config/.env` locally."
        )

    # Run advisor after user picked career (one-shot generation)
    if st.session_state.chat_phase == "generating":
        if not llm:
            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": "I can’t generate recommendations without **ANTHROPIC_API_KEY**. Add it in Streamlit **Secrets** or `config/.env`, then choose your career path again.",
                }
            )
            st.session_state.chat_phase = "pick_career"
            st.rerun()
        elif not (
            st.session_state.chat_pursuing
            and st.session_state.chat_target_role
            and st.session_state.chat_resume_bytes
            and st.session_state.chat_resume_filename
        ):
            st.session_state.chat_phase = "upload_resume"
            st.rerun()
        else:
            with st.spinner("Analyzing your resume and JSOM programs…"):
                bundle = run_jsom_advisor_pipeline(
                    llm,
                    st.session_state.chat_pursuing,
                    st.session_state.chat_target_role,
                    st.session_state.chat_resume_bytes,
                    st.session_state.chat_resume_filename,
                    st.session_state.chat_transcript_bytes,
                    st.session_state.chat_transcript_filename,
                )
            st.session_state.chat_result_bundle = bundle
            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": "Here’s your personalized analysis. **Scroll down** for skills, gaps, course recommendations, and the semester plan.",
                }
            )
            st.session_state.chat_phase = "results_shown"

    if (
        st.session_state.chat_phase == "pick_program"
        and not st.session_state.chat_welcomed
    ):
        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": (
                    "Hi! I’m the **JSOM Smart Advisor**. "
                    "**Step 1:** Which program are you pursuing? Select it from the dropdown below."
                ),
            }
        )
        st.session_state.chat_welcomed = True

    with st.container():
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Option pickers (chat-style with dropdowns)
    phase = st.session_state.chat_phase

    if phase == "pick_program":
        st.markdown(
            '<p class="chat-option-hint">Choose your JSOM program</p>',
            unsafe_allow_html=True,
        )
        program_options = ["Select a JSOM program"] + PURSUIT_OPTIONS
        program_pick = st.selectbox(
            "Choose your JSOM program",
            options=program_options,
            index=(
                program_options.index(st.session_state.chat_pursuing)
                if st.session_state.chat_pursuing in program_options
                else 0
            ),
            key="chat_program_dropdown",
            label_visibility="collapsed",
        )
        if (
            program_pick != "Select a JSOM program"
            and program_pick != st.session_state.chat_pursuing
        ):
            st.session_state.chat_pursuing = program_pick
            st.session_state.chat_messages.append(
                {"role": "user", "content": program_pick}
            )
            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "**Step 2:** Upload your resume (PDF or TXT) using the uploader below."
                    ),
                }
            )
            st.session_state.chat_phase = "upload_resume"
            st.rerun()

    elif phase == "upload_resume":
        st.markdown(
            '<p class="chat-option-hint">Upload resume</p>',
            unsafe_allow_html=True,
        )
        up = st.file_uploader(
            "Resume file",
            type=["pdf", "txt"],
            label_visibility="collapsed",
            key=f"chat_resume_uploader_{st.session_state.chat_upload_key}",
        )
        if up is not None:
            data = up.getvalue()
            fp = f"{up.name}:{len(data)}"
            if st.session_state.chat_resume_fingerprint != fp:
                st.session_state.chat_resume_bytes = data
                st.session_state.chat_resume_filename = up.name
                st.session_state.chat_resume_fingerprint = fp
                st.session_state.chat_messages.append(
                    {
                        "role": "user",
                        "content": f"📎 Uploaded **{up.name}**",
                    }
                )
                st.session_state.chat_messages.append(
                    {
                        "role": "assistant",
                        "content": (
                            "**Step 3 (optional):** Upload your transcript (PDF/TXT) so I can avoid "
                            "already-completed courses and build the plan for remaining semesters."
                        ),
                    }
                )
                st.session_state.chat_phase = "upload_transcript"
                st.rerun()

    elif phase == "upload_transcript":
        st.markdown(
            '<p class="chat-option-hint">Upload transcript (optional)</p>',
            unsafe_allow_html=True,
        )
        tr = st.file_uploader(
            "Transcript file",
            type=["pdf", "txt"],
            label_visibility="collapsed",
            key=f"chat_transcript_uploader_{st.session_state.chat_upload_key}",
        )
        if tr is not None:
            t_data = tr.getvalue()
            t_fp = f"{tr.name}:{len(t_data)}"
            if st.session_state.chat_transcript_fingerprint != t_fp:
                tr_file = _resume_file_from_bytes(t_data, tr.name)
                tr_text = extract_resume_text(tr_file)
                if not looks_like_transcript_text(tr_text):
                    st.session_state.chat_messages.append(
                        {
                            "role": "assistant",
                            "content": (
                                "The uploaded file does not look like a transcript. "
                                "Please upload an official transcript (PDF/TXT with term/course records), "
                                "or click **Skip transcript**."
                            ),
                        }
                    )
                    st.rerun()
                st.session_state.chat_transcript_bytes = t_data
                st.session_state.chat_transcript_filename = tr.name
                st.session_state.chat_transcript_fingerprint = t_fp
                st.session_state.chat_messages.append(
                    {"role": "user", "content": f"📄 Uploaded transcript **{tr.name}**"}
                )
                st.session_state.chat_messages.append(
                    {
                        "role": "assistant",
                        "content": (
                            "**Step 4:** What career path are you aiming for? "
                            "Select it from the dropdown below."
                        ),
                    }
                )
                st.session_state.chat_phase = "pick_career"
                st.rerun()
        if st.button(
            "Skip transcript",
            key="chat_transcript_skip",
            use_container_width=True,
        ):
            st.session_state.chat_messages.append(
                {"role": "user", "content": "Skipped transcript upload"}
            )
            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "**Step 4:** What career path are you aiming for? "
                        "Select it from the dropdown below."
                    ),
                }
            )
            st.session_state.chat_phase = "pick_career"
            st.rerun()

    elif phase == "pick_career":
        st.markdown(
            '<p class="chat-option-hint">Choose your target career path</p>',
            unsafe_allow_html=True,
        )
        career_options = ["Select a target career path"] + CAREER_PATH_OPTIONS
        career_pick = st.selectbox(
            "Choose your target career path",
            options=career_options,
            index=(
                career_options.index(st.session_state.chat_target_role)
                if st.session_state.chat_target_role in career_options
                else 0
            ),
            key="chat_career_dropdown",
            label_visibility="collapsed",
        )
        if (
            career_pick != "Select a target career path"
            and career_pick != st.session_state.chat_target_role
        ):
            st.session_state.chat_target_role = career_pick
            st.session_state.chat_messages.append(
                {"role": "user", "content": career_pick}
            )
            st.session_state.chat_phase = "generating"
            st.rerun()

    if st.session_state.chat_phase == "results_shown" and st.session_state.chat_result_bundle:
        st.markdown("---")
        st.markdown("### Your results")
        render_advisor_results(st.session_state.chat_result_bundle)
        st.markdown(
            '<p class="chat-option-hint">Want to try another program or path? Use **Start new conversation** in the sidebar.</p>',
            unsafe_allow_html=True,
        )

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
