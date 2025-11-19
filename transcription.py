# transcription.py
from typing import Dict, Any
from llm_client import client  # reuse OpenAI-compatible client


def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    """
    Transcribe audio using a hosted Whisper-like model via OpenAI-compatible API.

    For Groq:
      - OPENAI_BASE_URL="https://api.groq.com/openai/v1"
      - model="whisper-large-v3"

    For OpenAI:
      - OPENAI_BASE_URL="https://api.openai.com/v1"
      - model="gpt-4o-transcribe" or "whisper-1" (depending on your account)
    """
    # Choose a default model; override via env if you want
    model_name = "whisper-large-v3"  # Groq's transcription model

    with open(audio_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model=model_name,
            file=f,
            response_format="json",
        )

    # openai-python returns an object; access .text
    text = getattr(resp, "text", "") if resp else ""
    return {
        "text": (text or "").strip(),
        "segments": [],  # we don't need segments for news classification
    }
