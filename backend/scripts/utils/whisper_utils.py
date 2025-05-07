import os
import io
from faster_whisper import WhisperModel
from pydub import AudioSegment

# Load Whisper model with efficient quantization
model = WhisperModel("tiny", compute_type="int8")

def get_mispronounced_words(segments):
    """
    Extracts low-confidence words from a list of transcription segments.

    Args:
        segments (List[Segment]): List of segment objects with word-level probabilities

    Returns:
        List[Dict]: List of mispronounced words with low probability (< 0.75)
    """
    mispronounced = []

    for segment in segments:
        for word in getattr(segment, "words", []):
            if word.probability and word.probability < 0.75:
                mispronounced.append({
                    "word": word.word.strip()
                })

    return mispronounced

async def transcribe_audio(file):
    """
    Transcribes an uploaded audio file using Whisper and returns both transcript and mispronounced words.

    Steps:
    1. Read file and detect format
    2. Convert to mono 16kHz WAV
    3. Run Whisper transcription with word-level timestamps
    4. Return transcript and list of mispronounced words

    Args:
        file (UploadFile): Uploaded audio file

    Returns:
        Tuple[str, List[Dict]]: transcript text and mispronounced words
    """
    try:
        print("Received file:", file.filename)

        # Infer file extension (e.g., "mp4", "webm", "ogg")
        extension = os.path.splitext(file.filename)[1][1:].lower()
        print("Detected format:", extension)

        # Read audio data and convert to WAV
        data = await file.read()
        audio = AudioSegment.from_file(io.BytesIO(data), format=extension)
        audio = audio.set_frame_rate(16000).set_channels(1)

        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        buffer.seek(0)

        # Run Whisper transcription with word timestamps
        segments, info = model.transcribe(buffer, language="en", word_timestamps=True)

        # Compile transcript text
        transcript = " ".join([s.text for s in segments])

        # Identify mispronounced words based on probability
        mispronounced = get_mispronounced_words(segments)

        return transcript, mispronounced

    except Exception as e:
        print("Transcription Error:", str(e))
        raise e
