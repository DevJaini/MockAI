from fastapi import APIRouter, HTTPException
from scripts.utils.audio_utils import text_to_speech
import os
import re

router = APIRouter()

def clean_question(raw_question):
    """
    Remove numbering and bold labels like "**Technical Question:**" from the question.
    """
    # Remove number prefix like "1. "
    question = re.sub(r"^\d+\.\s*", "", raw_question)

    # Remove bold section like "**Technical Question:**"
    question = re.sub(r"\*\*(.*?)\*\*:", "", question)

    return question.strip()

@router.get("/play-question")
async def play_question():
    from scripts.routes.upload_resume import session_state

    if session_state["current_index"] >= len(session_state["questions"]):
        return {"message": "No more questions."}

    raw_question = session_state["questions"][session_state["current_index"]]
    question_text = clean_question(raw_question)

    filename = f"question_{session_state['current_index'] + 1}.mp3"
    path = text_to_speech(question_text, filename)

    session_state["current_index"] += 1
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

    return {
        "audio_url": f"{BASE_URL}/static/{filename}",
        "question_text": question_text
    }
