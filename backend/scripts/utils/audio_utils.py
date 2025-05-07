import os
from gtts import gTTS

# Directory to store generated MP3s
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

def text_to_speech(text: str, filename: str) -> str:
    """
    Converts the given text into an MP3 audio file using Google Text-to-Speech.
    
    If the file already exists, it will be reused.

    Args:
        text (str): The text to convert to speech.
        filename (str): The desired filename for the audio file.

    Returns:
        str: Path to the generated or reused MP3 file, or None if failed.
    """
    file_path = os.path.join(STATIC_DIR, filename)

    if os.path.exists(file_path):
        print(f"[INFO] Reusing existing audio: {file_path}")
        return file_path

    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(file_path)
        print(f"[INFO] Audio saved: {file_path}")
        return file_path
    except Exception as e:
        print(f"[ERROR] Failed to generate speech: {e}")
        return None
