import whisper

# Load once
model = whisper.load_model("base")

def transcribe_audio(file_path: str, language: str = "en") -> str:
    try:
        result = model.transcribe(file_path, language=language, task="translate")
        return result["text"]
    except Exception as e:
        print(f"Transcription failed: {e}")
        return "Error: could not transcribe audio."

