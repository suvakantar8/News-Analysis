# transcription.py
from typing import Dict, Any
import os
import tempfile

from llm_client import client  # reuse OpenAI-compatible client


# Keep upload under 20 MB to avoid 413 errors
MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB


def _make_limited_audio_copy(audio_path: str) -> str:
    """
    Ensure the audio file is not larger than MAX_UPLOAD_BYTES.
    If it is, create a truncated temp file containing only the first bytes.
    """
    size = os.path.getsize(audio_path)
    if size <= MAX_UPLOAD_BYTES:
        return audio_path

    base, ext = os.path.splitext(audio_path)
    with open(audio_path, "rb") as src, tempfile.NamedTemporaryFile(
        delete=False, suffix=ext
    ) as dst:
        dst.write(src.read(MAX_UPLOAD_BYTES))
        limited_path = dst.name

    return limited_path


def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    """
    Transcribe audio using Groq's Whisper-like model via OpenAI-compatible API.

    Requires:
      OPENAI_BASE_URL = "https://api.groq.com/openai/v1"
      OPENAI_API_KEY  = "gsk_..."
    """
    model_name = "whisper-large-v3"  # Groq transcription model

    safe_path = _make_limited_audio_copy(audio_path)

    with open(safe_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model=model_name,
            file=f,               # ✅ real file object, NOT a URL string
            response_format="json",
        )

    text = getattr(resp, "text", "") if resp else ""
    return {
        "text": (text or "").strip(),
        "segments": [],  # not needed for classification
    }
