import json
import os
from datetime import datetime

LOG_PATH = "face_confidence_log.json"

def get_average_face_confidence():
    if not os.path.exists(LOG_PATH):
        return 0

    try:
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
        if not data:
            return 0
        scores = [entry["confidence"] for entry in data]
        return sum(scores) / len(scores)
    except Exception as e:
        print("Error reading face confidence log:", e)
        return 0

def calculate_total_score(face_conf, answer_score, clarity, pronunciation):
    w1, w2, w3, w4 = 0.5, 0.9, 0.3, 0.8
    total = (face_conf * w1 +
             answer_score * w2 +
             clarity * w3 +
             pronunciation * w4)
    return round(total / (w1 + w2 + w3 + w4), 2)
