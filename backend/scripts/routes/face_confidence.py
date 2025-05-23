from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import base64, io, time, os, json
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
from main import FACE_LOG_PATH

router = APIRouter()

FRAME_WIDTH = 640
FRAME_HEIGHT = 600
# Decode base64-encoded image from frontend
async def decode_image(img_string):
    try:
        img_data = base64.b64decode(img_string.split(",")[1])
        image = Image.open(io.BytesIO(img_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

# Append face confidence data to local JSON file with timestamp
def append_face_confidence(conf):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = {"timestamp": timestamp, "confidence": conf}
    print(f"Logging confidence entry: {entry}")

    try:
        if not os.path.exists(FACE_LOG_PATH):
            with open(FACE_LOG_PATH, "w") as f:
                json.dump([entry], f, indent=2)
        else:
            with open(FACE_LOG_PATH, "r+") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("Log file was empty or corrupted. Resetting.")
                    data = []

                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error logging face confidence: {e}")

# WebSocket route for real-time face confidence detection
@router.websocket("/face-confidence")
async def detect_face_confidence(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected: face-confidence")

    last_logged_time = time.time()

    try:
        with mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1) as face_mesh:
            while True:
                data = await websocket.receive_json()

                if "image" not in data:
                    print("No image key in received data.")
                    continue

                frame = await decode_image(data["image"])
                if frame is None:
                    print("Frame decoding failed.")
                    continue

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb)

                face_confidence = 100.0

                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    nose_x = int(landmarks[1].x * FRAME_WIDTH)
                    left_eye_x = int(landmarks[33].x * FRAME_WIDTH)
                    right_eye_x = int(landmarks[263].x * FRAME_WIDTH)

                    center_x = FRAME_WIDTH // 2
                    deviation_x = abs(nose_x - center_x)
                    max_deviation = FRAME_WIDTH // 3

                    if deviation_x > max_deviation:
                        face_confidence -= min((deviation_x / FRAME_WIDTH) * 100, 40)

                    eye_distance = abs(left_eye_x - right_eye_x)
                    expected_eye_distance = FRAME_WIDTH // 5
                    tilt_penalty = min(abs(expected_eye_distance - eye_distance) / expected_eye_distance * 40, 30)
                    face_confidence -= tilt_penalty

                    face_confidence = max(min(face_confidence, 100), 0)
                else:
                    face_confidence = 0  # No face detected

                # Log every 2 seconds
                if time.time() - last_logged_time >= 2:
                    append_face_confidence(face_confidence)
                    last_logged_time = time.time()

                await websocket.send_json({"face_confidence": face_confidence})

    except WebSocketDisconnect:
        print("WebSocket disconnected.")
    except Exception as e:
        print(f"WebSocket error: {e}")
