import json
import os
from datetime import datetime
from main import FACE_LOG_PATH

def get_average_face_confidence():
    """
    Reads face confidence scores from the log file and returns a weighted average.
    Applies a penalty if too many frames had no face detected (score = 0).

    Returns:
        float: Final face confidence score between 0 and 100.
    """
    print("Called get_average_face_confidence", flush=True)

    if not os.path.exists(FACE_LOG_PATH):
        print(f"File not found: {FACE_LOG_PATH}", flush=True)
        return 0

    try:
        with open(FACE_LOG_PATH, "r") as f:
            data = json.load(f)

        if not data:
            return 0

        scores = [entry["confidence"] for entry in data]
        missing_frames = sum(1 for score in scores if score == 0)

        # Apply penalty if many frames had no face detected
        penalty = min((missing_frames / len(scores)) * 20, 20)  # Max penalty = 20

        average_score = sum(scores) / len(scores)
        final_score = max(0, average_score - penalty)

        return round(final_score, 2)

    except Exception as e:
        print("Error reading face confidence log:", e)
        return 0

def calculate_total_score(face_conf, answer_score, clarity, pronunciation):
    """
    Computes the weighted total score for an interview response.

    Args:
        face_conf (float): Face confidence score (0-100)
        answer_score (float): Score from combined technical + structural evaluation
        clarity (float): Clarity score (1–10)
        pronunciation (float): Pronunciation score (1–10)

    Returns:
        float: Weighted total score, normalized.
    """
    # Define weights for each component
    w1, w2, w3, w4 = 0.2, 0.9, 0.3, 0.8

    total = (
        face_conf * w1 +
        answer_score * w2 +
        clarity * w3 +
        pronunciation * w4
    )

    # Normalize by total weights
    return round(total / (w1 + w2 + w3 + w4), 2)
