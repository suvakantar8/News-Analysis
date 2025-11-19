from typing import Dict, Any

import whisper
from config import WHISPER_MODEL_NAME   # <─ changed

_model = None


def _get_whisper_model():
    global _model
    if _model is None:
        _model = whisper.load_model(WHISPER_MODEL_NAME)
    return _model


def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    """
    Transcribe audio with Whisper.
    Returns: {"text": "...", "segments": [...]}
    """
    model = _get_whisper_model()
    result = model.transcribe(audio_path)
    return {
        "text": result.get("text", "").strip(),
        "segments": result.get("segments", []),
    }
