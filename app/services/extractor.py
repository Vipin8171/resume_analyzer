"""Enhanced extraction of fields from resume text using regex and heuristics."""
import re
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from app.models.resume_schema import Resume, OnlineProfile, Project
from app.utils.text_cleaner import normalize_text

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(?:\+\d{1,3}[\s.-]?)?(?:\d{2,4}[\s.-]?)?\d{3}[\s.-]?\d{3,4}[\s.-]?\d{3,4}|\+\d{1,3}\s?\d{6,14}")
URL_RE = re.compile(r"https?://[^\s]+")

# Expanded profile labels for better matching
PROFILE_LABELS = {
    "linkedin": "LinkedIn",
    "github": "GitHub",
    "portfolio": "Portfolio",
    "medium": "Medium",
    "kaggle": "Kaggle",
    "leetcode": "LeetCode",
    "codeforces": "Codeforces",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
}

# Expanded tech skills vocabulary
TECH_WORDS = [
    # Programming Languages
    "python", "java", "c++", "c#", "javascript", "typescript", "go", "rust", "r", "scala", "kotlin",
    # Web Frameworks
    "fastapi", "flask", "django", "spring", "nodejs", "express", "next.js", "nextjs", "vue.js", "nuxt",
    # Data Science & ML
    "pandas", "numpy", "scipy", "scikit-learn", "sklearn", "matplotlib", "seaborn", "plotly",
    "statsmodels", "xgboost", "lightgbm", "catboost", "eda", "statistical analysis",
    # Databases
    "sql", "mysql", "postgres", "postgresql", "mongodb", "redis", "cassandra", "dynamodb", "elasticsearch",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab", "github", "circleci",
    # Big Data
    "spark", "hadoop", "kafka", "airflow", "dbt", "hive", "presto",
    # Deep Learning & AI
    "pytorch", "tensorflow", "keras", "torch", "onnx", "transformers", "hugging face",
    "bert", "gpt", "llm", "langchain", "faiss", "rag", "llama", "openai",
    # NLP
    "spacy", "nltk", "gensim", "textblob", "tokenization", "nlp", "ner", "sentiment",
    # Computer Vision
    "opencv", "opencv-python", "yolo", "yolov8", "yolov5", "yolov3", "cnn", "deepsort",
    # Frontend
    "react", "vue", "angular", "svelte", "html", "css", "sass", "bootstrap", "tailwind", "d3.js",
    # Tools & Others
    "git", "jupyter", "notebook", "jupyter notebook", "jira", "confluence", "notion",
    "linux", "bash", "shell", "powershell", "windows", "mac", "macos",
    # Power BI & Analytics
    "power bi", "powerbi", "tableau", "looker", "qlik", "excel", "vba",
    # Additional ML/DL
    "regression", "classification", "random forest", "lstm", "rnn", "cnn", "gan", "mlops",
    "time series", "forecasting", "clustering", "pca", "kmeans", "ensemble", "cross validation",
    "fine-tuning", "prompt engineering", "vector databases", "embeddings", "retrieval augmented",
]

# Section header detection keywords
SECTION_KEYWORDS = {
    "contact": ["contact", "phone", "email", "linkedin", "github", "address", "location"],
    "summary": ["summary", "objective", "profile", "about", "professional summary", "executive summary"],
    "education": ["education", "degree", "university", "college", "b.tech", "btech", "bachelor", "master", "m.tech", "mtech", "certification", "course", "gpa", "cgpa"],
    "experience": ["experience", "work", "employment", "professional", "job", "position", "worked as", "worked on"],
    "projects": ["projects", "project", "portfolio", "capstone", "case study", "assignment"],
    "skills": ["skills", "technical", "technologies", "competencies", "expertise", "proficient", "programming", "tools"],
    "achievements": ["achievements", "awards", "recognitions", "publications", "certifications", "honors", "accomplishments"],
}

PROJECT_HINTS = ["project", "assignment", "case study", "capstone", "experience"]
EXPERIENCE_HINTS = ["experience", "worked", "developed", "led", "managed", "implemented", "built", "designed", "created", "achieved"]


def label_url(url: str) -> str:
    """Classify URL to appropriate profile type."""
    u = url.lower()
    for key, lbl in PROFILE_LABELS.items():
        if key in u:
            return lbl
    return "Website"


def extract_name_robust(text: str) -> str:
    """
    Extract full name from resume text.
    Handles multi-line names and formatting issues.
    Returns clean, single-line format.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return ""
    
    # Skip header/contact lines and look for name in first 5 meaningful lines
    name_candidates = []
    for i, line in enumerate(lines[:15]):
        # Skip if it's obviously contact info, email, or URL
        if '@' in line or 'http' in line or '+' in line and len(line) < 5:
            continue
        # Skip if it's too long (likely not a name)
        if len(line) > 100:
            continue
        # Skip if it's all uppercase with numbers (likely a header)
        if line.isupper() and any(c.isdigit() for c in line):
            continue
        # Skip common non-name lines
        if any(skip in line.lower() for skip in ["summary", "objective", "about", "phone", "email", "linkedin", "github"]):
            continue
        
        # Check if line looks like a name (short, capitalized)
        words = line.split()
        if 1 <= len(words) <= 5:  # Names typically have 1-5 words
            # Check if mostly alphabetic
            alpha_count = sum(1 for c in line if c.isalpha() or c.isspace() or c in ['-', "'"])
            if alpha_count / len(line) > 0.7:  # At least 70% alphabetic
                name_candidates.append(line)
    
    # Find best candidate (should be early in resume)
    if name_candidates:
        # Try to combine multi-line names
        if len(name_candidates) >= 2:
            first_candidate = name_candidates[0]
            second_candidate = name_candidates[1]
            # Check if they can be combined (e.g., "V T" + "IPIN OMER" -> "V T Ipin Omer")
            if len(first_candidate.split()) <= 3 and len(second_candidate.split()) <= 3:
                combined = (first_candidate + " " + second_candidate).strip()
                if len(combined.split()) <= 5:  # Still reasonable name length
                    return combined.title()  # Proper title case
        
        return name_candidates[0].title()
    
    return ""


def extract_email(text: str) -> str:
    """Extract email address from resume."""
    match = EMAIL_RE.search(text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Extract phone number from resume."""
    match = PHONE_RE.search(text)
    return match.group(0) if match else ""


def detect_section_start(line: str, section: str) -> bool:
    """Detect if line is a section header."""
    line_lower = line.lower().strip()
    if ':' not in line and not line_lower.endswith('s'):
        return False
    keywords = SECTION_KEYWORDS.get(section, [])
    return any(kw in line_lower for kw in keywords)


def split_resume_by_sections(text: str) -> Dict[str, str]:
    """
    Split resume text into semantic sections.
    Returns dict with section names as keys and content as values.
    """
    sections = {k: "" for k in SECTION_KEYWORDS.keys()}
    sections["other"] = ""
    
    lines = text.split('\n')
    current_section = "contact"  # Usually contact info is at top
    current_content = []
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check if this line starts a new section
        detected_section = None
        for section_name in SECTION_KEYWORDS.keys():
            if detect_section_start(line, section_name):
                detected_section = section_name
                break
        
        if detected_section:
            # Save previous section
            sections[current_section] = '\n'.join(current_content).strip()
            current_section = detected_section
            current_content = [line]  # Start with the header line
        else:
            current_content.append(line)
    
    # Save last section
    sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def extract_projects_from_text(text: str) -> List[Project]:
    """
    Extract projects with technologies from text.
    Looks for project entries typically formatted as:
    Project Name (Tech Stack) - Description
    or
    Project Name
    Technologies: Python, SQL, etc
    """
    projects: List[Project] = []
    
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for project indicators
        if any(hint in line.lower() for hint in ["project:", "• "]) or (
            line and not line[0].isdigit() and len(line) > 5 and 
            any(tech.lower() in line.lower() for tech in TECH_WORDS[:10])  # Common techs
        ):
            # Extract tech from this line
            techs = [t for t in TECH_WORDS if t.lower() in line.lower()]
            
            # Get project name (remove tech keywords)
            project_name = line
            for tech in techs:
                project_name = project_name.lower().replace(tech.lower(), "").strip()
            project_name = project_name.replace("•", "").replace("project:", "").strip()
            project_name = project_name.split("(")[0].strip()  # Remove parenthetical tech
            
            if project_name and len(project_name) > 3:
                projects.append(Project(
                    name=project_name[:150],
                    technologies=sorted(set(techs))[:10]  # Top 10 techs per project
                ))
        
        i += 1
    
    return projects[:10]  # Max 10 projects


def extract_skills_from_text(text: str) -> List[str]:
    """Extract all detected technical skills from resume."""
    text_lower = text.lower()
    detected_skills = set()
    
    # Find exact matches for tech words
    for tech in TECH_WORDS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(tech) + r'\b'
        if re.search(pattern, text_lower):
            detected_skills.add(tech)
    
    return sorted(list(detected_skills))


def extract_achievements_from_text(text: str) -> List[str]:
    """Extract achievements and accomplishments from text."""
    achievements = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        # Look for bullet points or numbered items
        if line.startswith('•') or line.startswith('-') or line[0].isdigit() and '.' in line[:3]:
            achievement = line.lstrip('•-0123456789. ').strip()
            if achievement and len(achievement) > 10:
                achievements.append(achievement[:200])
    
    return achievements[:10]  # Max 10 achievements


def extract_profiles_from_text(text: str) -> List[OnlineProfile]:
    """Extract online profiles/links from text."""
    profiles = []
    urls = URL_RE.findall(text)
    
    # Also look for plain profile names mentioned in text
    profile_mentions = re.findall(
        r'\b(LinkedIn|GitHub|Kaggle|LeetCode|Codeforces|Portfolio|Medium|GitLab)\b',
        text,
        re.IGNORECASE
    )
    
    # Match URLs to mentioned profiles
    for url in urls:
        label = label_url(url)
        profiles.append(OnlineProfile(label=label, url=url))
    
    return profiles




def classify_resume_sections(text: str) -> dict:
    """
    Classify and extract content from each resume section.
    Returns comprehensive section breakdown with proper categorization.
    """
    sections = split_resume_by_sections(text)
    
    return {
        "full_text": text,
        "contact": sections.get("contact", "").strip(),
        "summary": sections.get("summary", "").strip(),
        "education": sections.get("education", "").strip(),
        "experience": sections.get("experience", "").strip(),
        "projects": sections.get("projects", "").strip(),
        "skills": sections.get("skills", "").strip(),
        "achievements": sections.get("achievements", "").strip(),
    }


def save_extracted_data(text: str, extracted: Resume) -> None:
    """
    Save FULL extracted data with proper classification to debug text file.
    Now properly extracts and classifies education, projects, skills, and achievements.
    """
    result_dir = "results"
    os.makedirs(result_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{result_dir}/extracted_{timestamp}.txt"
    
    # Classify sections
    sections = classify_resume_sections(text)
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Header
        f.write("=" * 100 + "\n")
        f.write(f"RESUME EXTRACTION & CLASSIFICATION REPORT - {datetime.now().isoformat()}\n")
        f.write("=" * 100 + "\n\n")
        
        # Full Raw Text
        f.write("📄 FULL RAW TEXT (Complete Extracted Content):\n")
        f.write("-" * 100 + "\n")
        f.write(text)
        f.write("\n\n")
        
        # Classified Sections (RAW SECTION CONTENT)
        f.write("=" * 100 + "\n")
        f.write("🔍 CLASSIFIED SECTIONS (Raw Section Content):\n")
        f.write("=" * 100 + "\n\n")
        
        if sections["contact"].strip():
            f.write("📞 CONTACT INFORMATION:\n")
            f.write("-" * 100 + "\n")
            f.write(sections["contact"].strip() + "\n\n")
        
        if sections["summary"].strip():
            f.write("📋 SUMMARY / OBJECTIVE:\n")
            f.write("-" * 100 + "\n")
            f.write(sections["summary"].strip() + "\n\n")
        
        if sections["education"].strip():
            f.write("🎓 EDUCATION:\n")
            f.write("-" * 100 + "\n")
            f.write(sections["education"].strip() + "\n\n")
        
        if sections["experience"].strip():
            f.write("💼 EXPERIENCE / WORK:\n")
            f.write("-" * 100 + "\n")
            f.write(sections["experience"].strip() + "\n\n")
        
        if sections["projects"].strip():
            f.write("🚀 PROJECTS / PORTFOLIO:\n")
            f.write("-" * 100 + "\n")
            f.write(sections["projects"].strip() + "\n\n")
        
        if sections["skills"].strip():
            f.write("🛠️ SKILLS / TECHNOLOGIES:\n")
            f.write("-" * 100 + "\n")
            f.write(sections["skills"].strip() + "\n\n")
        
        if sections["achievements"].strip():
            f.write("🏆 ACHIEVEMENTS / CERTIFICATIONS:\n")
            f.write("-" * 100 + "\n")
            f.write(sections["achievements"].strip() + "\n\n")
        
        # Structured Extraction (PARSED MODEL OUTPUT)
        f.write("=" * 100 + "\n")
        f.write("✅ STRUCTURED EXTRACTION (Parsed Model Output):\n")
        f.write("=" * 100 + "\n\n")
        
        f.write(f"👤 NAME: {extracted.name or 'NOT EXTRACTED'}\n")
        f.write(f"📧 EMAIL: {extracted.email or 'NOT EXTRACTED'}\n")
        f.write(f"📱 PHONE: {extracted.phone or 'NOT EXTRACTED'}\n\n")
        
        f.write(f"📝 EXPERIENCE SUMMARY:\n{extracted.experience_summary or 'NOT EXTRACTED'}\n\n")
        
        f.write(f"🛠️ SKILLS ({len(extracted.skills)} detected):\n")
        if extracted.skills:
            for skill in sorted(extracted.skills):
                f.write(f"  ✓ {skill}\n")
        else:
            f.write("  (No skills extracted)\n")
        f.write("\n")
        
        f.write(f"🌐 ONLINE PROFILES ({len(extracted.online_profiles)} found):\n")
        if extracted.online_profiles:
            for p in extracted.online_profiles:
                f.write(f"  • {p.label}: {p.url}\n")
        else:
            f.write("  (No profiles found)\n")
        f.write("\n")
        
        f.write(f"🚀 PROJECTS ({len(extracted.projects)} detected):\n")
        if extracted.projects:
            for i, proj in enumerate(extracted.projects, 1):
                f.write(f"  {i}. {proj.name}\n")
                if proj.technologies:
                    f.write(f"     Technologies: {', '.join(proj.technologies)}\n")
        else:
            f.write("  (No projects extracted)\n")
        f.write("\n")
        
        f.write(f"🏆 ACHIEVEMENTS ({len(extracted.achievements or []) if extracted.achievements else 0} detected):\n")
        if extracted.achievements:
            for achievement in extracted.achievements:
                f.write(f"  • {achievement}\n")
        else:
            f.write("  (No achievements extracted)\n")
        f.write("\n")
        
        f.write("=" * 100 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 100 + "\n")



def extract_resume_info(text: str) -> Resume:
    """
    Enhanced extraction using robust heuristics and proper section detection.
    Now correctly extracts: name, contact info, skills, projects, achievements, and profiles.
    """
    # Extract basic contact information
    name = extract_name_robust(text)
    email = extract_email(text)
    phone = extract_phone(text)
    
    # Extract sections
    sections = split_resume_by_sections(text)
    
    # Extract summary from summary section
    experience_summary = sections.get("summary", "").strip()
    if not experience_summary:
        # Fallback: try to get first paragraph
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 20]
        if len(lines) > 2:
            experience_summary = lines[1][:300]
    
    # Extract structured data from their respective sections
    profiles = extract_profiles_from_text(text)
    skills = extract_skills_from_text(text)
    projects = extract_projects_from_text(sections.get("projects", text))
    achievements = extract_achievements_from_text(sections.get("achievements", text))
    
    resume_obj = Resume(
        name=name or "NOT EXTRACTED",
        email=email or "",
        phone=phone or "",
        online_profiles=profiles,
        experience_summary=experience_summary if experience_summary else None,
        projects=projects,
        skills=skills,
        achievements=achievements if achievements else None,
    )
    
    # Save debug file
    save_extracted_data(text, resume_obj)
    
    return resume_obj
