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
        print("1", EVALUATION_LOG_PATH)
        return {"message": "No evaluations yet."}

    latest = data[-1]

    # Pick best model feedback based on highest technical score
    # gpt = latest.get("feedback", {}).get("gpt", {})
    # claude = latest.get("feedback", {}).get("claude", {})

    # try:
    #     gpt_score = gpt.get("technical_score", 0)
    #     claude_score = claude.get("technical_score", 0)

    #     print("gpt_score", gpt_score)
    #     print("claude_score", claude_score)

    #     best = gpt if gpt_score >= claude_score else claude

    #     print("response", best)
    # except:
    #     best = {"feedback": "No valid evaluation."}

    return {
        "face_confidence": latest.get("face_confidence", 0),
        "clarity_score": latest.get("clarity_score", 0),
        "technical_score": latest.get("technical_score", 0),
        "structure_score": latest.get("structure_score", 0),
        "pronunciation_score": latest.get("pronunciation_score", 0),
        "final_score": latest.get("final_score", 0),
        "mispronounced_words": latest.get("mispronounced_words", []),
        "feedback": latest.get("feedback", "N/A"),
    }