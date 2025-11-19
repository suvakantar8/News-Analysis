import os
import tempfile
from yt_dlp import YoutubeDL

def download_audio_from_youtube(url: str):
    """
    Download audio from YouTube Shorts using yt-dlp + cookies.
    Required to bypass bot checks on Streamlit Cloud.
    """
    # Read cookies from Streamlit secrets (or env var)
    cookies_txt = os.getenv("YOUTUBE_COOKIES")

    cookie_file_path = None
    if cookies_txt:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmp.write(cookies_txt.encode("utf-8"))
        tmp.close()
        cookie_file_path = tmp.name

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "nocheckcertificate": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        # Use cookies if available
        "cookiefile": cookie_file_path,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(info)

    info["audio_path"] = audio_path
    return info
