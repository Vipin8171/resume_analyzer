from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.services.resume_parser import read_resume_text
from app.services.extractor import extract_resume_info
from app.services.groq_analyzer import generate_resume_analysis
from app.models.resume_schema import Resume, JobDescription

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def get_upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.post("/upload", response_class=HTMLResponse)
async def upload_resume(request: Request,
                        resume: UploadFile = File(...),
                        jd_title: Optional[str] = Form(None),
                        jd_text: Optional[str] = Form(None)):
    """Upload and analyze resume against JD."""
    # Parse resume (now returns text + hyperlinks)
    text, hyperlinks = await read_resume_text(resume)
    resume_obj: Resume = extract_resume_info(text)
    
    # If hyperlinks were found, merge them with extracted profiles
    if hyperlinks:
        from app.models.resume_schema import OnlineProfile
        from app.services.extractor import label_url
        for link_text, url in hyperlinks:
            if url and not any(p.url == url for p in resume_obj.online_profiles):
                profile = OnlineProfile(label=label_url(url), url=url)
                resume_obj.online_profiles.append(profile)

    # Prepare JD
    jd_desc = jd_text or ""
    jd_title_val = jd_title or ""
    jd_obj = JobDescription(title=jd_title_val, description=jd_desc)

    # Generate analysis using Groq (if JD provided)
    analysis = None
    groq_error = None
    if jd_desc:
        try:
            analysis_data = generate_resume_analysis(resume_obj, jd_obj)
            analysis = analysis_data
        except Exception as e:
            groq_error = f"Analysis Error: {str(e)}. Please ensure GROQ_API_KEY2 is set in .env file."

    return templates.TemplateResponse("result.html", {
        "request": request,
        "resume": resume_obj,
        "jd": jd_obj,
        "analysis": analysis,
        "groq_error": groq_error
    })
