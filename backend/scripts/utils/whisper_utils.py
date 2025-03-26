import os
from faster_whisper import WhisperModel
from pydub import AudioSegment
import io
import traceback

model = WhisperModel("tiny", compute_type="int8")

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
        segments, _ = model.transcribe(buffer, language="en")
        transcript = " ".join([s.text for s in segments])
        print("📝 Transcript:", transcript)

        return transcript

    except Exception as e:
        print("❌ Transcription Error:", str(e))
        traceback.print_exc()
        raise e
