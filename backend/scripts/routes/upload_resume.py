from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from scripts.utils.openai_utils import generate_questions
from scripts.utils.nlp_utils import extract_keywords
import os
import pdfplumber
from docx import Document

router = APIRouter()
session_state = {"questions": [], "current_index": 0}

def extract_text_from_pdf(file_path):
    print("📄 Extracting text from PDF...")
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        print("✅ PDF text extracted.")
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        raise HTTPException(status_code=400, detail=f"PDF read error: {str(e)}")
    return text

def extract_text_from_docx(file_path):
    print("📄 Extracting text from DOCX...")
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), job_description: str = Form(...)):
    print("🔁 API Call: /upload-resume")
    print(f"📄 Filename: {file.filename}")
    print(f"📝 Job Description (preview): {job_description[:100]}...")

    extension = os.path.splitext(file.filename)[1].lower()
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text based on file type
    if extension == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif extension in [".docx", ".doc"]:
        text = extract_text_from_docx(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF or DOCX.")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in resume.")

    print("🧠 Extracting keywords...", text)
    keywords = extract_keywords(text + job_description)
    print("🔑 Keywords:", keywords)

    print("🤖 Generating interview questions using OpenAI...")
    questions = generate_questions(text, job_description, keywords)

    print("✅ Questions Generated:", questions)
    for i, q in enumerate(questions, 1):
        print(f"Q{i}: {q}")

    session_state["questions"] = questions
    session_state["current_index"] = 0

    return {"total_questions": len(questions)}
