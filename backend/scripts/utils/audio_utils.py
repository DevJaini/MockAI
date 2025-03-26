import os
from gtts import gTTS

STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

def text_to_speech(text: str, filename: str) -> str:
    """
    Converts the given text to an MP3 file using gTTS
    and returns the file path.

    Args:
        text (str): The question or sentence to convert to speech.
        filename (str): The name of the output MP3 file (e.g., "question_1.mp3").

    Returns:
        str: Path to the saved MP3 file (relative to static/).
    """
    file_path = os.path.join(STATIC_DIR, filename)

    # Avoid regenerating the same file
    if os.path.exists(file_path):
        print(f"🔊 Reusing existing speech file: {file_path}")
        return file_path

    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(file_path)
        print(f"🔊 Saved speech: {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ Error generating speech: {e}")
        return None
