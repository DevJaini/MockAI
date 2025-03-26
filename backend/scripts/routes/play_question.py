from fastapi import APIRouter, HTTPException
from scripts.utils.audio_utils import text_to_speech
import os

router = APIRouter()

@router.get("/play-question")
async def play_question():
    from scripts.routes.upload_resume import session_state

    if session_state["current_index"] >= len(session_state["questions"]):
        return {"message": "No more questions."}

    q = session_state["questions"][session_state["current_index"]]
    filename = f"question_{session_state['current_index'] + 1}.mp3"
    path = text_to_speech(q, filename)


    session_state["current_index"] += 1
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    return {"audio_url": f"{BASE_URL}/static/{filename}"}

