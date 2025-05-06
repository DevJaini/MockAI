from fastapi import APIRouter
import json
from main import EVALUATION_LOG_PATH
from scripts.utils.openai_utils import summarize_feedback_with_gpt 

router = APIRouter()

@router.get("/interview-report")
async def get_report():
    try:
        with open(EVALUATION_LOG_PATH, "r") as f:
            data = json.load(f)
    except:
        return {"message": "No evaluations yet."}

    if not data:
        return {"message": "Evaluation log is empty."}

    # Calculate averages
    total = len(data)
    sum_clarity = sum(d.get("clarity_score", 0) for d in data)
    sum_tech = sum(d.get("technical_score", 0) for d in data)
    sum_structure = sum(d.get("structure_score", 0) for d in data)
    sum_face = sum(d.get("face_confidence", 0) for d in data)
    sum_final = sum(d.get("final_score", 0) for d in data)
    sum_pron = sum(d.get("pronunciation_score", 0) for d in data)

    summary = {
        "average_clarity_score": round(sum_clarity / total, 2),
        "average_technical_score": round(sum_tech / total, 2),
        "average_structure_score": round(sum_structure / total, 2),
        "average_face_confidence": round(sum_face / total, 2),
        "average_pronunciation_score": round(sum_pron / total, 2),
        "average_final_score": round(sum_final / total, 2)
    }

    # Extract all GPT and Claude feedbacks
    gpt_feedbacks = [entry["feedback"]["gpt"] for entry in data if "feedback" in entry and "gpt" in entry["feedback"]]
    claude_feedbacks = [entry["feedback"]["claude"] for entry in data if "feedback" in entry and "claude" in entry["feedback"]]

    overall_feedback = summarize_feedback_with_gpt(gpt_feedbacks, claude_feedbacks)

    return {
        "evaluations": data,
        "summary": summary,
        "overall_feedback": overall_feedback
    }
