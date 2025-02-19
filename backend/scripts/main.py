import pdfplumber
from docx import Document
import pyttsx3
import os
import pathlib
from dotenv import load_dotenv
import openai
import mediapipe as mp
import numpy as np
import pandas as pd
import cv2
import signal
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import base64
from PIL import Image
import uvicorn
import io

app = FastAPI()

# initialize models and env files
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
face_mesh = mp_face_mesh.FaceMesh()
tts_engine = pyttsx3.init()
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# defining current directory
thisdir = pathlib.Path(__file__).parent.absolute()
client = openai.Client(api_key=os.getenv("OPENAPI_KEY"))

landmark_data = []

cap = cv2.VideoCapture(0)

confidence_data = []


FRAME_WIDTH = 640  
FRAME_HEIGHT = 600

async def decode_image(img_string):
    """ Decodes base64 image received from React """
    try:
        img_data = base64.b64decode(img_string.split(',')[1])
        image = Image.open(io.BytesIO(img_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None  # Return None if decoding fails

@app.websocket("/ws")
async def detect_face_confidence(websocket: WebSocket):
    """ WebSocket connection for face confidence detection """
    await websocket.accept()
    print("Connected to WebSocket")

    try:
        while True:
            data = await websocket.receive_json()

            if "image" not in data:
                print("Invalid data format received. Skipping...")
                continue

            frame = await decode_image(data["image"])

            if frame is None:
                print("Warning: Empty frame received, skipping processing.")
                continue  # Skip this frame

            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = face_mesh.process(rgb_frame)

            # Default confidence (0% if no face detected)
            face_confidence = 100.0  

            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0].landmark

                # Get key face points
                nose_tip = face_landmarks[1]
                left_eye = face_landmarks[33]
                right_eye = face_landmarks[263]

                # Convert to pixel values
                nose_x = int(nose_tip.x * FRAME_WIDTH)
                left_eye_x = int(left_eye.x * FRAME_WIDTH)
                right_eye_x = int(right_eye.x * FRAME_WIDTH)

                # Checking horizontal centering
                center_x = FRAME_WIDTH // 2
                deviation_x = abs(nose_x - center_x)
                max_deviation = FRAME_WIDTH // 3  

                if deviation_x > max_deviation:
                    penalty_x = min((deviation_x / FRAME_WIDTH) * 100, 40)  
                    face_confidence -= penalty_x

                # Checking head tilt (Rotation)
                eye_distance = abs(left_eye_x - right_eye_x)
                expected_eye_distance = FRAME_WIDTH // 5  

                tilt_penalty = min(abs(expected_eye_distance - eye_distance) / expected_eye_distance * 40, 30)
                face_confidence -= tilt_penalty  

                # Ensure confidence stays in [0, 100] range
                face_confidence = max(min(face_confidence, 100), 0)

            else:
                face_confidence = 0  # No face detected

            # Send confidence score back to React
            await websocket.send_json({"face_confidence": face_confidence})

    except WebSocketDisconnect:
        print("WebSocket connection closed.")
    except Exception as e:
        print(f"Unexpected WebSocket Error: {e}")




def generate_interview_questions(resume_text, job_description):
    prompt = f"""
    You are an AI job interview coach. Generate 5 technical and behavioral interview questions 
    based on the following resume and job description: 

    Resume: {resume_text}

    Job Description: {job_description}

    Format your response as:
    1. [Question]
    2. [Question]
    3. [Question]
    4. [Question]
    5. [Question]
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are an expert interview coach. You need to create 5 interview technical and behavioral questions based on the resume and job description."},
                  {"role": "user", "content": prompt}]
    )
    print(response.choices[0].message.content.split("\n"))
    return response.choices[0].message.content.split("\n")

# parses the pad file to get the text and generates questions
def read_pdf_tables(file_path):

    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # Ensure there is text before speaking
                text += page_text + "\n"
                ques = generate_interview_questions(
                    page_text, "Software Engineer")
                tts_engine.say(page_text)  # Queue the text to be spoken

    # tts_engine.runAndWait()  # Process the queued text-to-speech commands
    return ques


# def read_docx(file_path):
#     doc = Document(file_path)
#     text = "\n".join([para.text for para in doc.paragraphs])
#     return text

# print(read_docx("sample.docx"))
# calling the main function
def main():
    # read_pdf_tables("/Users/kp/capstone/backend/My current resume.pdf")
    detect_face_confidence()
    # df = pd.read_csv("pose_face_data.csv")
    # print(df.head())
    


if __name__ == "__main__":
   
    uvicorn.run(app, host="0.0.0.0", port=8000)
