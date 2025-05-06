import os
from gtts import gTTS

STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

def text_to_speech(text: str, filename: str) -> str:
    file_path = os.path.join(STATIC_DIR, filename)

    if os.path.exists(file_path):
        print(f"Reusing audio: {file_path}")
        return file_path

    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(file_path)
        print(f"Audio saved: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None
