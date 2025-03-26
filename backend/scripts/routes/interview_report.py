from fastapi import APIRouter
from scripts.routes.submit_answer import evaluations
from scripts.routes.upload_resume import session_state

router = APIRouter()

@router.get("/interview-report")
async def get_report():
    average_face_score = 82.4  # Dummy value for now
    return {
        "questions": session_state["questions"],
        "answers": evaluations,
        "face_confidence": average_face_score,
        "final_score": "Strong performance, but watch tone in Q4."
    }
