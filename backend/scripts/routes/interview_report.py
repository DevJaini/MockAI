from fastapi import APIRouter
import json
from main import EVALUATION_LOG_PATH
from scripts.utils.openai_utils import summarize_feedback_with_gpt

router = APIRouter()

@router.get("/interview-report")
async def get_report():
    """
    Returns the full interview evaluation log, average scores, and an AI-generated summary.
    """
    try:
        with open(EVALUATION_LOG_PATH, "r") as f:
            data = json.load(f)
            if not data:
                return {"message": "Evaluation log is empty."}
    except FileNotFoundError:
        print("Evaluation log file not found.")
        return {"message": "No evaluations yet."}
    except json.JSONDecodeError:
        print("Evaluation log file is corrupted or not valid JSON.")
        return {"message": "Evaluation log is corrupted."}
    except Exception as e:
        print(f"Unexpected error reading evaluation log: {e}")
        return {"message": "An unexpected error occurred."}

    total = len(data)

    # Safely compute all averages
    def safe_avg(key):
        return round(sum(d.get(key, 0) for d in data) / total, 2)

    summary = {
        "average_clarity_score": safe_avg("clarity_score"),
        "average_technical_score": safe_avg("technical_score"),
        "average_structure_score": safe_avg("structure_score"),
        "average_face_confidence": safe_avg("face_confidence"),
        "average_pronunciation_score": safe_avg("pronunciation_score"),
        "average_final_score": safe_avg("final_score"),
    }

    # Collect GPT and Claude feedback only if available
    gpt_feedbacks = [
        entry["feedback"]["gpt"]
        for entry in data
        if "feedback" in entry and "gpt" in entry["feedback"]
    ]
    claude_feedbacks = [
        entry["feedback"]["claude"]
        for entry in data
        if "feedback" in entry and "claude" in entry["feedback"]
    ]

    overall_feedback = summarize_feedback_with_gpt(gpt_feedbacks, claude_feedbacks)

    return {
        "evaluations": data,
        "summary": summary,
        "overall_feedback": overall_feedback,
    }
