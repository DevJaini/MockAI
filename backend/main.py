from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Create necessary folders
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)

app = FastAPI()

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (MP3s)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import and include all routers
from scripts.routes.upload_resume import router as resume_router
from scripts.routes.play_question import router as play_router
from scripts.routes.submit_answer import router as answer_router
from scripts.routes.face_confidence import router as face_router
from scripts.routes.interview_report import router as report_router

app.include_router(resume_router)
app.include_router(play_router)
app.include_router(answer_router)
app.include_router(face_router)
app.include_router(report_router)
