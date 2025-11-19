# transcription.py
from typing import Dict, Any
import os
import tempfile

from llm_client import client  # reuse OpenAI-compatible client

# Keep audio upload under 20 MB to avoid 413 errors
MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB


def _make_limited_audio_copy(audio_path: str) -> str:
    """
    Ensure the audio file is not larger than MAX_UPLOAD_BYTES.
    If it is, create a new temp file that contains only the first MAX_UPLOAD_BYTES bytes.
    This avoids 413 'Request Entity Too Large' errors from the API.
    """
    size = os.path.getsize(audio_path)
    if size <= MAX_UPLOAD_BYTES:
        return audio_path  # already small enough

    # Create a truncated copy
    base, ext = os.path.splitext(audio_path)
    with open(audio_path, "rb") as src, tempfile.NamedTemporaryFile(
        delete=False, suffix=ext
    ) as dst:
        dst.write(src.read(MAX_UPLOAD_BYTES))
        limited_path = dst.name

    return limited_path


def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    """
    Transcribe audio using a hosted Whisper-like model via an OpenAI-compatible API.

    For Groq:
      - OPENAI_BASE_URL="https://api.groq.com/openai/v1"
      - model="whisper-large-v3"
    """
    model_name = "whisper-large-v3"  # Groq's transcription model

    # Ensure file size is within safe limits for the API
    safe_audio_path = _make_limited_audio_copy(audio_path)

    with open(safe_audio_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model=model_name,
            file=f,
            response_format="json",
        )

    text = getattr(resp, "text", "") if resp else ""
    return {
        "text": (text or "").strip(),
        "segments": [],  # we don't need segments for classification
    }
