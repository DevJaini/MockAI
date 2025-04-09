from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import base64, cv2, numpy as np, io
from PIL import Image
import mediapipe as mp

router = APIRouter()

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()
FRAME_WIDTH = 640
FRAME_HEIGHT = 600

async def decode_image(img_string):
    try:
        img_data = base64.b64decode(img_string.split(',')[1])
        image = Image.open(io.BytesIO(img_data))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

@router.websocket("/face-confidence")
async def detect_face_confidence(websocket: WebSocket):
    await websocket.accept()
    print("Connected to WebSocket")

    try:
        while True:
            data = await websocket.receive_json()
            if "image" not in data:
                continue

            frame = await decode_image(data["image"])
            if frame is None:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = face_mesh.process(rgb_frame)

            face_confidence = 100.0

            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0].landmark
                nose_x = int(face_landmarks[1].x * FRAME_WIDTH)
                left_eye_x = int(face_landmarks[33].x * FRAME_WIDTH)
                right_eye_x = int(face_landmarks[263].x * FRAME_WIDTH)

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
                face_confidence = 0

            await websocket.send_json({"face_confidence": face_confidence})
    except WebSocketDisconnect:
        print("WebSocket closed")
    except Exception as e:
        print(f"WebSocket error: {e}")
