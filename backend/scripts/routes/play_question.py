from fastapi import APIRouter, HTTPException
import os
import re
from scripts.utils.audio_utils import text_to_speech

router = APIRouter()

def clean_question(raw_question: str) -> str:
    """
    Cleans a question string by removing numbering and section labels.

    Example:
        "1. **Technical Question:** What is a closure in JavaScript?"
        -> "What is a closure in JavaScript?"
    """
    # Remove leading number (e.g., "1. ")
    question = re.sub(r"^\d+\.\s*", "", raw_question)
    
    # Remove bold labels like "**Technical Question:**"
    question = re.sub(r"\*\*(.*?)\*\*[:：]?\s*", "", question)

    return question.strip()

@router.get("/play-question")
async def play_question():
    """
    Returns the next question from session state along with the TTS audio URL.
    """
    try:
        from scripts.routes.upload_resume import session_state

        if session_state["current_index"] >= len(session_state["questions"]):
            return {"message": "No more questions."}

        raw_question = session_state["questions"][session_state["current_index"]]
        question_text = clean_question(raw_question)

        filename = f"question_{session_state['current_index'] + 1}.mp3"
        path = text_to_speech(question_text, filename)

        if not path or not os.path.exists(path):
            print(f"[ERROR] Audio file not created: {filename}")
            raise HTTPException(status_code=500, detail="Failed to generate question audio.")

        session_state["current_index"] += 1
        BASE_URL = os.getenv("BASE_URL", "https://mockai-mqnl.onrender.com")

        return {
            "audio_url": f"{BASE_URL}/static/{filename}",
            "question_text": question_text
        }

    except Exception as e:
        print(f"[ERROR] play-question failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while playing question.")
