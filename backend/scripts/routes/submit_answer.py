from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from scripts.utils.whisper_utils import transcribe_audio
from scripts.utils.openai_utils import evaluate_with_chatgpt, evaluate_with_claude
from scripts.utils.scoring_utils import get_average_face_confidence, calculate_total_score
import os
from main import EVALUATION_LOG_PATH
import json
router = APIRouter()

@router.post("/submit-answer")
async def evaluate_response(file: UploadFile = File(...), question: str = Form(...)):
    print("🔁 /submit-answer endpoint hit")
    print("📄 File received:", file.filename)
    print("🧠 Question:", question)

    transcript, mispronounced_words = await transcribe_audio(file)
    print("📝 Transcript:", transcript)
    print("❌ Mispronounced:", mispronounced_words)

    gpt_result = evaluate_with_chatgpt(question, transcript)
    claude_result = evaluate_with_claude(question, transcript)

    print("🤖 GPT Result:", gpt_result)
    print("🤖 Claude Result:", claude_result)

    clarity = round((gpt_result["clarity"] + claude_result["clarity"]) / 2, 2)
    tech = round((gpt_result["technical_depth"] + claude_result["technical_depth"]) / 2, 2)
    structure = round((gpt_result["structure"] + claude_result["structure"]) / 2, 2)

    answer_score = round((clarity * 0.3 + tech * 0.4 + structure * 0.3), 2)
    pronunciation_score = max(2, 10 - len(mispronounced_words))
    face_conf = get_average_face_confidence()

    final_score = calculate_total_score(face_conf, answer_score, clarity, pronunciation_score)
    print("📊 Scores - Clarity:", clarity, "| Tech:", tech, "| Structure:", structure)
    print("🎯 Final Score:", final_score)

    output = {
        "question": question,
        "transcription": transcript,
        "clarity_score": clarity,
        "technical_score": tech,
        "structure_score": structure,
        "answer_score": answer_score,
        "pronunciation_score": pronunciation_score,
        "face_confidence": final_score,
        "final_score": final_score,
        "mispronounced_words": mispronounced_words,
        "feedback": {
            "gpt": gpt_result["feedback"],
            "claude": claude_result["feedback"],
        }
    }

    if not os.path.exists(EVALUATION_LOG_PATH):
        with open(EVALUATION_LOG_PATH, "w") as f:
            json.dump([output], f, indent=2)
    else:
        with open(EVALUATION_LOG_PATH, "r+") as f:
            data = json.load(f)
            data.append(output)
            f.seek(0)
            json.dump(data, f, indent=2)

        print(f"✅ Evaluation log written to: {EVALUATION_LOG_PATH}")

    return output
