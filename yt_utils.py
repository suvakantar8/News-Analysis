# yt_utils.py
import os
import tempfile
from typing import Dict, Any

from yt_dlp import YoutubeDL
from config import YTDLP_DOWNLOAD_DIR
import streamlit as st


def download_audio_from_youtube(url: str) -> Dict[str, Any]:
    """
    Download audio in a format accepted by Groq Whisper API.
    We force yt-dlp to pick only native m4a/webm formats so ffmpeg is NOT required.
    """
    # Load cookies (optional but recommended)
    cookies_txt = os.getenv("YOUTUBE_COOKIES") or getattr(st.secrets, "YOUTUBE_COOKIES", None)

    cookie_file_path = None
    if cookies_txt:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmp.write(cookies_txt.encode("utf-8"))
        tmp.close()
        cookie_file_path = tmp.name

    os.makedirs(YTDLP_DOWNLOAD_DIR, exist_ok=True)

    # Force formats YouTube ALWAYS provides natively WITHOUT FFMPEG:
    # - m4a (AAC audio-only)
    # - webm (Opus audio-only)
    ydl_opts = {
        "format": (
            "bestaudio[ext=m4a]/"  # first try m4a
            "bestaudio[ext=webm]/"  # fallback to webm
            "bestaudio"  # final fallback
        ),
        "outtmpl": os.path.join(YTDLP_DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "nocheckcertificate": True,
        "overwrites": True,
    }

    if cookie_file_path:
        ydl_opts["cookiefile"] = cookie_file_path

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(info)

    # Validate extension for Groq API
    allowed = (".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".ogg", ".opus", ".wav", ".webm")
    ext = os.path.splitext(audio_path)[-1].lower()

    if ext not in allowed:
        raise ValueError(
            f"Downloaded file format '{ext}' is not allowed by Groq. "
            f"File: {audio_path}"
        )

    info["audio_path"] = audio_path
    return info
