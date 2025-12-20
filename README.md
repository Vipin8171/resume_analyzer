# Resume Analyzer

FastAPI-based resume analysis tool that parses PDF/DOCX/TXT resumes, extracts structured fields (name, contact, education, projects, skills, achievements, online profiles), and runs Groq LLM analysis for fit against a job description.
<img width="1919" height="1079" alt="Screenshot 2025-12-13 232254" src="https://github.com/user-attachments/assets/cf94a1d8-24c0-467e-9032-5bdbce67a4fc" />

## Features
- PDF (pdfplumber) and DOCX (python-docx) parsing with hyperlink extraction
- Robust section detection (education, projects, skills, achievements, profiles)
- Clean, NLP-ready output with debug files in `results/`
- Groq analysis (llama-3.1-8b-instant) with compatibility scoring and recommendations

## Setup
1) Create & activate a virtual env (PowerShell):
```powershell
python -m venv env
./env/Scripts/Activate.ps1
```
2) Install dependencies:
```powershell
pip install -r requirements.txt
```
3) Configure environment:
- Copy `.env.example` to `.env`
- Set `GROQ_API_KEY2=<your_key>`

## Run
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000, upload a resume + optional JD, then check `results/extracted_*.txt` for full extraction/debug info.

## Notes
- `results/` holds debug extraction outputs (ignored by git)
- `.env` is ignored; use `.env.example` for defaults
- Requires Python 3.10+ (tested on Windows)
