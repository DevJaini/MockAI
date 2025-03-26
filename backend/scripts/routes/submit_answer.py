from fastapi import APIRouter, UploadFile, File
from scripts.utils.whisper_utils import transcribe_audio
from scripts.utils.openai_utils import evaluate_answer

router = APIRouter()

evaluations = []

@router.post("/submit-answer")
async def submit_answer(file: UploadFile = File(...)):
    print("-------", file)
    transcript = await transcribe_audio(file)
    evaluation = evaluate_answer(transcript)
    evaluations.append(evaluation)
    return {"transcription": transcript, "evaluation": evaluation}
