from pathlib import Path

import streamlit as st

from src.analyzer import analyze_match, build_report


st.set_page_config(
    page_title="MatchWise | AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px;}
      .hero {padding: 1.35rem 1.5rem; border: 1px solid rgba(128,128,128,.25); border-radius: 18px;
             background: linear-gradient(115deg, rgba(74,126,255,.12), rgba(21,190,160,.07)); margin-bottom: 1.3rem;}
      .hero h1 {margin: 0 0 .35rem 0; font-size: 2.1rem; letter-spacing: -.04em;}
      .hero p {margin: 0; opacity: .78; font-size: 1rem;}
      .section-title {font-size: 1.12rem; font-weight: 700; margin: .3rem 0 .65rem 0;}
      .skill-chip {display:inline-block; padding: .35rem .65rem; margin: .2rem .25rem .2rem 0;
                   border-radius: 999px; border: 1px solid rgba(128,128,128,.32); font-size: .88rem;}
      .muted {opacity: .72; font-size: .9rem;}
      div[data-testid="stMetric"] {background: rgba(128,128,128,.07); border: 1px solid rgba(128,128,128,.18);
                                    padding: 1rem; border-radius: 14px;}
      .stButton button[kind="primary"] {border-radius: 10px; font-weight: 650;}
    </style>
    """,
    unsafe_allow_html=True,
)


def read_resume(uploaded_file) -> str:
    """Extract text from TXT, PDF, and DOCX uploads."""
    suffix = Path(uploaded_file.name).suffix.lower()
    raw = uploaded_file.getvalue()
    if suffix == ".txt":
        return raw.decode("utf-8", errors="ignore")
    if suffix == ".pdf":
        from pypdf import PdfReader
        import io

        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        from docx import Document
        import io

        document = Document(io.BytesIO(raw))
        parts = [p.text for p in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                parts.append(" ".join(cell.text for cell in row.cells))
        return "\n".join(parts)
    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")


def show_skills(title: str, skills: list[str], empty_message: str) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if skills:
        st.markdown("".join(f'<span class="skill-chip">{skill}</span>' for skill in skills), unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="muted">{empty_message}</p>', unsafe_allow_html=True)


with st.sidebar:
    st.markdown("## 🎯 MatchWise")
    st.caption("A small NLP project with a practical purpose.")
    st.divider()
    st.markdown("### How it works")
    st.markdown(
        "1. Extract text from your resume.\n"
        "2. Compare it with the job description using TF-IDF and cosine similarity.\n"
        "3. Detect skills using a curated skill dictionary.\n"
        "4. Generate an explainable match report."
    )
    st.divider()
    st.markdown("### Privacy")
    st.caption("Analysis runs locally in this app session. Your resume is not sent to an external AI API.")
    st.markdown("### Built with")
    st.caption("Python · Streamlit · scikit-learn · NLP")

st.markdown(
    '<div class="hero"><h1>Find your fit. Improve your story.</h1>'
    '<p>See how closely your resume aligns with a job description—and what to improve next.</p></div>',
    unsafe_allow_html=True,
)

left, right = st.columns(2, gap="large")
with left:
    st.markdown("### 01 · Your resume")
    upload = st.file_uploader("Upload a resume", type=["pdf", "docx", "txt"], help="PDF, DOCX, or plain text")
    resume_text = ""
    if upload is not None:
        try:
            resume_text = read_resume(upload)
            st.success(f"Loaded {upload.name} · {len(resume_text.split())} words")
        except Exception as exc:
            st.error(f"Could not read this file: {exc}")
    pasted_resume = st.text_area(
        "Or paste your resume text",
        height=250,
        placeholder="Paste your summary, experience, projects, education, and skills here...",
    )
    if pasted_resume.strip():
        resume_text = pasted_resume

with right:
    st.markdown("### 02 · Target job")
    job_text = st.text_area(
        "Paste the job description",
        height=330,
        placeholder="Paste the responsibilities, requirements, qualifications, and preferred skills...",
    )
    st.caption("Tip: Include the full requirements section for a more useful comparison.")

analyze = st.button("✨ Analyze my match", type="primary", width="stretch")

if analyze:
    if not resume_text.strip() or not job_text.strip():
        st.warning("Please add both your resume and the job description before analyzing.")
    else:
        try:
            result = analyze_match(resume_text, job_text)
            st.session_state["match_result"] = result
            st.session_state["match_report"] = build_report(result)
        except ValueError as exc:
            st.error(str(exc))

result = st.session_state.get("match_result")
if result:
    st.divider()
    st.markdown("## Your match report")
    st.caption("A transparent comparison of the text and skills found in the two documents.")

    m1, m2, m3 = st.columns(3)
    m1.metric("Overall match", f"{result.overall_score:.1f}%")
    m2.metric("Text similarity", f"{result.similarity_score:.1f}%")
    m3.metric("Skill coverage", f"{result.skill_coverage:.1f}%")
    st.progress(min(max(int(round(result.overall_score)), 0), 100) / 100)

    if result.overall_score >= 75:
        st.success("Strong alignment detected. Focus on making your strongest evidence easy to see.")
    elif result.overall_score >= 50:
        st.info("Moderate alignment. A few targeted resume improvements may make your fit clearer.")
    else:
        st.warning("Low detected alignment. Review the missing requirements before applying.")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        show_skills("✅ Matched skills", result.matched_skills, "No recognized skills matched yet.")
        show_skills("🧩 Skills detected in your resume", result.resume_skills, "No skills from the current dictionary were detected.")
    with c2:
        show_skills("＋ Skills not detected in your resume", result.missing_skills, "No missing skills detected from the current dictionary.")
        show_skills("📌 Skills detected in the job description", result.job_skills, "No recognized skills found in the job description.")

    st.markdown("### What to improve")
    for suggestion in result.suggestions:
        st.markdown(f"- {suggestion}")

    if result.top_shared_terms:
        st.markdown("### Shared keywords")
        st.caption("High-signal terms found in both documents: " + " · ".join(result.top_shared_terms))

    st.download_button(
        "⬇️ Download match report",
        data=st.session_state["match_report"],
        file_name="matchwise_report.md",
        mime="text/markdown",
        width="stretch",
    )
    st.caption(
        "Important: This score is an educational NLP estimate, not a recruiter score, hiring prediction, or guarantee. "
        "The skill dictionary is curated and may miss synonyms or domain-specific terms."
    )
else:
    st.info("Add your resume and a job description, then select **Analyze my match** to see your report.")

st.markdown("<div class='muted' style='text-align:center;margin-top:2.5rem'>MATCHWISE · A portfolio project in practical NLP</div>", unsafe_allow_html=True)
