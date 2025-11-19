import os
from typing import Dict, Any

from yt_dlp import YoutubeDL
from config import YTDLP_DOWNLOAD_DIR   # <─ changed


def download_audio_from_youtube(url: str) -> Dict[str, Any]:
    """
    Download audio from a YouTube URL using yt-dlp and return
    metadata including the local audio file path.
    Requires ffmpeg installed on the system.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(YTDLP_DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(info)
        base, _ = os.path.splitext(audio_path)
        audio_path = base + ".mp3"

    info["audio_path"] = audio_path
    return info
