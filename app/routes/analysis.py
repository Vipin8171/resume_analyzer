from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models.resume_schema import Resume, JobDescription, AnalysisResult
from app.services.skill_matcher import analyze_resume_vs_jd

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/analysis", response_class=HTMLResponse)
async def analyze(request: Request,
                  resume_json: str = Form(...),
                  jd_title: str = Form(""),
                  jd_text: str = Form("")):
    import json
    resume_dict = json.loads(resume_json)
    resume = Resume(**resume_dict)
    jd = JobDescription(title=jd_title, description=jd_text)

    analysis: AnalysisResult = analyze_resume_vs_jd(resume, jd)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "resume": resume,
        "jd": jd,
        "analysis": analysis
    })