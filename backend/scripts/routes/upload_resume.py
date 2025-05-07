from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from scripts.utils.openai_utils import generate_questions
from scripts.utils.nlp_utils import extract_keywords
import os
import pdfplumber
from docx import Document
import json
from main import EVALUATION_LOG_PATH, FACE_LOG_PATH
import glob

router = APIRouter()

# In-memory session tracking
session_state = {
    "questions": [],
    "current_index": 0  # Start from 0 always
}

def reset_interview_logs():
    """
    Clears previous evaluation data:
    - evaluation.json
    - face_confidence_log.json
    - generated MP3 question files
    """
    try:
        with open(EVALUATION_LOG_PATH, "w") as f:
            json.dump([], f)
        with open(FACE_LOG_PATH, "w") as f:
            json.dump([], f)
        print("Cleared evaluation and face confidence logs.")
    except Exception as e:
        print(f"Error clearing log files: {e}")

    # Remove old question audio files
    mp3_files = glob.glob(os.path.join("static", "question_*.mp3"))
    for file_path in mp3_files:
        try:
            os.remove(file_path)
            print(f"Removed: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pdfplumber.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        print("PDF text extracted successfully.")
    except Exception as e:
        print(f"Error reading PDF: {e}")
        raise HTTPException(status_code=400, detail=f"PDF read error: {str(e)}")
    return text

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    """
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        raise HTTPException(status_code=400, detail="DOCX read error.")

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...), 
    job_description: str = Form(...), 
    num_questions: int = Form(2)
):
    """
    Accepts resume file and job description, extracts keywords,
    and generates a set of interview questions.
    """
    reset_interview_logs()

    extension = os.path.splitext(file.filename)[1].lower()
    file_path = os.path.join("uploads", file.filename)

    # Save uploaded file
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        print(f"File saved at: {file_path}")
    except Exception as e:
        print(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

    # Extract text from uploaded resume
    if extension == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif extension in [".docx", ".doc"]:
        text = extract_text_from_docx(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF or DOCX.")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in resume.")

    # Extract keywords and generate interview questions
    keywords = extract_keywords(text + job_description)
    questions = generate_questions(text, job_description, keywords, num_questions=num_questions)

    for i, q in enumerate(questions, 1):
        print(f"Q{i}: {q}")

    session_state["questions"] = questions
    session_state["current_index"] = 0

    return {
        "message": "Questions generated successfully",
        "total_questions": len(questions),
        "questions": questions
    }
