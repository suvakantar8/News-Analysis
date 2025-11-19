# yt_utils.py
import os
import tempfile
from typing import Dict, Any

from yt_dlp import YoutubeDL
from config import YTDLP_DOWNLOAD_DIR
import streamlit as st  # for secrets on Streamlit Cloud


def download_audio_from_youtube(url: str) -> Dict[str, Any]:
    """
    Download audio from a YouTube URL using yt-dlp.
    - Uses cookies if provided via env/Streamlit secrets.
    - Avoids ffmpeg by not using postprocessors (keeps native audio format).
    """
    # Read cookies from env / Streamlit secrets (optional but recommended for YouTube)
    cookies_txt = os.getenv("YOUTUBE_COOKIES") or getattr(st.secrets, "YOUTUBE_COOKIES", None)

    cookie_file_path = None
    if cookies_txt:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmp.write(cookies_txt.encode("utf-8"))
        tmp.close()
        cookie_file_path = tmp.name

    os.makedirs(YTDLP_DOWNLOAD_DIR, exist_ok=True)

    ydl_opts = {
        # Prefer an audio-only format that doesn’t need ffmpeg merging
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": os.path.join(YTDLP_DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "nocheckcertificate": True,
    }

    if cookie_file_path:
        ydl_opts["cookiefile"] = cookie_file_path

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(info)

    info["audio_path"] = audio_path
    return info
