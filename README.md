# MatchWise — AI Resume & Job Match Analyzer

MatchWise is a beginner-friendly NLP/ML portfolio project. It compares a resume with a job description, estimates their text similarity, detects relevant skills, and produces practical improvement suggestions.

## Features

- Upload a resume as PDF, DOCX, or TXT, or paste its text.
- Paste a job description.
- Calculate TF-IDF cosine similarity between the two documents.
- Detect skills from both documents using a curated skills dictionary.
- Show matched skills, skills not detected in the resume, and shared keywords.
- Download a Markdown match report.
- Run locally without an external AI API or API key.

## Tech stack

- **Python** — application logic
- **Streamlit** — interactive web interface
- **scikit-learn** — TF-IDF vectorization and cosine similarity
- **pypdf / python-docx** — PDF and Word text extraction

## Run locally (Windows)

1. Install Python 3.10 or newer.
2. Extract this project folder and open PowerShell inside it.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   streamlit run app.py
   ```

6. Open the local URL Streamlit prints in the terminal (usually `http://localhost:8501`).

**Shortcut:** On Windows, double-click `launch_windows.bat` to create the virtual environment, install dependencies, and start the app automatically.

## Try the included demo

Use `sample_data/demo_resume.txt` as the resume and `sample_data/demo_job_description.txt` as the job description to see a sample analysis. The sample candidate is fictional.

## How the ML/NLP works

### 1. Text vectorization

The resume and job description are converted into TF-IDF vectors using unigrams and bigrams. TF-IDF gives higher importance to terms that are useful in a document and less common across the compared text.

### 2. Text similarity

Cosine similarity measures the angle between the two TF-IDF vectors. The result is shown as a percentage.

### 3. Skill matching

A small curated dictionary detects common technical, analytics, software, and electrical-engineering skills. The app compares the skills detected in the two documents.

### 4. Overall score

When the job description contains recognized skills:

`Overall score = 45% × text similarity + 55% × skill coverage`

`Skill coverage = matched recognized job skills / all recognized job skills × 100`

When no job-description skills are detected, the overall score uses text similarity alone. The UI displays each component so the score is explainable.

## Project structure

```text
ai_resume_matcher/
├── app.py                  # Streamlit interface
├── src/
│   ├── __init__.py
│   └── analyzer.py         # NLP, skill extraction, scoring, report
├── tests/
│   └── test_analyzer.py    # Basic automated tests
├── requirements.txt
├── launch_windows.bat
├── sample_data/            # Fictional demo resume and job description
├── README.md
└── .gitignore
```

## Test the matching engine

```powershell
python -m unittest discover -s tests -v
```

## Limitations and honest interpretation

- This is a lightweight NLP matching aid, not a hiring prediction system.
- TF-IDF measures wording overlap; it does not understand context as a modern language model would.
- The skill detector can miss synonyms, abbreviations, and skills not yet in its dictionary.
- A missing skill means **not detected in the provided resume text**, not proof that a person lacks that skill.
- Never add a skill or experience to a resume unless it is genuine and can be explained in an interview.

## Good next upgrades

1. Add semantic embeddings (for example, Sentence Transformers) and compare them against the TF-IDF baseline.
2. Add a larger, editable skill taxonomy for specific job families.
3. Add bullet-level feedback and highlight evidence in the resume for each matched skill.
4. Add a small evaluation dataset and report precision/recall for skill extraction.
5. Deploy the Streamlit app and add a demo video to the GitHub README.

## Suggested resume project entry

**MatchWise — NLP-Based Resume & Job Description Matcher**  
Built a Streamlit application that compares resumes with job descriptions using TF-IDF vectorization and cosine similarity. Implemented skill extraction, weighted match scoring, missing-skill analysis, and downloadable feedback reports using Python and scikit-learn.
