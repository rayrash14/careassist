from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from app.services.text_to_speech import text_to_speech
from app.services.speech_to_text import transcribe_audio
from app.services.translation_service import translate_text

import shutil, os, uuid, subprocess

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a"}
MAX_DURATION_SECONDS = 30

def get_audio_duration(file_path: str) -> float:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of",
             "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        return float(result.stdout)
    except Exception:
        return -1

@router.post("/transcribe")
async def transcribe_voice(file: UploadFile = File(...), lang: str = "en"):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    filename = f"tmp_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join("/tmp", filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        duration = get_audio_duration(file_path)
        if duration > MAX_DURATION_SECONDS:
            raise HTTPException(status_code=400, detail="Audio too long. Limit: 30s.")

        transcript = transcribe_audio(file_path, language=lang)

        # Translate Hindi to English (for consistency in backend)
        if lang == "hi":
            transcript = translate_text(transcript, from_lang="hi", to_lang="en")

        return {"transcript": transcript}

    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Transcription failed: {e}"})

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.post("/speak")
async def speak_text(payload: dict):
    text = payload.get("text")
    lang = payload.get("lang", "en")  # "hi" or "en"

    if not text:
        return {"error": "No text provided."}

    # ✅ Pass language to TTS
    file_path = text_to_speech(text, lang)

    if not file_path or not os.path.exists(file_path):
        return {"error": "TTS failed."}

    def stream_audio():
        with open(file_path, "rb") as f:
            yield from f

    return StreamingResponse(stream_audio(), media_type="audio/wav")
