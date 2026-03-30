"""
Streamlit Frontend Application
JSOM Smart Advisor - Resume-based course recommendation.
"""

import base64
import html
import json
import os
import re
from pathlib import Path
from typing import Any

import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_xai import ChatXAI
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
        --advisor-green: #0f5a33;
        --advisor-green-2: #0b3f27;
        --advisor-orange: #f08a1c;
        --advisor-orange-2: #d97706;
        --advisor-bg: #f6f8fb;
        --advisor-text: #0f172a;
        --advisor-muted: #6b7280;
    }
    /* Overall page tone */
    .stApp {
        background: var(--advisor-bg);
        color: var(--advisor-text);
    }
    .corner-logo {
        position: fixed;
        top: 3.5rem;
        left: 0.75rem;
        width: 120px;
        z-index: 999;
        border-radius: 999px;
        background: #ffffff;
        padding: 4px;
        box-shadow: 0 4px 10px rgba(15, 23, 42, 0.15);
        border: 2px solid rgba(15, 90, 51, 0.25);
    }
    .title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.25rem;
        color: var(--advisor-green);
    }
    .subtitle {
        text-align: center;
        font-size: 1rem;
        color: var(--advisor-muted);
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
        background: var(--advisor-orange);
        color: white;
        border: 1px solid rgba(0,0,0,0.08);
    }
    .stButton>button:hover {
        background: var(--advisor-orange-2);
        color: white;
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
    /* Main recommendation card */
    .answer-card{
        background: linear-gradient(180deg, var(--advisor-green) 0%, var(--advisor-green-2) 100%);
        color: #ffffff;
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 10px 24px rgba(15, 90, 51, 0.22);
        border: 1px solid rgba(255,255,255,0.12);
        line-height: 1.45;
        white-space: normal;
        overflow-wrap: anywhere;
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
) -> str:
    skills_str = ", ".join(skills) if skills else "not clearly specified"
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
- You MUST list **concrete courses** as separate lines. Each line MUST look like:
  **BUAN 6398 Prescriptive Analytics** (subject code + short title as in the catalog text).
- When the EXTRACTED COURSE CATALOG block below is non-empty, **prioritize those lines** and include the same codes in your answer.
- When codes appear anywhere in PROGRAM CONTEXT, copy them — do not paraphrase the degree into tracks.
- Recommend **5–10 specific courses** when the context lists that many; otherwise as many as are clearly named with codes in the text.
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
    if first == "STATUS: NO_MATCH":
        body = rest.strip()
        return (body if body else DEFAULT_NO_COURSE_MESSAGE), True
    if first == "STATUS: OK":
        return (rest.strip() if rest.strip() else text), False

    # Model omitted status line — show full response
    return text, False


def count_course_lines(text: str) -> int:
    """Count lines that look like concrete course entries (e.g., BUAN 6398 ...)."""
    if not text:
        return 0
    course_token_re = re.compile(r"[A-Z]{2,5}\s\d{4}\b")
    n = 0
    for line in text.splitlines():
        norm = re.sub(r"[*_`#]+", "", line)
        if course_token_re.search(norm):
            n += 1
    return n


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

        pursuing = st.selectbox(
            "What program are you pursuing?",
            options=["Select your program"] + PURSUIT_OPTIONS,
            index=0,
            help="Choose your exact JSOM degree/program.",
        )

        resume_file = st.file_uploader(
            "Upload your resume",
            type=["pdf", "txt"],
            help="Upload a recent version of your resume (PDF or TXT).",
        )

        target_role = st.selectbox(
            "What career path are you aiming for?",
            options=["Select a career path"] + CAREER_PATH_OPTIONS,
            index=0,
            help="Career paths mapped to standard industry topic checklists (open-source JSON).",
        )

        if st.button("Get JSOM Subject Recommendations"):
            if pursuing == "Select your program":
                st.warning("Please choose what you’re pursuing from the dropdown.")
            elif not resume_file:
                st.warning("Please upload your resume.")
            elif target_role == "Select a career path":
                st.warning("Please choose your target career path from the dropdown.")
            elif not llm:
                st.error(
                    "Recommendations are disabled. Set **XAI_API_KEY** (Grok) in Streamlit secrets or config/.env."
                )
            else:
                with st.spinner("Analyzing your resume and JSOM programs..."):
                    resume_text = extract_resume_text(resume_file)
                    skills = extract_skills_from_resume(resume_text)
                    matched_skills, missing_skills, roadmap_slug, gap_source_note = (
                        compute_skill_gaps(resume_text, skills, target_role.strip())
                    )
                    program_map, pursuit_warning = match_pursuing_to_programs(pursuing.strip())
                    programs_context = fetch_program_context(program_map)
                    course_catalog = extract_course_catalog(programs_context)

                    if not programs_context.strip():
                        answer = DEFAULT_NO_COURSE_MESSAGE
                        no_match = True
                    else:
                        program_key = PURSUIT_TO_PROGRAM.get(
                            pursuing.strip(), pursuing.strip()
                        )
                        prompt = build_recommendation_prompt(
                            pursuing.strip(),
                            skills,
                            target_role.strip(),
                            programs_context,
                            course_catalog,
                            program_key,
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
                            if (
                                no_match
                                and "MUST respond with STATUS: OK" in hint_txt
                            ):
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
                                answer, no_match = parse_llm_recommendation(
                                    raw_answer
                                )
                            # Guardrail: if model returns too few concrete course lines,
                            # enrich with deterministic catalog-derived list.
                            if not no_match and count_course_lines(answer) < 4:
                                fallback = build_fallback_course_list_from_catalog(
                                    course_catalog,
                                    program_key,
                                    target_role.strip(),
                                )
                                if fallback:
                                    answer = fallback
                        except Exception as e:
                            answer = (
                                "I encountered an error while generating recommendations. "
                                "Please try again or check your API configuration."
                            )
                            no_match = True
                            st.error(str(e))

                if pursuit_warning:
                    st.info(pursuit_warning)

                if skills:
                    st.subheader("Skills detected from your resume")
                    st.write(", ".join(skills))
                else:
                    st.subheader("Skills detected from your resume")
                    st.write("No clear skills were detected from the uploaded resume.")

                st.subheader("Skill gaps for your target role")
                st.caption(gap_source_note)
                if missing_skills:
                    st.write(", ".join(missing_skills))
                else:
                    st.write("No major gaps detected against the selected topic list for this role.")

                st.subheader("Recommended JSOM Subjects for Your Goal")
                if no_match:
                    st.info(
                        "No course list is suggested for this program + career path combination "
                        "(or catalog data wasn’t enough). Read the note below."
                    )
                answer_html = html.escape(answer).replace("\n", "<br/>")
                st.markdown(
                    f"<div class='answer-card'>{answer_html}</div>",
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
