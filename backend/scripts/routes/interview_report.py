from fastapi import APIRouter
import json
from main import EVALUATION_LOG_PATH

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

    # Combine feedbacks from all
    all_feedbacks = []
    for entry in data:
        fb = entry.get("feedback", {})
        if isinstance(fb, dict):
            gpt = fb.get("gpt", "")
            claude = fb.get("claude", "")
            all_feedbacks.append(f"- GPT: {gpt}\n- Claude: {claude}")
        elif isinstance(fb, str):
            all_feedbacks.append(fb)

    overall_feedback = "\n\n".join(all_feedbacks)

    return {
        "evaluations": data,
        "summary": summary,
        "overall_feedback": overall_feedback
    }
