# yt_utils.py
import os
import tempfile
from typing import Dict, Any
import streamlit as st
from yt_dlp import YoutubeDL
from config import YTDLP_DOWNLOAD_DIR


# Groq allowed formats
GROQ_ALLOWED_EXTS = (
    ".flac", ".mp3", ".mp4", ".mpeg", ".mpga",
    ".m4a", ".ogg", ".opus", ".wav", ".webm"
)


def download_audio_from_youtube(url: str) -> Dict[str, Any]:
    """
    Download an audio file from YouTube in a format acceptable by Groq.
    We use a strict fallback chain to ensure yt-dlp only picks valid formats.
    """

    # Optional: load cookies
    cookies_txt = os.getenv("YOUTUBE_COOKIES") or getattr(st.secrets, "YOUTUBE_COOKIES", None)

    cookie_file_path = None
    if cookies_txt:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmp.write(cookies_txt.encode("utf-8"))
        tmp.close()
        cookie_file_path = tmp.name

    os.makedirs(YTDLP_DOWNLOAD_DIR, exist_ok=True)

    # FORMAT STRATEGY (safe for Streamlit Cloud, no ffmpeg required):
    #
    # 1. Try native audio formats in this order:
    #    - m4a (AAC)
    #    - webm (Opus)
    #    - mp4 (AAC)
    #
    # 2. If not available, fallback to "bestaudio", but ONLY
    #    allow it if extension is in Groq's allowed list.
    #
    format_chain = (
        "bestaudio[ext=m4a]/"
        "bestaudio[ext=webm]/"
        "bestaudio[ext=mp4]/"
        "bestaudio/best"
    )

    ydl_opts = {
        "format": format_chain,
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "outtmpl": os.path.join(YTDLP_DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "overwrites": True,
    }

    if cookie_file_path:
        ydl_opts["cookiefile"] = cookie_file_path

    # Download
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(info)

    # Validate extension
    ext = os.path.splitext(audio_path)[-1].lower()

    if ext not in GROQ_ALLOWED_EXTS:
        raise ValueError(
            f"❌ Downloaded format '{ext}' is not allowed by Groq.\n"
            f"File: {audio_path}\n\n"
            f"This video does NOT provide audio in any Groq-supported format.\n"
            f"Try another YouTube Short or use a proxy / cookies."
        )

    info["audio_path"] = audio_path
    info["url"] = info.get("url") or info.get("requested_formats", [{}])[0].get("url")
    return info


