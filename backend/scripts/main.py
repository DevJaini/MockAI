import pdfplumber
from docx import Document
import os
import pathlib
from dotenv import load_dotenv
import openai
import mediapipe as mp
import numpy as np
import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import base64
from PIL import Image
import uvicorn
import io
from faster_whisper import WhisperModel
from pydub import AudioSegment
from scipy.io.wavfile import write
from gtts import gTTS
import time
import re
from datetime import datetime
import json
import anthropic
from typing import Dict, Tuple
import random

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
# tts_engine = pyttsx3.init()
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
client_claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))
FACE_LOG_PATH = "face_confidence_log.json"
EVALUATION_LOG = "evaluation.json"

landmark_data = []

cap = cv2.VideoCapture(0)

confidence_data = []


FRAME_WIDTH = 640  
FRAME_HEIGHT = 600

def append_evaluation_log(question: str, transcription: str, feedback: str):

    sanitize_feedback = sanitize_string(feedback)

    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "answer_transcription": transcription,
        "feedback": sanitize_feedback
    }

    try:
        if not os.path.exists(EVALUATION_LOG):
            with open(EVALUATION_LOG, "w") as f:
                json.dump([log_entry], f, indent=2)
        else:
            with open(EVALUATION_LOG, "r+") as f:
                data = json.load(f)
                data.append(log_entry)
                f.seek(0)
                json.dump(data, f, indent=2)

        print("Feedback appended to evaluation log.")
    except Exception as e:
        print(f"Error writing evaluation log: {e}")

def append_face_confidence(conf):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"timestamp": timestamp, "confidence": conf}

    try:
        if not os.path.exists(FACE_LOG_PATH):
            with open(FACE_LOG_PATH, "w") as f:
                json.dump([entry], f, indent=2)
        else:
            with open(FACE_LOG_PATH, "r+") as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error writing face confidence: {e}")

def get_average_face_confidence():
    try:
        with open(FACE_LOG_PATH, "r") as f:
            data = json.load(f)
        if not data:
            return 0
        scores = [entry["confidence"] for entry in data]
        return sum(scores) / len(scores)
    except Exception as e:
        print(f"Error reading face log: {e}")
        return 0
    
def calculate_total_score(face_confidence, answer_score, clarity_score, pronunciation_score):
    w1, w2, w3, w4 = 0.5, 0.9, 0.3, 0.8
    total = (face_confidence * w1 +
             answer_score * w2 +
             clarity_score * w3 +
             pronunciation_score * w4)
    return round(total / (w1 + w2 + w3 + w4), 2)  # Normalize

@app.post("/final-evaluation")
async def final_evaluation(
    file: UploadFile = File(...),
    question: str = ""
):
    # Step 1: Transcribe audio
    converted_wav = await convert_audio(file)
    segments, _ = whisper_model.transcribe(converted_wav, language="en")
    transcription = " ".join([segment.text for segment in segments])

    if not transcription:
        raise HTTPException(status_code=500, detail="Transcription failed.")

    # Step 2: Evaluate using GPT & Claude
    gpt_result = evaluate_with_chatgpt(question, transcription)
    claude_result = evaluate_with_claude(question, transcription)

    # Step 3: Extract detailed scores
    clarity_scores = [gpt_result.get("clarity", 0), claude_result.get("clarity", 0)]
    technical_scores = [gpt_result.get("technical_depth", 0), claude_result.get("technical_depth", 0)]
    structure_scores = [gpt_result.get("structure", 0), claude_result.get("structure", 0)]

    # Step 4: Weighted average answer_score
    clarity_score = round(sum(clarity_scores) / len(clarity_scores), 2)
    technical_score = round(sum(technical_scores) / len(technical_scores), 2)
    structure_score = round(sum(structure_scores) / len(structure_scores), 2)

    # Assign custom weights for answer quality breakdown
    answer_score = round((clarity_score * 0.3 + technical_score * 0.4 + structure_score * 0.3), 2)

    pronunciation_score = 7  
    face_avg = get_average_face_confidence()

    final_score = calculate_total_score(face_avg, answer_score, clarity_score, pronunciation_score)

    feedback_combined = {
        "clarity": gpt_result.get("clarity_feedback", "N/A"),
        "technical_depth": gpt_result.get("technical_depth_feedback", "N/A"),
        "structure": gpt_result.get("structure_feedback", "N/A"),
        "improvement_suggestions": f"{gpt_result.get('feedback')} | {claude_result.get('feedback')}"
    }

    append_evaluation_log(question, transcription, feedback_combined)

    return {
        "transcription": transcription,
        "face_avg": round(face_avg, 2),
        "clarity_score": clarity_score,
        "technical_score": technical_score,
        "structure_score": structure_score,
        "answer_score": answer_score,
        "pronunciation_score": pronunciation_score,
        "final_score": final_score,
        "feedback": feedback_combined
    }



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

    last_logged_time = time.time()

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

            if time.time() - last_logged_time >= 2:
                append_face_confidence(face_confidence)
                last_logged_time = time.time()


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

def generate_interview_questions_claude(resume_text, job_description):
    prompt = f"""
        You are an AI job interview coach. Generate 5 technical and behavioral interview questions 
        based on the following resume and job description:

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Format your response as:
        1. [Question]
        2. [Question]
        3. [Question]
        4. [Question]
        5. [Question]
    """

        # Claude's message structure
    message = client.messages.create(
    model="claude-3-sonnet-20240229",  # You can also use 'claude-3-opus-20240229' or 'claude-3-haiku-20240307'
    max_tokens=1024,
    temperature=0.5,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
    )

    output_text = message.content[0].text  # Get plain text response
    questions = [line.strip() for line in output_text.split("\n") if line.strip()]
        
    print("\n".join(questions))  # Debug print
    return questions

# function to convert text to speech
def text_to_speech(text, output_file):
    """Converts text to speech and saves it as an MP3 file."""
    file_path = os.path.join(STATIC_DIR, output_file)

    if os.path.exists(file_path):
        print(f" Reusing existing speech file: {file_path}")
        return file_path

    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(file_path)
        print(f" Saved speech: {file_path}")
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

# Dynamic system prompt generator
def generate_system_prompt(criteria: Dict[str, Dict[int, str]], role_description: str) -> Tuple[str, Dict[str, int]]:
    preferences = {key: random.randint(1, 5) for key in criteria}
    descriptions = {key: criteria[key][val] for key, val in preferences.items()}
    prompt = f"{role_description} with the following preferences: {json.dumps(descriptions, ensure_ascii=False)}"
    return prompt, preferences

# Evaluation criteria for interview scoring
criteria = {
    "clarity": {
        1: "Prefers concise and minimal answers",
        2: "Values short but complete responses",
        3: "Likes balanced answers with good explanation",
        4: "Prefers detailed and descriptive answers",
        5: "Wants deeply detailed, step-by-step responses"
    },
    "technical_depth": {
        1: "Basic explanation is enough",
        2: "Values surface-level technical points",
        3: "Balanced depth and breadth",
        4: "Wants strong technical justification",
        5: "Seeks deep knowledge and thorough explanations"
    },
    "structure": {
        1: "Unstructured or casual answers are fine",
        2: "Basic logical flow preferred",
        3: "Likes moderate structure",
        4: "Wants well-organized answers",
        5: "Demands strong structure with intro-body-summary format"
    }
}

# Generate system prompts
chatgpt_system_prompt, _ = generate_system_prompt(criteria, "You are an AI interview evaluator")
claude_system_prompt, _ = generate_system_prompt(criteria, "You are a Claude-based interview evaluator")


def evaluate_with_chatgpt(question: str, answer: str) -> Dict:
    prompt = f"""
You are an expert AI interview evaluator. Based on the candidate's response to the question below, return a detailed evaluation in JSON format.

Evaluate the answer on three dimensions (scale 1–10):
- clarity
- technical_depth
- structure

Then, provide constructive feedback as a string.

Respond ONLY with valid JSON in this format:
{{
  "clarity": <1-10>,
  "technical_depth": <1-10>,
  "structure": <1-10>,
  "feedback": "<summary and suggestions>"
}}

Question: {question}
Answer: {answer}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": chatgpt_system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    try:
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        return {
            "clarity": 0,
            "technical_depth": 0,
            "structure": 0,
            "feedback": f"Parsing error: {str(e)}\nRaw: {response.choices[0].message.content}"
        }


def evaluate_with_claude(question: str, answer: str) -> Dict:
    prompt = f"""
You are a Claude-based AI interview evaluator. Based on the candidate's response, evaluate three dimensions (scale 1–10):

- clarity
- technical_depth
- structure

Provide your answer strictly in JSON like this:
{{
  "clarity": <1-10>,
  "technical_depth": <1-10>,
  "structure": <1-10>,
  "feedback": "<overall feedback with suggestions>"
}}

Question: {question}
Answer: {answer}
"""

    response = client_claude.messages.create(
        model="claude-3-5-sonnet-latest", 
        max_tokens=512,
        temperature=0.7,
        system=claude_system_prompt,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    content = response.content[0].text.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "clarity": 0,
            "technical_depth": 0,
            "structure": 0,
            "feedback": f"Invalid response from Claude: {content}"
        }


@app.post("/evaluate-response")
async def evaluate_response(file: UploadFile = File(...), question: str = ""):
    """Uploads user's spoken answer, transcribes it, and sends it to GPT for evaluation"""
    converted_wav = await convert_audio(file)

    if not converted_wav:
        raise HTTPException(status_code=500, detail="Audio conversion failed")

    segments, _ = whisper_model.transcribe(converted_wav, language="en")
    transcription = " ".join([segment.text for segment in segments])

    if not transcription:
        raise HTTPException(status_code=500, detail="Transcription failed")

    # feedback = evaluate_answer(question, transcription)
    # feedback_claude = evaluate_answer_claude(question, transcription)
    # print(question)
    # append_evaluation_log(question, transcription, feedback)

    # return {
    #     "transcription": transcription,
    #     "gpt_evaluation": feedback,
    #     "claude_evaluation": feedback_claude
    # }
     # GPT & Claude evaluations
    gpt_result = evaluate_with_chatgpt(question, transcription)
    claude_result = evaluate_with_claude(question, transcription)

    # Ensemble score (average)
    scores = [gpt_result.get("score", 0), claude_result.get("score", 0)]
    scores = [s for s in scores if isinstance(s, (int, float))]  # safe filter
    final_score = round(sum(scores) / len(scores), 2) if scores else "N/A"

    # Combine feedback
    feedback_combined = f"""
     GPT Feedback: {gpt_result.get("feedback")}
     Claude Feedback: {claude_result.get("feedback")}
    """

    # Optional: log full results
    append_evaluation_log(question, transcription, feedback_combined)

    return {
        "transcription": transcription,
        "gpt_score": gpt_result.get("score"),
        "claude_score": claude_result.get("score"),
        "final_score": final_score,
        "gpt_feedback": gpt_result.get("feedback"),
        "claude_feedback": claude_result.get("feedback"),
        "combined_feedback": feedback_combined.strip()
    }


def sanitize_feedback(feedback: str):
    if not isinstance(feedback, str):
        return feedback

   
    feedback = re.sub(r"^\*\*Feedback:\*\*\s*\n*", "", feedback.strip())
    return feedback.strip()


def read_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Ensemble Evaluation (replaces evaluate_answer)
def evaluate_answer(question: str, answer: str) -> Dict:
    gpt_eval = evaluate_with_chatgpt(question, answer)
    claude_eval = evaluate_with_claude(question, answer)

    gpt_score = gpt_eval.get("score", 0)
    claude_score = claude_eval.get("score", 0)

    final_score = round((gpt_score + claude_score) / 2, 2)
    feedback_combined = f"ChatGPT: {gpt_eval.get('feedback')} | Claude: {claude_eval.get('feedback')}"

    return {
        "final_score": final_score,
        "chatgpt_score": gpt_score,
        "claude_score": claude_score,
        "feedback": feedback_combined
    }
# calling the main function
def main():
    text = read_pdf_tables("/Users/kp/capstone/backend/My current resume.pdf")
    
    # detect_face_confidence()
    # df = pd.read_csv("pose_face_data.csv")
    # print(df.head())
    


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="0.0.0.0", port=8000)
