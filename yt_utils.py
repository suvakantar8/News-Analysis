import os
import tempfile
from typing import Dict, Any

from yt_dlp import YoutubeDL
from config import YTDLP_DOWNLOAD_DIR
import streamlit as st


def download_audio_from_youtube(url: str) -> Dict[str, Any]:
    """
    Download audio in a format accepted by Groq Whisper API.

    Strategy:
    - Let yt-dlp pick the best *audio-only* stream if possible (bestaudio)
    - If not available, fall back to best single-file stream (best)
    - We do NOT use any postprocessors → no ffmpeg needed.
    - Finally, we validate that the file extension is one supported by Groq.
    """

    # Load cookies (optional but recommended for YouTube)
    cookies_txt = os.getenv("YOUTUBE_COOKIES") or getattr(st.secrets, "YOUTUBE_COOKIES", None)

    cookie_file_path = None
    if cookies_txt:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmp.write(cookies_txt.encode("utf-8"))
        tmp.close()
        cookie_file_path = tmp.name

    os.makedirs(YTDLP_DOWNLOAD_DIR, exist_ok=True)

    # More flexible format selection:
    # - "bestaudio": best audio-only stream (no merging needed)
    # - "best": best single file (video+audio) if available
    # Both should be downloadable without ffmpeg if they are single streams.
    ydl_opts = {
        "format": "bestaudio/best",
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

    # Groq allowed extensions:
    # flac mp3 mp4 mpeg mpga m4a ogg opus wav webm
    allowed_exts = (".flac", ".mp3", ".mp4", ".mpeg", ".mpga",
                    ".m4a", ".ogg", ".opus", ".wav", ".webm")

    ext = os.path.splitext(audio_path)[-1].lower()

    if ext not in allowed_exts:
        raise ValueError(
            f"Downloaded file format '{ext}' is not allowed by Groq. "
            f"Try a different YouTube Short. (File: {audio_path})"
        )

    info["audio_path"] = audio_path
    return info
