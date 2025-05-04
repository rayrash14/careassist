from TTS.api import TTS
import os
import uuid
import textwrap
import soundfile as sf
import numpy as np

# Use an English-only, stable open-source model
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
#"tts_models/en/ljspeech/tacotron2-DDC"
tts = TTS(model_name=MODEL_NAME)

def text_to_speech(text: str, lang: str = "en") -> str:
    filename = f"tts_{uuid.uuid4().hex}.wav"
    file_path = os.path.join("/tmp", filename)

    # Determine speaker reference
    speaker_wav_path = (
        "app/assets/speakers/hi_clean.wav" if lang == "hi" else "app/assets/speakers/en_clean.wav"
    )

    try:
        print(f"[TTS] Generating audio. Language: {lang}")

        # Split into 150-char chunks
        chunks = textwrap.wrap(text, width=140, break_long_words=False)

        # Collect audio arrays
        full_audio = []

        for chunk in chunks:
            wav = tts.tts(
                text=chunk,
                speaker_wav=speaker_wav_path,
                language=lang
            )
            full_audio.append(wav)

        # Concatenate and save
        full_audio = np.concatenate(full_audio)
        sf.write(file_path, full_audio, samplerate=22050)
        print(f"[TTS] File saved: {file_path} | Size: {os.path.getsize(file_path)} bytes")

        return file_path

    except Exception as e:
        print(f"[TTS Error] {e}")
        return ""
