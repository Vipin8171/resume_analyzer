"""Compatibility scoring utilities."""
from typing import List, Tuple

def compute_compatibility(resume_skills: List[str], jd_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Return a tuple of (score_0_to_10, matched_skills, missing_skills).
    Score = 10 * (|matched| / max(1, |jd_skills|)), bounded [0, 10].
    """
    rs = set(s.lower() for s in resume_skills)
    js = set(s.lower() for s in jd_skills)

    matched = sorted(rs.intersection(js))
    missing = sorted(js.difference(rs))

    denom = max(1, len(js))
    score = 10.0 * (len(matched) / denom)
    return round(score, 2), matched, missing
def calculate_compatibility_score(resume_skills, job_description_skills):
    """
    Calculate the compatibility score between resume skills and job description skills.

    Parameters:
    - resume_skills (set): A set of skills extracted from the resume.
    - job_description_skills (set): A set of skills extracted from the job description.

    Returns:
    - float: A compatibility score between 0 and 10.
    """
    if not job_description_skills:
        return 0.0

    matched_skills = resume_skills.intersection(job_description_skills)
    skill_match_percentage = len(matched_skills) / len(job_description_skills)

    # Calculate score based on skill match percentage
    score = skill_match_percentage * 10
    return round(score, 2)


def analyze_skills(resume_skills, job_description_skills):
    """
    Analyze the skills from the resume against the job description.

    Parameters:
    - resume_skills (set): A set of skills extracted from the resume.
    - job_description_skills (set): A set of skills extracted from the job description.

    Returns:
    - dict: A dictionary containing matched skills, missing skills, and score.
    """
    matched_skills = resume_skills.intersection(job_description_skills)
    missing_skills = job_description_skills.difference(resume_skills)

    compatibility_score = calculate_compatibility_score(resume_skills, job_description_skills)

    return {
        "matched_skills": list(matched_skills),
        "missing_skills": list(missing_skills),
        "compatibility_score": compatibility_score
    }