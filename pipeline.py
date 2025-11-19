# pipeline.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from yt_utils import download_audio_from_youtube
from transcription import transcribe_audio
from llm_client import analyze_transcript


@dataclass
class NewsItem:
    video_url: str
    video_title: str
    channel: Optional[str]
    transcript: str
    is_news: bool
    category: Optional[str]
    headline: Optional[str]
    summary: Optional[str]
    tags: List[str] = field(default_factory=list)
    raw_llm_output: Dict[str, Any] = field(default_factory=dict)
    video_id: Optional[str] = None
    thumbnail: Optional[str] = None


def process_short_url(url: str) -> NewsItem:
    info = download_audio_from_youtube(url)

    video_title = info.get("title", "")
    channel = info.get("uploader", None)
    video_id = info.get("id", None)
    thumbnail = info.get("thumbnail", None)
    audio_path = info["audio_path"]

    # Remote transcription now
    transcription = transcribe_audio(audio_path)
    transcript_text = transcription["text"]

    analysis = analyze_transcript(transcript_text)

    is_news = bool(analysis.get("is_news"))
    category = analysis.get("category")
    headline = analysis.get("headline")
    summary = analysis.get("summary")
    tags = analysis.get("tags") or []

    return NewsItem(
        video_url=url,
        video_title=video_title,
        channel=channel,
        transcript=transcript_text,
        is_news=is_news,
        category=category,
        headline=headline,
        summary=summary,
        tags=tags,
        raw_llm_output=analysis,
        video_id=video_id,
        thumbnail=thumbnail,
    )
