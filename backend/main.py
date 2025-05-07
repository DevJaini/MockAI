from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Ensure necessary directories exist for file uploads and static content
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Define base directory and log file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Root path of backend directory
EVALUATION_LOG_PATH = os.path.join(BASE_DIR, "evaluation.json")  # Path for storing evaluation results
FACE_LOG_PATH = os.path.join(BASE_DIR, "face_confidence_log.json")  # Path for logging face confidence data

# Initialize FastAPI app instance
app = FastAPI()

# Set up CORS to allow cross-origin requests (required for frontend-backend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (e.g., audio files) from the /static route
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modular route imports to keep main.py clean and maintainable
from scripts.routes.upload_resume import router as resume_router
from scripts.routes.play_question import router as play_router
from scripts.routes.submit_answer import router as answer_router
from scripts.routes.face_confidence import router as face_router
from scripts.routes.interview_report import router as report_router

# Register all route modules with the FastAPI app
app.include_router(resume_router)
app.include_router(play_router)
app.include_router(answer_router)
app.include_router(face_router)
app.include_router(report_router)