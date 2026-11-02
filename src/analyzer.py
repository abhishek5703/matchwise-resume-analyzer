"""Core NLP matching logic for the AI Resume & Job Match Analyzer.

This project uses transparent, local NLP techniques (TF-IDF + cosine similarity)
with a curated skills dictionary. It does not call an external AI service.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Canonical skill names map to common spellings and aliases.
SKILL_ALIASES: Dict[str, Sequence[str]] = {
    "Python": ("python",),
    "C++": ("c++", "cpp"),
    "C": ("c programming", "c language"),
    "C#": ("c#", "c sharp"),
    "Java": ("java",),
    "SQL": ("sql", "structured query language"),
    "Machine Learning": ("machine learning", "ml"),
    "Deep Learning": ("deep learning",),
    "Natural Language Processing": ("natural language processing", "nlp"),
    "Generative AI": ("generative ai", "gen ai", "llm", "large language model"),
    "Data Analysis": ("data analysis", "data analytics", "analytics"),
    "Statistics": ("statistics", "statistical analysis"),
    "Power BI": ("power bi", "powerbi"),
    "Tableau": ("tableau",),
    "Excel": ("excel", "microsoft excel", "advanced excel"),
    "Pandas": ("pandas",),
    "NumPy": ("numpy",),
    "Matplotlib": ("matplotlib",),
    "Scikit-learn": ("scikit-learn", "sklearn", "scikit learn"),
    "TensorFlow": ("tensorflow",),
    "PyTorch": ("pytorch",),
    "Git": ("git", "github"),
    "Docker": ("docker",),
    "Linux": ("linux",),
    "AWS": ("aws", "amazon web services"),
    "Azure": ("azure", "microsoft azure"),
    "Google Cloud": ("google cloud", "gcp"),
    "REST APIs": ("rest api", "rest apis", "restful api", "restful apis"),
    "HTML": ("html",),
    "CSS": ("css",),
    "JavaScript": ("javascript", "js"),
    "React": ("react", "react.js", "reactjs"),
    "Node.js": ("node.js", "nodejs", "node js"),
    "MongoDB": ("mongodb", "mongo db"),
    "MySQL": ("mysql",),
    "PostgreSQL": ("postgresql", "postgres"),
    "Streamlit": ("streamlit",),
    "Problem Solving": ("problem solving", "analytical thinking"),
    "Communication": ("communication", "communication skills", "verbal communication", "written communication"),
    "Leadership": ("leadership", "team leadership"),
    "Project Management": ("project management", "program management"),
    "Power Systems": ("power systems", "power system analysis"),
    "MATLAB": ("matlab",),
    "Simulink": ("simulink",),
    "Embedded Systems": ("embedded systems", "embedded software"),
    "Microcontrollers": ("microcontroller", "microcontrollers", "mcu"),
    "RTOS": ("rtos", "real-time operating system", "real time operating system"),
    "UART": ("uart",),
    "SPI": ("spi",),
    "I2C": ("i2c", "i²c"),
    "Power Electronics": ("power electronics",),
    "Electrical Machines": ("electrical machines", "electric machines"),
    "Renewable Energy": ("renewable energy", "solar energy", "photovoltaic", "solar pv"),
}


@dataclass
class MatchResult:
    similarity_score: float
    skill_coverage: float
    overall_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    resume_skills: List[str]
    job_skills: List[str]
    top_shared_terms: List[str]
    suggestions: List[str]


# Aliases that are also ordinary English words ("excel in a role", "react quickly").
# These only count when written capitalized/uppercase, as a tool name would be.
AMBIGUOUS_ALIASES = {"excel", "react"}
_NOT_A_TOOL_AFTER = r"(?!\s+(?:in|at|as|to)\b)"


def _contains_phrase(text: str, phrase: str) -> bool:
    """Match phrases without accidentally matching inside unrelated words."""
    boundary_before, boundary_after = r"(?<![A-Za-z0-9])", r"(?![A-Za-z0-9])"
    if phrase.lower() in AMBIGUOUS_ALIASES:
        forms = "|".join(re.escape(f) for f in {phrase.capitalize(), phrase.upper()})
        pattern = rf"{boundary_before}(?:{forms}){boundary_after}{_NOT_A_TOOL_AFTER}"
        return re.search(pattern, text) is not None
    pattern = rf"{boundary_before}{re.escape(phrase.lower())}{boundary_after}"
    return re.search(pattern, text.lower()) is not None


def extract_skills(text: str) -> List[str]:
    """Return canonical skills found in text, in dictionary order."""
    found: List[str] = []
    for canonical, aliases in SKILL_ALIASES.items():
        if any(_contains_phrase(text, alias) for alias in aliases):
            found.append(canonical)
    return found


def _top_shared_terms(resume_text: str, job_text: str, limit: int = 8) -> List[str]:
    """Find high-signal terms (words and phrases) that appear in both documents."""
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=3000)
    matrix = vectorizer.fit_transform([resume_text, job_text])
    names = vectorizer.get_feature_names_out()
    resume_weights = matrix[0].toarray().ravel()
    job_weights = matrix[1].toarray().ravel()
    candidates: List[Tuple[float, str]] = []
    for idx, term in enumerate(names):
        if resume_weights[idx] > 0 and job_weights[idx] > 0 and not term.isdigit():
            candidates.append((float(job_weights[idx]), term))
    candidates.sort(reverse=True)
    return [term for _, term in candidates[:limit]]


def analyze_match(resume_text: str, job_text: str) -> MatchResult:
    """Compare a resume and job description using TF-IDF and skill coverage.

    Overall score = 45% text similarity + 55% required-skill coverage.
    If no recognized skills are found in the job description, similarity is used
    as the overall score instead of pretending skill coverage is zero.
    """
    resume_text = resume_text.strip()
    job_text = job_text.strip()
    if len(resume_text) < 30:
        raise ValueError("Please provide a longer resume (at least 30 characters).")
    if len(job_text) < 30:
        raise ValueError("Please provide a longer job description (at least 30 characters).")

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)
    try:
        matrix = vectorizer.fit_transform([resume_text, job_text])
    except ValueError as exc:
        raise ValueError("The documents do not contain enough readable text to compare.") from exc

    similarity = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0]) * 100
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)
    matched = [skill for skill in job_skills if skill in resume_skills]
    missing = [skill for skill in job_skills if skill not in resume_skills]

    if job_skills:
        coverage = len(matched) / len(job_skills) * 100
        overall = 0.45 * similarity + 0.55 * coverage
    else:
        coverage = similarity
        overall = similarity

    suggestions: List[str] = []
    if missing:
        suggestions.append(
            "The job description mentions " + ", ".join(missing[:6])
            + ". Add these only if you genuinely have the skill; support each one with a project, course, or work example."
        )
    if similarity < 35:
        suggestions.append(
            "Your resume wording is quite different from the job description. Rework the summary and project bullets to clearly describe relevant work using accurate terminology from the role."
        )
    elif similarity < 60:
        suggestions.append(
            "Make the most relevant projects and experience easier to find. Put role-relevant tools, methods, and outcomes near the top of each bullet."
        )
    else:
        suggestions.append(
            "Your wording has a good overlap with this role. Strengthen bullets with measurable outcomes, scale, and your individual contribution."
        )
    suggestions.append(
        "Tailor your resume for this specific role, but do not add keywords or claim experience that you cannot explain in an interview."
    )

    return MatchResult(
        similarity_score=round(similarity, 1),
        skill_coverage=round(coverage, 1),
        overall_score=round(overall, 1),
        matched_skills=matched,
        missing_skills=missing,
        resume_skills=resume_skills,
        job_skills=job_skills,
        top_shared_terms=_top_shared_terms(resume_text, job_text),
        suggestions=suggestions,
    )


def build_report(result: MatchResult) -> str:
    """Create a portable Markdown report for download."""
    matched = ", ".join(result.matched_skills) or "None detected"
    missing = ", ".join(result.missing_skills) or "None detected"
    resume = ", ".join(result.resume_skills) or "None detected"
    job = ", ".join(result.job_skills) or "None detected"
    terms = ", ".join(result.top_shared_terms) or "None detected"
    suggestions = "\n".join(f"- {item}" for item in result.suggestions)
    return f"""# Resume & Job Match Report

> This is an informational NLP comparison, not a hiring prediction or guarantee.

## Match overview
- **Overall match score:** {result.overall_score}%
- **Text similarity (TF-IDF):** {result.similarity_score}%
- **Recognized skill coverage:** {result.skill_coverage}%

## Skills comparison
- **Skills detected in resume:** {resume}
- **Skills detected in job description:** {job}
- **Matched skills:** {matched}
- **Skills not detected in resume:** {missing}

## Shared terms
{terms}

## Suggested improvements
{suggestions}

## Scoring method
When recognized job-description skills are available, the overall score is 45% TF-IDF cosine similarity and 55% recognized skill coverage. If no skills are recognized in the job description, the overall score falls back to text similarity. Results depend on the skill dictionary and wording of the documents.
"""
