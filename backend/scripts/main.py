import fitz  # PyMuPDF for PDF parsing
import spacy
from docx import Document
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
import pyttsx3
import os
import pathlib
import openai
import mediapipe as mp
import cv2
import numpy as np
import pandas as pd
# pdfplumber
# Load environment variables
load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAPI_KEY")
openai.api_key = "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"

# Load spaCy NLP model for entity extraction
nlp = spacy.load("en_core_web_sm")

# Initialize other models
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
face_mesh = mp_face_mesh.FaceMesh()
tts_engine = pyttsx3.init()
thisdir = pathlib.Path(__file__).parent.absolute()
client = openai.Client(api_key="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")

landmark_data = []
cap = cv2.VideoCapture(0)
confidence_data = []
FRAME_WIDTH = 640  
FRAME_HEIGHT = 600

# app = FastAPI()

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using PyMuPDF."""
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_entities(text):
    """Extract structured information (skills, education, experience) using spaCy NLP."""
    doc = nlp(text)
    entities = {"skills": [], "education": [], "experience": []}
    for ent in doc.ents:
        if ent.label_ in ["ORG", "GPE"]:
            entities["education"].append(ent.text)
        elif ent.label_ in ["DATE"]:
            entities["experience"].append(ent.text)
        elif ent.label_ in ["NORP", "PRODUCT", "LANGUAGE"]:
            entities["skills"].append(ent.text)
    return entities

# def detect_face_confidence():
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         print("Error: Camera not accessible!")
#         return

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Error: Failed to read frame!")
#             break

      
#         frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

#         # convert frame to RGB
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # process face detection
#         face_results = face_mesh.process(rgb_frame)

#         # default confidence (0% if no face detected)
#         face_confidence = 100.0  

#         if face_results.multi_face_landmarks:
#             face_landmarks = face_results.multi_face_landmarks[0].landmark

#             # Get key face points
#             nose_tip = face_landmarks[1]  # Nose tip (reference for centering)
#             left_eye = face_landmarks[33]  # Left eye center
#             right_eye = face_landmarks[263]  # Right eye center

#             # Convert to pixel values
#             nose_x = int(nose_tip.x * FRAME_WIDTH)
#             nose_y = int(nose_tip.y * FRAME_HEIGHT)
#             left_eye_x = int(left_eye.x * FRAME_WIDTH)
#             right_eye_x = int(right_eye.x * FRAME_WIDTH)

#             # checking horizontal centering
#             center_x = FRAME_WIDTH // 2
#             deviation_x = abs(nose_x - center_x)
#             max_deviation = FRAME_WIDTH // 3  # Allowable head movement before penalty

#             if deviation_x > max_deviation:
#                 penalty_x = min((deviation_x / FRAME_WIDTH) * 100, 40)  # Gradual drop
#                 face_confidence -= penalty_x

#             # checking head tilt (Rotation)
#             eye_distance = abs(left_eye_x - right_eye_x)
#             expected_eye_distance = FRAME_WIDTH // 5  # Approximate normal eye distance

#             tilt_penalty = min(abs(expected_eye_distance - eye_distance) / expected_eye_distance * 40, 30)
#             face_confidence -= tilt_penalty  # Reduce confidence gradually based on tilt

#             # check distance from Camera (Z-Axis)
#             nose_depth = nose_tip.z  # Z is negative when closer
#             if nose_depth < -0.3:  # Too close
#                 face_confidence -= 15
#             elif nose_depth > 0.2:  # Too far
#                 face_confidence -= 25

#             # Ensure confidence stays in [0, 100] range
#             face_confidence = max(min(face_confidence, 100), 0)

#             # Draw landmarks on the frame
#             for face_landmarks in face_results.multi_face_landmarks:
#                 mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION)

#             # Draw nose center
#             cv2.circle(frame, (nose_x, nose_y), 5, (0, 255, 0), -1)

#         else:
#             face_confidence = 0  # No face detected

#         # Display confidence score
#         confidence_text = f"Face Confidence: {face_confidence:.2f}%"
#         cv2.putText(frame, confidence_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

#         # Show the live video
#         cv2.imshow("Face Confidence Detection", frame)

#         # Store confidence data
#         confidence_data.append(face_confidence)

#         # Press 'q' to exit
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     print("Camera feed stopped.")

#     # Save confidence scores to CSV
#     df = pd.DataFrame({"Face Confidence (%)": confidence_data})
#     df.to_csv("face_confidence.csv", index=False)
#     print("Face confidence data saved to face_confidence.csv!")

# def generate_interview_questions(resume_text, job_description):
#     """Use OpenAI's GPT to generate interview questions based on the resume and job description."""
#     prompt = f"""
#     You are an AI job interview coach. Generate 5 technical and behavioral interview questions 
#     based on the following resume and job description: 

#     Resume: {resume_text}
#     Job Description: {job_description}

#     Format your response as:
#     1. [Question]
#     2. [Question]
#     3. [Question]
#     4. [Question]
#     5. [Question]
#     """
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[{"role": "system", "content": "Generate technical and behavioral interview questions."},
#                   {"role": "user", "content": prompt}]
#     )
#     return response["choices"][0]["message"]["content"].split("\n")

# @app.post("/parse_resume/")
# async def parse_resume(file: UploadFile = File(...), job_description: str = ""):
#     """API endpoint to parse resume and generate interview questions."""
#     file_path = f"temp_{file.filename}"
#     with open(file_path, "wb") as buffer:
#         buffer.write(await file.read())
    
#     if file.filename.endswith(".pdf"):
#         resume_text = extract_text_from_pdf(file_path)
#     elif file.filename.endswith(".docx"):
#         resume_text = extract_text_from_docx(file_path)
#     else:
#         return {"error": "Unsupported file format"}
    
#     entities = extract_entities(resume_text)
#     questions = generate_interview_questions(resume_text, job_description)
    
#     os.remove(file_path)  # Clean up temporary file
    
#     return {"resume_text": resume_text, "entities": entities, "interview_questions": questions}

def main():
    pdf = extract_text_from_pdf("/Users/admin/Desktop/capstone/backend/My current resume.pdf")
    ent = extract_entities(pdf)
    # print(thisdir)
    print(ent)


if __name__ == "__main__": 
    main()