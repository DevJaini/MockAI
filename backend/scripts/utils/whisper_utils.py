import os
from faster_whisper import WhisperModel
from pydub import AudioSegment
import io

model = WhisperModel("tiny", compute_type="int8")

def get_mispronounced_words(segments):
    mispronounced = []
    for segment in segments:
        for word in getattr(segment, "words", []):
            if word.probability and word.probability < 0.75:
                mispronounced.append({
                    "word": word.word.strip()
                })
    return mispronounced

async def transcribe_audio(file):
    try:
        print("📥 Received:", file.filename)

        # Guess format from file extension
        extension = os.path.splitext(file.filename)[1][1:].lower()  # "mp4", "webm", etc.
        print("📦 Detected format:", extension)

        data = await file.read()
        audio = AudioSegment.from_file(io.BytesIO(data), format=extension)
        print("🔁 Converted to AudioSegment. Duration:", audio.duration_seconds, "sec")

        audio = audio.set_frame_rate(16000).set_channels(1)
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        buffer.seek(0)

        print("🎙️ Transcribing with Whisper...")
        segments, info = model.transcribe(buffer, language="en", word_timestamps=True)
        transcript = " ".join([s.text for s in segments])
        mispronounced = get_mispronounced_words(segments)

        print("📝 Transcript:", transcript)

        return transcript, mispronounced

    except Exception as e:
        print("❌ Transcription Error:", str(e))
        raise e
