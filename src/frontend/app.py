"""
Streamlit Frontend Application
JSOM Smart Advisor - Resume-based course recommendation.
"""

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


# Community roadmaps from roadmap.sh (see https://roadmap.sh/, source: developer-roadmap repo)
ROADMAP_JSON_BASE = (
    "https://raw.githubusercontent.com/kamranahmedse/developer-roadmap/master/"
    "src/data/roadmaps/{slug}/{slug}.json"
)


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
        ("ml engineer", "machine-learning"),
        ("ai engineer", "ai-engineer"),
        ("software engineer", "backend"),
        ("backend developer", "backend"),
        ("full stack", "full-stack"),
        ("frontend", "frontend"),
        ("devops", "devops"),
        ("cyber security", "cyber-security"),
        ("product manager", "product-manager"),
        ("engineering manager", "engineering-manager"),
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

    noise = frozenset(
        {
            "optional",
            "pick a language",
            "learn the basics",
            "learn basics",
            "version control systems",
            "what is",
            "roadmap",
        }
    )
    cleaned: list[str] = []
    for s in found:
        sl = s.lower().strip()
        if sl in noise or len(sl) < 3 or len(s) > 85:
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
        return matched, missing, None, "Built-in role baseline (add a more specific target role for roadmap.sh topics)."

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
    note = f"Topics derived from roadmap.sh community roadmaps (GitHub: developer-roadmap / `{slug}.json`)."
    return matched_topics, missing_topics, slug, note

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

Below is information from the JSOM program page(s) the student selected (see PROGRAM lines).
Use ONLY this information to recommend specific subjects (courses) that will help the student
prepare for the target role.

IMPORTANT – Scope:
- Recommend courses ONLY from the program(s) listed in the context below.
- Do NOT recommend courses from other JSOM degrees or programs that are not in this context.

IMPORTANT – Course codes are required:
- For EVERY recommended course you MUST include the official course code (e.g. ACCT 6301, OPRE 6366, MIS 6324, MKT 6301).
- Prefer course code + title pairs found in the extracted catalog list below.
- Format each course as: COURSE_CODE Course Title (example: BUAN 6398 Prescriptive Analytics).
- If the context does not list a code for a course, use the closest match or state "[Code from catalog: check program page]".
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
1. Confirm which JSOM program(s) from the context you are using (must match PROGRAM lines only).
2. List 3–10 high-impact courses from that program only.
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
                    matched_skills, missing_skills, roadmap_slug, gap_source_note = (
                        compute_skill_gaps(resume_text, skills, target_role.strip())
                    )
                    program_map, pursuit_warning = match_pursuing_to_programs(pursuing.strip())
                    programs_context = fetch_program_context(program_map)
                    course_catalog = extract_course_catalog(programs_context)

                    prompt = build_recommendation_prompt(
                        pursuing.strip(),
                        skills,
                        target_role.strip(),
                        programs_context,
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
                if roadmap_slug:
                    st.markdown(
                        f"Explore the full roadmap interactively: **[roadmap.sh](https://roadmap.sh/)** "
                        f"— topic list loaded from community roadmap data (`{roadmap_slug}`)."
                    )
                if missing_skills:
                    st.write(", ".join(missing_skills))
                else:
                    st.write("No major gaps detected against the selected topic list for this role.")

                if matched_skills:
                    st.caption("Topics/skills already reflected in your resume: " + ", ".join(matched_skills))

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
