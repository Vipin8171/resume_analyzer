"""Groq API integration for AI-powered resume analysis."""
import os
from groq import Groq
from app.models.resume_schema import Resume, JobDescription

def get_groq_client() -> Groq:
    """Initialize Groq client with API key from environment."""
    api_key = os.getenv("GROQ_API_KEY2")
    if not api_key:
        raise ValueError("GROQ_API_KEY2 environment variable not set. Please add it to your .env file.")
    return Groq(api_key=api_key)


def generate_resume_analysis(resume: Resume, jd: JobDescription) -> dict:
    """
    Generate detailed compatibility analysis using Groq API.
    
    Args:
        resume: Extracted resume data
        jd: Job description
    
    Returns:
        dict with analysis results
    """
    client = get_groq_client()
    
    # Prepare resume summary
    resume_summary = f"""
    Name: {resume.name}
    Email: {resume.email}
    Phone: {resume.phone}
    Skills: {', '.join(resume.skills)}
    Experience: {resume.experience_summary or 'Not specified'}
    Projects: {', '.join([p.name for p in resume.projects]) if resume.projects else 'None mentioned'}
    Online Profiles: {', '.join([f"{p.label}: {p.url}" for p in resume.online_profiles])}
    """
    
    # Create prompt for Groq
    prompt = f"""Analyze this resume against the job description and provide:

RESUME:
{resume_summary}

JOB DESCRIPTION:
Title: {jd.title}
Description: {jd.description}

Please provide your analysis in this EXACT format (use these exact section headers):

COMPATIBILITY_SCORE: (a number 0-10)

MATCHED_SKILLS:
(list each skill on a new line with a dash)

MISSING_SKILLS:
(list each skill on a new line with a dash)

STRENGTHS:
(bullet points of what the candidate has going for them)

GAPS:
(bullet points of what's missing)

RECOMMENDATIONS:
(specific, actionable advice for the candidate)

OVERALL_ASSESSMENT:
(2-3 sentences summarizing fit for this role)

Be concise but detailed. Focus on technical fit."""

    # Call Groq API
    message = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000,
    )
    
    response_text = message.choices[0].message.content
    
    # Parse response
    return parse_groq_response(response_text)


def parse_groq_response(response: str) -> dict:
    """Parse Groq response into structured format."""
    result = {
        "compatibility_score": 5.0,
        "matched_skills": [],
        "missing_skills": [],
        "strengths": [],
        "gaps": [],
        "recommendations": [],
        "overall_assessment": "Analysis complete.",
        "raw_response": response,
    }
    
    # Parse sections
    sections = response.split("\n\n")
    current_section = None
    
    for section in sections:
        section_lower = section.lower()
        
        if "compatibility_score" in section_lower:
            try:
                # Extract score number
                for word in section.split():
                    try:
                        score = float(word)
                        if 0 <= score <= 10:
                            result["compatibility_score"] = score
                            break
                    except ValueError:
                        continue
            except:
                pass
        
        elif "matched_skills" in section_lower:
            skills = extract_list_items(section)
            result["matched_skills"] = skills
        
        elif "missing_skills" in section_lower:
            skills = extract_list_items(section)
            result["missing_skills"] = skills
        
        elif "strengths" in section_lower:
            items = extract_list_items(section)
            result["strengths"] = items
        
        elif "gaps" in section_lower:
            items = extract_list_items(section)
            result["gaps"] = items
        
        elif "recommendations" in section_lower:
            items = extract_list_items(section)
            result["recommendations"] = items
        
        elif "overall_assessment" in section_lower:
            text = extract_text_after_header(section)
            if text:
                result["overall_assessment"] = text
    
    return result


def extract_list_items(text: str) -> list:
    """Extract list items from section text."""
    items = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        # Skip headers and empty lines
        if not line or ':' in line or '=' in line:
            continue
        # Remove list markers
        if line.startswith('-'):
            line = line[1:].strip()
        elif line.startswith('•'):
            line = line[1:].strip()
        elif line and line[0].isdigit() and '.' in line[:3]:
            line = line.split('.', 1)[1].strip()
        
        if line:
            items.append(line)
    
    return items


def extract_text_after_header(text: str) -> str:
    """Extract text content after header."""
    lines = text.split('\n')
    content = []
    skip_header = True
    
    for line in lines:
        if skip_header:
            if ':' in line or '=' in line:
                skip_header = False
            continue
        if line.strip():
            content.append(line.strip())
    
    return ' '.join(content)
