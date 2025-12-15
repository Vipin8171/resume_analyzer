from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes import upload, analysis

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Resume Analyzer - Phase 1")

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["upload"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI-powered Resume Analyzer!"}