import re
import logging
import feedparser
import requests
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

logger = logging.getLogger(__name__)


def get_transcript(url: str) -> str | None:
    """
    Given a URL, attempt to retrieve a transcript.
    Tries YouTube first, then falls back to podcast RSS/show notes.
    Returns plain text transcript or None if unavailable.
    """
    if _is_youtube(url):
        return _get_youtube_transcript(url)
    else:
        return _get_podcast_transcript(url)


def _is_youtube(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url


def _extract_youtube_id(url: str) -> str | None:
    """Extract the video ID from various YouTube URL formats."""
    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:embed/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def _get_youtube_transcript(url: str) -> str | None:
    """Fetch auto-generated or manual captions from YouTube."""
    video_id = _extract_youtube_id(url)
    if not video_id:
        logger.warning(f"Could not extract YouTube video ID from: {url}")
        return None

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-GB"])
        # Join all segments into a single readable string with rough timestamps
        chunks = []
        for entry in transcript_list:
            minutes = int(entry["start"] // 60)
            seconds = int(entry["start"] % 60)
            chunks.append(f"[{minutes:02d}:{seconds:02d}] {entry['text']}")
        return "\n".join(chunks)

    except NoTranscriptFound:
        logger.warning(f"No English transcript found for video: {video_id}")
        return None
    except TranscriptsDisabled:
        logger.warning(f"Transcripts disabled for video: {video_id}")
        return None
    except Exception as e:
        logger.error(f"YouTube transcript error for {video_id}: {e}")
        return None


def _get_podcast_transcript(url: str) -> str | None:
    """
    For non-YouTube URLs, try to get useful text from:
    1. RSS feed description/show notes (often contains key topics)
    2. Raw page content as a fallback
    
    Note: Full podcast transcripts via RSS are rare — this gives the LLM
    enough context (title + description) to do a partial analysis.
    """
    try:
        # Try treating it as an RSS feed directly
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            title = entry.get("title", "")
            summary = entry.get("summary", "") or entry.get("description", "")
            content = entry.get("content", [{}])[0].get("value", "")
            return f"TITLE: {title}\n\nSHOW NOTES:\n{summary or content}"

        # Fall back to fetching the page and pulling readable text
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        # Very basic text extraction — strips HTML tags
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()

        # Return first 8000 chars — enough for LLM context without blowing token limits
        return text[:8000] if text else None

    except Exception as e:
        logger.error(f"Podcast transcript error for {url}: {e}")
        return None