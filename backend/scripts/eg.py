# from fastapi import FastAPI, UploadFile, File
# from pydantic import BaseModel
# import openai
# import whisper
# import mediapipe as mp
# import cv2
# import pyttsx3
# import asyncio
# import numpy as np
# import os

# app = FastAPI()

# # Load AI models
# whisper_model = whisper.load_model("base")
# mp_face = mp.solutions.face_detection.FaceDetection()

# # OpenAI API Key
# openai.api_key = "YOUR_OPENAI_API_KEY"

# # Text-to-Speech Engine
# tts_engine = pyttsx3.init()


# class ResumeInput(BaseModel):
#     resume_text: str
#     job_description: str

# # Generate AI Interview Questions


# @app.post("/generate_questions")
# def generate_questions(data: ResumeInput):
#     prompt = f"Generate 5 interview questions based on this resume: {data.resume_text} and job description: {data.job_description}"
#     response = openai.ChatCompletion.create(
#         model="gpt-4", messages=[{"role": "user", "content": prompt}])
#     return {"questions": response['choices'][0]['message']['content'].split("\n")}

# # Convert AI Question to Speech


# @app.post("/generate_audio")
# def generate_audio(text: str):
#     audio_file = "question_audio.mp3"
#     tts_engine.save_to_file(text, audio_file)
#     tts_engine.runAndWait()
#     return {"audio_url": f"/static/{audio_file}"}

# # Speech-to-Text Conversion


# @app.post("/transcribe_audio")
# async def transcribe_audio(file: UploadFile = File(...)):
#     audio_path = f"temp_audio/{file.filename}"
#     with open(audio_path, "wb") as buffer:
#         buffer.write(await file.read())

#     result = whisper_model.transcribe(audio_path)
#     return {"transcription": result["text"]}

# # Body Language Analysis


# @app.post("/analyze_video")
# async def analyze_video(file: UploadFile = File(...)):
#     video_path = f"temp_video/{file.filename}"
#     with open(video_path, "wb") as buffer:
#         buffer.write(await file.read())

#     cap = cv2.VideoCapture(video_path)
#     confidence_scores = []

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = mp_face.process(frame_rgb)
#         if results.detections:
#             for detection in results.detections:
#                 confidence_scores.append(detection.score[0])

#     cap.release()

#     avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.5
#     return {"confidence_score": round(avg_confidence * 100, 2)}

from faster_whisper import WhisperModel
import soundfile as sf
import numpy as np

# Load saved debug audio
audio_np, sample_rate = sf.read("debug_audio.wav")
audio_np = np.array(audio_np, dtype=np.float32)

# Print shape to confirm it's correct
print(f"✅ Debug Audio Shape: {audio_np.shape} - Sample Rate: {sample_rate}")

# Initialize Whisper
whisper_model = WhisperModel("small")  # Try "tiny" if this still crashes

# Transcribe manually
segments, _ = whisper_model.transcribe(audio_np, language="en")
transcribed_text = " ".join([segment.text for segment in segments])

print("✅ Whisper Output:", transcribed_text)
