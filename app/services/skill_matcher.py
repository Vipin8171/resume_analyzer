"""Rule-based skill matching without heavy dependencies."""
from typing import List
from app.models.resume_schema import Resume, JobDescription, AnalysisResult
from app.utils.scoring import compute_compatibility
from app.utils.text_cleaner import normalize_text

# Minimal vocabulary for Phase 1; extend later if needed
DEFAULT_SKILL_VOCAB = [
    "python","fastapi","flask","django","nlp","spacy","nltk","bert","transformers",
    "pandas","numpy","sql","mongodb","postgres","aws","docker","kubernetes","spark",
]


def extract_skills_from_text(text: str) -> List[str]:
    t = normalize_text(text)
    tokens = set(t.split())
    return sorted([s for s in DEFAULT_SKILL_VOCAB if s in tokens])


def analyze_resume_vs_jd(resume: Resume, jd: JobDescription) -> AnalysisResult:
    jd_skills = extract_skills_from_text(jd.title + "\n" + jd.description)

    score, matched, missing = compute_compatibility(resume.skills, jd_skills)

    irrelevant = [s for s in resume.skills if s not in jd_skills]

    suggestions = {
        "add": missing,
        "remove": [],
    }

    return AnalysisResult(
        compatibility_score=score,
        matched_skills=matched,
        missing_skills=missing,
        irrelevant_content=irrelevant,
        suggestions=suggestions,
    )