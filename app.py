import io
from html import escape
from pathlib import Path

import streamlit as st

from src.analyzer import analyze_match, build_report


st.set_page_config(
    page_title="MatchWise | AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Design system
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

:root {
  --bg: #07080F;
  --surface: rgba(255,255,255,.035);
  --surface-2: rgba(255,255,255,.06);
  --border: rgba(255,255,255,.09);
  --border-hi: rgba(139,124,255,.45);
  --text: #ECEEF8;
  --muted: #9AA0B8;
  --violet: #8B7CFF;
  --blue: #4EA8FF;
  --teal: #2DE1C2;
  --amber: #FFC857;
  --rose: #FF6B8B;
  --grad: linear-gradient(120deg, #8B7CFF 0%, #4EA8FF 50%, #2DE1C2 100%);
}

html, body, [class*="css"], .stApp, .stMarkdown, button, input, textarea {
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif !important;
}

/* ---------- App canvas ---------- */
.stApp {
  background:
    radial-gradient(900px 500px at 8% -8%, rgba(139,124,255,.20), transparent 60%),
    radial-gradient(800px 500px at 100% 0%, rgba(45,225,194,.12), transparent 60%),
    radial-gradient(700px 600px at 50% 110%, rgba(78,168,255,.10), transparent 60%),
    var(--bg);
  background-attachment: fixed;
}
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(16,18,30,.95), rgba(9,10,18,.98));
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
.brand { display:flex; align-items:center; gap:.7rem; margin-bottom:.2rem; }
.brand-mark {
  width:40px; height:40px; border-radius:12px; background: var(--grad);
  display:grid; place-items:center; font-size:1.25rem;
  box-shadow: 0 8px 24px -6px rgba(139,124,255,.7);
}
.brand-name { font-size:1.25rem; font-weight:800; letter-spacing:-.03em; }
.brand-tag { color: var(--muted); font-size:.8rem; margin:0 0 .4rem 0; }
.side-h { font-size:.7rem; letter-spacing:.14em; text-transform:uppercase; color: var(--muted); font-weight:700; margin:1.2rem 0 .7rem 0; }
.step { display:flex; gap:.75rem; margin-bottom:.8rem; align-items:flex-start; }
.step-n {
  flex:0 0 auto; width:26px; height:26px; border-radius:8px; display:grid; place-items:center;
  font-size:.75rem; font-weight:700; color:#fff; background: rgba(139,124,255,.2);
  border:1px solid rgba(139,124,255,.45);
}
.step-t { font-size:.86rem; color:#C9CDE0; line-height:1.4; }
.step-t b { color: var(--text); }
.privacy {
  border:1px solid rgba(45,225,194,.3); background: rgba(45,225,194,.07);
  border-radius:14px; padding:.8rem .9rem; font-size:.82rem; color:#BFEFE6; line-height:1.45;
}
.stack { display:flex; flex-wrap:wrap; gap:.35rem; }
.stack span {
  font-size:.72rem; padding:.22rem .55rem; border-radius:8px; color:#C9CDE0;
  background: var(--surface-2); border:1px solid var(--border);
}

/* ---------- Hero ---------- */
.hero {
  position:relative; overflow:hidden; padding:2.6rem 2.4rem; border-radius:28px; margin-bottom:1.8rem;
  border:1px solid var(--border);
  background:
    radial-gradient(520px 260px at 90% 0%, rgba(139,124,255,.30), transparent 70%),
    radial-gradient(420px 260px at 0% 100%, rgba(45,225,194,.18), transparent 70%),
    rgba(255,255,255,.03);
  backdrop-filter: blur(14px);
  box-shadow: 0 30px 80px -40px rgba(139,124,255,.55), inset 0 1px 0 rgba(255,255,255,.08);
  animation: rise .7s cubic-bezier(.2,.8,.2,1) both;
}
.hero::after {
  content:""; position:absolute; inset:0; pointer-events:none; opacity:.35;
  background-image: radial-gradient(rgba(255,255,255,.14) 1px, transparent 1px);
  background-size: 22px 22px;
  mask-image: linear-gradient(120deg, transparent 35%, #000 100%);
  -webkit-mask-image: linear-gradient(120deg, transparent 35%, #000 100%);
}
.eyebrow {
  display:inline-flex; align-items:center; gap:.5rem; padding:.3rem .75rem; border-radius:999px;
  font-size:.74rem; font-weight:600; color:#D8D3FF; letter-spacing:.04em;
  background: rgba(139,124,255,.14); border:1px solid rgba(139,124,255,.4);
}
.eyebrow i { width:7px; height:7px; border-radius:50%; background: var(--teal); box-shadow:0 0 10px var(--teal); animation: pulse 2s infinite; }
.hero h1 {
  position:relative; z-index:1; margin:1rem 0 .7rem 0; font-size:3.1rem; line-height:1.05;
  font-weight:800; letter-spacing:-.045em; padding:0;
}
.grad-text { background: var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
.hero p { position:relative; z-index:1; margin:0; max-width:620px; color:#B4B9D0; font-size:1.06rem; line-height:1.6; }
.hero-stats { position:relative; z-index:1; display:flex; gap:2rem; margin-top:1.6rem; flex-wrap:wrap; }
.hero-stats div b { display:block; font-size:1.25rem; font-weight:800; letter-spacing:-.02em; }
.hero-stats div span { font-size:.76rem; color: var(--muted); }

/* ---------- Panel headings ---------- */
.panel-head { display:flex; align-items:center; gap:.8rem; margin: .2rem 0 .9rem 0; }
.panel-num {
  font-family:'JetBrains Mono', monospace; font-size:.8rem; font-weight:500; color:#fff;
  padding:.28rem .55rem; border-radius:8px; background: var(--grad);
}
.panel-title { font-size:1.25rem; font-weight:700; letter-spacing:-.02em; }
.panel-sub { color: var(--muted); font-size:.85rem; margin:-.5rem 0 1rem 0; }

/* ---------- Inputs ---------- */
div[data-testid="stFileUploader"] section {
  background: var(--surface); border:1.5px dashed rgba(139,124,255,.45); border-radius:18px;
  padding:1.3rem; transition: all .25s ease;
}
div[data-testid="stFileUploader"] section:hover {
  background: rgba(139,124,255,.08); border-color: var(--violet); box-shadow: 0 0 0 4px rgba(139,124,255,.1);
}
div[data-testid="stFileUploader"] button {
  border-radius:10px; border:1px solid var(--border-hi); background: rgba(139,124,255,.12); color: var(--text);
}
.stTextArea textarea {
  background: var(--surface) !important; border:1px solid var(--border) !important; border-radius:16px !important;
  color: var(--text) !important; padding: 1rem !important; line-height:1.55; transition: all .2s ease;
}
.stTextArea textarea:focus { border-color: var(--violet) !important; box-shadow: 0 0 0 4px rgba(139,124,255,.16) !important; }
.stTextArea textarea::placeholder { color:#6B7190 !important; }
label, .stTextArea label p, div[data-testid="stFileUploader"] label p { color:#C9CDE0 !important; font-weight:600 !important; font-size:.88rem !important; }
div[data-testid="stAlert"] { border-radius:14px; border:1px solid var(--border); backdrop-filter: blur(8px); }

/* ---------- Buttons ---------- */
.stButton button[kind="primary"], .stDownloadButton button {
  position:relative; border:0; border-radius:14px; padding:.95rem 1.4rem; font-weight:700; font-size:1.02rem;
  letter-spacing:-.01em; color:#fff; background: linear-gradient(120deg, #7A6BFF, #4EA8FF 55%, #2DE1C2);
  background-size:160% 100%; background-position:0% 0;
  box-shadow: 0 14px 34px -12px rgba(100,130,255,.8), inset 0 1px 0 rgba(255,255,255,.3);
  transition: transform .2s ease, box-shadow .2s ease, background-position .5s ease;
}
.stButton button[kind="primary"]:hover, .stDownloadButton button:hover {
  transform: translateY(-2px); background-position:100% 0; color:#fff;
  box-shadow: 0 20px 44px -12px rgba(100,130,255,.95), inset 0 1px 0 rgba(255,255,255,.35);
}
.stButton button[kind="primary"]:active, .stDownloadButton button:active { transform: translateY(0) scale(.99); }
.stDownloadButton button p, .stButton button[kind="primary"] p { color:#fff !important; font-weight:700; }

/* ---------- Results ---------- */
.results-head { margin: 2.4rem 0 1.2rem 0; animation: rise .6s ease both; }
.results-head h2 { font-size:2rem; font-weight:800; letter-spacing:-.04em; margin:0; padding:0; }
.results-head p { color: var(--muted); margin:.3rem 0 0 0; }

.card {
  background: var(--surface); border:1px solid var(--border); border-radius:22px; padding:1.5rem;
  backdrop-filter: blur(12px); box-shadow: inset 0 1px 0 rgba(255,255,255,.05);
  animation: rise .6s cubic-bezier(.2,.8,.2,1) both; height:100%;
}
.card-label { font-size:.7rem; letter-spacing:.14em; text-transform:uppercase; color: var(--muted); font-weight:700; margin-bottom:1rem; }

/* score ring */
.gauge-wrap { display:flex; align-items:center; gap:1.5rem; flex-wrap:wrap; }
.gauge { position:relative; width:170px; height:170px; flex:0 0 auto; }
.gauge svg { transform: rotate(-90deg); width:100%; height:100%; overflow:visible; }
.gauge .track { fill:none; stroke: rgba(255,255,255,.07); stroke-width:13; }
.gauge .arc {
  fill:none; stroke-width:13; stroke-linecap:round; stroke-dasharray: 440; stroke-dashoffset: 440;
  filter: drop-shadow(0 0 10px var(--glow)); animation: fill 1.6s cubic-bezier(.2,.8,.2,1) .2s forwards;
}
.gauge-center { position:absolute; inset:0; display:grid; place-content:center; text-align:center; }
.gauge-center b { font-size:3rem; font-weight:800; letter-spacing:-.05em; line-height:1; }
.gauge-center b small { font-size:1.3rem; opacity:.7; }
.gauge-center span { font-size:.72rem; color: var(--muted); letter-spacing:.12em; text-transform:uppercase; margin-top:.35rem; font-weight:600; }
.verdict { flex:1 1 170px; min-width:0; }
.badge { display:inline-block; padding:.3rem .75rem; border-radius:999px; font-size:.76rem; font-weight:700; letter-spacing:.03em; margin-bottom:.8rem; }
.verdict h3 { font-size:1.35rem; font-weight:700; letter-spacing:-.025em; margin:0 0 .5rem 0; padding:0; }
.verdict p { color:#B4B9D0; line-height:1.6; margin:0; font-size:.95rem; }

/* component bars */
.bar-row { margin-bottom:1.25rem; }
.bar-row:last-child { margin-bottom:0; }
.bar-top { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:.5rem; }
.bar-top span { font-size:.88rem; color:#C9CDE0; font-weight:500; }
.bar-top b { font-size:1.15rem; font-weight:700; letter-spacing:-.02em; }
.bar-track { height:9px; border-radius:99px; background: rgba(255,255,255,.07); overflow:hidden; }
.bar-fill { height:100%; border-radius:99px; width:0; animation: grow 1.3s cubic-bezier(.2,.8,.2,1) .3s forwards; }
.bar-note { font-size:.75rem; color: var(--muted); margin-top:.4rem; }

/* skill chips */
.chip-title { display:flex; align-items:center; justify-content:space-between; margin-bottom:.9rem; }
.chip-title .t { font-size:1rem; font-weight:700; letter-spacing:-.015em; }
.count { font-family:'JetBrains Mono', monospace; font-size:.72rem; padding:.15rem .5rem; border-radius:7px; background: var(--surface-2); color:#C9CDE0; border:1px solid var(--border); }
.chips { display:flex; flex-wrap:wrap; gap:.45rem; }
.chip {
  display:inline-flex; align-items:center; gap:.4rem; padding:.38rem .8rem; border-radius:999px;
  font-size:.82rem; font-weight:500; border:1px solid var(--border); background: var(--surface-2); color:#D8DBEC;
  transition: transform .15s ease, box-shadow .15s ease;
}
.chip:hover { transform: translateY(-2px); }
.chip.ok   { color:#9FF3E1; background: rgba(45,225,194,.10); border-color: rgba(45,225,194,.35); }
.chip.ok:hover { box-shadow:0 6px 18px -8px rgba(45,225,194,.8); }
.chip.miss { color:#FFDE9A; background: rgba(255,200,87,.09); border-color: rgba(255,200,87,.35); }
.chip.miss:hover { box-shadow:0 6px 18px -8px rgba(255,200,87,.8); }
.chip.info { color:#BFD9FF; background: rgba(78,168,255,.09); border-color: rgba(78,168,255,.3); }
.chip.kw   { color:#D8D3FF; background: rgba(139,124,255,.12); border-color: rgba(139,124,255,.35); }
.empty { color: var(--muted); font-size:.88rem; font-style:italic; }

/* suggestions */
.tips { display:grid; gap:.8rem; }
.tip { display:flex; gap:1rem; padding:1rem 1.1rem; border-radius:16px; background: rgba(255,255,255,.03); border:1px solid var(--border); transition: all .2s ease; }
.tip:hover { background: rgba(139,124,255,.07); border-color: var(--border-hi); transform: translateX(4px); }
.tip-n { flex:0 0 auto; width:30px; height:30px; border-radius:10px; display:grid; place-items:center; font-weight:700; font-size:.85rem; background: var(--grad); color:#fff; }
.tip-t { color:#D0D4E6; line-height:1.6; font-size:.93rem; }

.disclaimer { margin-top:1.4rem; padding:1rem 1.2rem; border-radius:14px; border:1px solid var(--border); background: var(--surface); color: var(--muted); font-size:.8rem; line-height:1.55; }

/* empty state */
.empty-state {
  margin-top:1.4rem; padding:1.6rem; border-radius:20px; border:1px dashed var(--border);
  background: var(--surface); text-align:center; color: var(--muted);
}
.empty-state b { color: var(--text); }
.empty-state .ico { font-size:1.8rem; margin-bottom:.4rem; }

.foot { text-align:center; margin-top:3rem; color:#5F657F; font-size:.75rem; letter-spacing:.2em; }

.grid { display:grid; gap:1.5rem; margin-bottom:1.5rem; align-items:stretch; }
.grid.g2 { grid-template-columns: 1fr 1fr; }
.grid.g-hero { grid-template-columns: 1.25fr 1fr; }
.grid .card { height:auto; }
@media (max-width: 860px) { .grid.g2, .grid.g-hero { grid-template-columns: 1fr; } }

/* ---------- Motion ---------- */
@keyframes rise  { from { opacity:0; transform: translateY(16px); } to { opacity:1; transform:none; } }
@keyframes fill  { to { stroke-dashoffset: var(--off); } }
@keyframes grow  { to { width: var(--w); } }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:.35; } }
@media (prefers-reduced-motion: reduce) { * { animation-duration: .01ms !important; animation-delay: 0s !important; } }

@media (max-width: 720px) {
  .hero { padding:1.6rem 1.3rem; }
  .hero h1 { font-size:2.1rem; }
  .gauge { width:160px; height:160px; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def read_resume(uploaded_file) -> str:
    """Extract text from TXT, PDF, and DOCX uploads."""
    suffix = Path(uploaded_file.name).suffix.lower()
    raw = uploaded_file.getvalue()
    if suffix == ".txt":
        return raw.decode("utf-8", errors="ignore")
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        from docx import Document

        document = Document(io.BytesIO(raw))
        parts = [p.text for p in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                parts.append(" ".join(cell.text for cell in row.cells))
        return "\n".join(parts)
    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")


def panel_head(num: str, title: str, sub: str) -> None:
    st.markdown(
        f'<div class="panel-head"><span class="panel-num">{num}</span><span class="panel-title">{title}</span></div>'
        f'<div class="panel-sub">{sub}</div>',
        unsafe_allow_html=True,
    )


def chips_card(title: str, icon: str, items: list[str], kind: str, empty: str) -> str:
    body = (
        '<div class="chips">' + "".join(f'<span class="chip {kind}">{escape(i)}</span>' for i in items) + "</div>"
        if items
        else f'<div class="empty">{escape(empty)}</div>'
    )
    return (
        f'<div class="card"><div class="chip-title"><span class="t">{icon} {escape(title)}</span>'
        f'<span class="count">{len(items)}</span></div>{body}</div>'
    )


def tone(score: float) -> dict:
    if score >= 75:
        return dict(color="#2DE1C2", bg="rgba(45,225,194,.14)", label="STRONG MATCH", head="Strong alignment detected",
                    text="Focus on making your strongest evidence easy to see — lead with impact and measurable results.")
    if score >= 50:
        return dict(color="#4EA8FF", bg="rgba(78,168,255,.14)", label="MODERATE MATCH", head="Moderate alignment",
                    text="A few targeted resume improvements could make your fit much clearer to a reader.")
    return dict(color="#FFC857", bg="rgba(255,200,87,.14)", label="LOW MATCH", head="Low detected alignment",
                text="Review the missing requirements below before applying, and tailor your story to the role.")


def gauge_html(score: float) -> str:
    t = tone(score)
    pct = min(max(score, 0), 100)
    circumference = 440  # 2 * pi * r (r = 70)
    offset = circumference * (1 - pct / 100)
    return f"""
    <div class="card">
      <div class="card-label">Overall match score</div>
      <div class="gauge-wrap">
        <div class="gauge">
          <svg viewBox="0 0 160 160">
            <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#8B7CFF"/><stop offset="100%" stop-color="{t['color']}"/>
            </linearGradient></defs>
            <circle class="track" cx="80" cy="80" r="70"/>
            <circle class="arc" cx="80" cy="80" r="70" stroke="url(#g)" style="--off:{offset:.1f}; --glow:{t['color']}88"/>
          </svg>
          <div class="gauge-center"><b>{score:.0f}<small>%</small></b><span>match</span></div>
        </div>
        <div class="verdict">
          <span class="badge" style="color:{t['color']};background:{t['bg']};border:1px solid {t['color']}55">{t['label']}</span>
          <h3>{t['head']}</h3>
          <p>{t['text']}</p>
        </div>
      </div>
    </div>"""


def bars_html(similarity: float, coverage: float) -> str:
    def row(label: str, value: float, grad: str, note: str) -> str:
        v = min(max(value, 0), 100)
        return (
            f'<div class="bar-row"><div class="bar-top"><span>{label}</span><b>{value:.1f}%</b></div>'
            f'<div class="bar-track"><div class="bar-fill" style="--w:{v:.1f}%;background:{grad}"></div></div>'
            f'<div class="bar-note">{note}</div></div>'
        )

    return (
        '<div class="card"><div class="card-label">Score breakdown</div>'
        + row("Text similarity", similarity, "linear-gradient(90deg,#8B7CFF,#4EA8FF)", "TF-IDF cosine similarity · 45% weight")
        + row("Skill coverage", coverage, "linear-gradient(90deg,#4EA8FF,#2DE1C2)", "Matched job skills ÷ recognized job skills · 55% weight")
        + "</div>"
    )


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">🎯</div><div class="brand-name">MatchWise</div></div>'
        '<p class="brand-tag">Resume intelligence, explained.</p>'
        '<div class="side-h">How it works</div>'
        '<div class="step"><div class="step-n">1</div><div class="step-t"><b>Extract</b> text from your resume.</div></div>'
        '<div class="step"><div class="step-n">2</div><div class="step-t"><b>Compare</b> it with the job using TF-IDF &amp; cosine similarity.</div></div>'
        '<div class="step"><div class="step-n">3</div><div class="step-t"><b>Detect</b> skills with a curated dictionary.</div></div>'
        '<div class="step"><div class="step-n">4</div><div class="step-t"><b>Report</b> an explainable match &amp; next steps.</div></div>'
        '<div class="side-h">Privacy</div>'
        '<div class="privacy">🔒 Analysis runs locally in this session. Your resume is never sent to an external AI API.</div>'
        '<div class="side-h">Built with</div>'
        '<div class="stack"><span>Python</span><span>Streamlit</span><span>scikit-learn</span><span>NLP</span></div>',
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <span class="eyebrow"><i></i>AI RESUME ANALYZER</span>
      <h1>Find your fit.<br><span class="grad-text">Improve your story.</span></h1>
      <p>See how closely your resume aligns with a job description — and exactly what to improve next.
         Transparent scoring, no black box.</p>
      <div class="hero-stats">
        <div><b>TF-IDF</b><span>text similarity</span></div>
        <div><b>50+</b><span>skills tracked</span></div>
        <div><b>100%</b><span>runs locally</span></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------------
left, right = st.columns(2, gap="large")
with left:
    panel_head("01", "Your resume", "Upload a file or paste the text directly.")
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
    panel_head("02", "Target job", "Paste the full posting for the best comparison.")
    job_text = st.text_area(
        "Paste the job description",
        height=330,
        placeholder="Paste the responsibilities, requirements, qualifications, and preferred skills...",
    )
    st.caption("Tip: Include the full requirements section for a more useful comparison.")

st.write("")
analyze = st.button("✨ Analyze my match", type="primary", width="stretch")

if analyze:
    if not resume_text.strip() or not job_text.strip():
        st.warning("Please add both your resume and the job description before analyzing.")
    else:
        try:
            with st.spinner("Analyzing your match…"):
                result = analyze_match(resume_text, job_text)
                st.session_state["match_result"] = result
                st.session_state["match_report"] = build_report(result)
        except ValueError as exc:
            st.error(str(exc))

# ----------------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------------
result = st.session_state.get("match_result")
if result:
    st.markdown(
        '<div class="results-head"><h2>Your match <span class="grad-text">report</span></h2>'
        "<p>A transparent comparison of the text and skills found in the two documents.</p></div>",
        unsafe_allow_html=True,
    )

    def grid(kind: str, *cards: str) -> str:
        return f'<div class="grid {kind}">' + "".join(cards) + "</div>"

    st.markdown(
        grid("g-hero", gauge_html(result.overall_score), bars_html(result.similarity_score, result.skill_coverage))
        + grid(
            "g2",
            chips_card("Matched skills", "✅", result.matched_skills, "ok", "No recognized skills matched yet."),
            chips_card("Skills not detected in your resume", "＋", result.missing_skills, "miss",
                       "No missing skills detected from the current dictionary."),
        )
        + grid(
            "g2",
            chips_card("Skills in your resume", "🧩", result.resume_skills, "info",
                       "No skills from the current dictionary were detected."),
            chips_card("Skills in the job description", "📌", result.job_skills, "info",
                       "No recognized skills found in the job description."),
        ),
        unsafe_allow_html=True,
    )

    tips = "".join(
        f'<div class="tip"><div class="tip-n">{i}</div><div class="tip-t">{escape(s)}</div></div>'
        for i, s in enumerate(result.suggestions, 1)
    )
    st.markdown(
        f'<div class="card"><div class="card-label">What to improve</div><div class="tips">{tips}</div></div>',
        unsafe_allow_html=True,
    )

    if result.top_shared_terms:
        st.write("")
        st.markdown(
            chips_card("Shared keywords", "🔑", result.top_shared_terms, "kw",
                       "No shared keywords found."),
            unsafe_allow_html=True,
        )

    st.write("")
    st.download_button(
        "⬇️ Download match report",
        data=st.session_state["match_report"],
        file_name="matchwise_report.md",
        mime="text/markdown",
        width="stretch",
    )
    st.markdown(
        '<div class="disclaimer"><b>Important:</b> This score is an educational NLP estimate, not a recruiter score, '
        "hiring prediction, or guarantee. The skill dictionary is curated and may miss synonyms or domain-specific terms.</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="empty-state"><div class="ico">📊</div>'
        "Add your resume and a job description, then select <b>Analyze my match</b> to see your report.</div>",
        unsafe_allow_html=True,
    )

st.markdown("<div class='foot'>MATCHWISE · A PORTFOLIO PROJECT IN PRACTICAL NLP</div>", unsafe_allow_html=True)