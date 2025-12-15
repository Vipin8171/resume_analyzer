from pydantic import BaseModel
from typing import List, Optional, Dict

class OnlineProfile(BaseModel):
    label: str
    url: str

class Project(BaseModel):
    name: str
    technologies: List[str]

class Resume(BaseModel):
    name: str
    email: str
    phone: str
    online_profiles: List[OnlineProfile]
    experience_summary: Optional[str] = None
    projects: List[Project] = []
    skills: List[str] = []
    achievements: Optional[List[str]] = None

class JobDescription(BaseModel):
    title: str
    description: str

class AnalysisResult(BaseModel):
    compatibility_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    irrelevant_content: List[str]
    suggestions: Dict[str, List[str]]  # Key: "remove" or "add", Value: List of suggestions