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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import base64
from PIL import Image
import uvicorn
import io
import soundfile as sf
from faster_whisper import WhisperModel
from pydub import AudioSegment
import librosa
import wave
from scipy.io.wavfile import write
from gtts import gTTS
import time
import re

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
app = FastAPI()
UPLOAD_DIR = "uploads"
STATIC_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static files directory to serve MP3 files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


session_state = {"questions": [], "current_question_index": 0}

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


whisper_model = WhisperModel("tiny", compute_type="int8", num_workers=1)


# defining current directory
thisdir = pathlib.Path(__file__).parent.absolute()
client = openai.Client(api_key=os.getenv("OPENAPI_KEY"))

landmark_data = []

cap = cv2.VideoCapture(0)

confidence_data = []


FRAME_WIDTH = 640  
FRAME_HEIGHT = 600

#function to decode image
async def decode_image(img_string):
    """ Decodes base64 image received from React """
    try:
        img_data = base64.b64decode(img_string.split(',')[1])
        image = Image.open(io.BytesIO(img_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None  # Return None if decoding fails

# function to detect face confidence based on eye movement and face centering
@app.websocket("/face-confidence")
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

# function to convert audio from frontend to desired sample rate and format
async def convert_audio(file: UploadFile):
    # convert webm to wav and return numpy array
    try:
        audio_data = await file.read()
        audio_io = io.BytesIO(audio_data)

        # convert WebM to WAV
        audio_segment = AudioSegment.from_file(audio_io, format="webm")
        original_sample_rate = audio_segment.frame_rate
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)

        print(f"Original Sample Rate: {original_sample_rate} Hz converted to 16,000 Hz")

        # save for debugging
        wav_filename = "uploaded_audio.wav"
        audio_segment.export(wav_filename, format="wav")

        # convert to NumPy array
        audio_np = np.array(audio_segment.get_array_of_samples(), dtype=np.float32) / 32768.0

        # ensure at least 1 second (16000 samples)
        if len(audio_np) < 16000:
            print(f"⚠️ Audio too short ({len(audio_np)} samples), padding to 16000 samples...")
            audio_np = np.pad(audio_np, (0, 16000 - len(audio_np)), mode='constant')

        return wav_filename
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None

# function to upload audio and transcribe it
@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    # receive audio file, convert and transcribe
    converted_wav = await convert_audio(file)

    if not converted_wav:
        return {"error": "Audio conversion failed"}

    # transcribe using Whisper
    segments, _ = whisper_model.transcribe(converted_wav, language="en")
    transcription = " ".join([segment.text for segment in segments])

    print(f"Transcription: {transcription}")

    return {"transcription": transcription}

# function to sanitize string by removing unwanted characters
def sanitize_string(text):
    """
    Cleans the input text by removing unwanted characters like asterisks, extra spaces, and empty entries.

    Parameters:
    - text (str): The input string.

    Returns:
    - str: A cleaned version of the input string.
    """
    if not isinstance(text, str) or not text.strip():
        return None  # Ignore empty or non-string values

    # Remove asterisks, special characters, and extra spaces
    text = re.sub(r"[\*\"'_]", "", text)  # Removes *, ", ', _
    
    # Remove numeric prefixes (e.g., "1. ", "2. ")
    text = re.sub(r"^\d+\.\s*", "", text)

    # Normalize multiple spaces into a single space and strip leading/trailing spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

# function to generate interview questions based on resume and job description
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

# function to convert text to speech
def text_to_speech(text, output_file):
    """Converts text to speech and saves it as an MP3 file."""
    file_path = os.path.join(STATIC_DIR, output_file)

    if os.path.exists(file_path):
        print(f"🔊 Reusing existing speech file: {file_path}")
        return file_path

    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(file_path)
        print(f"🔊 Saved speech: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

# function to read questions and converting them to speech
def read_questions_and_speak(questions):
    """
    Iterate through the list of questions, converting each to speech one by one.
    """
    for i, question in enumerate(questions):
        question = sanitize_string(question)
        if question:  # Ignore empty strings
            print(f"Speaking Question {i + 1}: {question}")
            text_to_speech(question, f"question_{i + 1}.mp3")
            time.sleep(2) 
    
# parses the pdf file to get the text and generate questions
def read_pdf_tables(file_path):
    """Extracts text from PDF and generates interview questions."""
    global session_state

    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            print("⚠️ No text found in the PDF!")
            return []

        print("PDF Text Extracted. Generating Questions.")

        # Generate questions
        raw_questions = generate_interview_questions(text, "Software Engineer")

        # Sanitize questions
        session_state["questions"] = [sanitize_string(q) for q in raw_questions if sanitize_string(q)]
        session_state["current_question_index"] = 0  # Reset index

        return session_state["questions"]

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return []

# function to upload the pdf file to extract questions
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Handles PDF upload and extracts questions """
    global session_state

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    questions = read_pdf_tables(file_location)

    if not questions:
        raise HTTPException(status_code=500, detail="Failed to generate questions.")

    return {"message": "Questions generated. Click 'Next Question' to generate audio.", "total_questions": len(questions)}

# function to play the next question only when the button is clicked
@app.get("/play-next-question")
async def play_next_question():
    """Returns the next question's audio file URL which is only generated when the button is clicked."""
    global session_state

    if not session_state["questions"]:
        raise HTTPException(status_code=400, detail="No questions available. Please upload a new PDF.")

    if session_state["current_question_index"] >= len(session_state["questions"]):
        return {"message" : "No more questions available."}

    # Get the next question
    question_text = session_state["questions"][session_state["current_question_index"]]

    if not question_text or question_text.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid question text for speech synthesis.")

    print(f"🎙️ Playing Question {session_state['current_question_index'] + 1}: {question_text}")

    # Generate filename based on the current question index and save as static MP3 file
    filename = f"question_{session_state['current_question_index'] + 1}.mp3"

    # Generate speech only when the button is clicked for that particular question
    audio_path = text_to_speech(question_text, filename)

    if not audio_path or not os.path.exists(audio_path):
        raise HTTPException(status_code=500, detail="Generated audio file missing or invalid.")

    # Increment question index after returning the response
    session_state["current_question_index"] += 1

    return {"audio_url": f"http://127.0.0.1:8000/static/{filename}"}

# def read_docx(file_path):
#     doc = Document(file_path)
#     text = "\n".join([para.text for para in doc.paragraphs])
#     return text

# print(read_docx("sample.docx"))
# calling the main function
def main():
    text = read_pdf_tables("/Users/kp/capstone/backend/My current resume.pdf")
    
    # detect_face_confidence()
    # df = pd.read_csv("pose_face_data.csv")
    # print(df.head())
    


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="0.0.0.0", port=8000)
