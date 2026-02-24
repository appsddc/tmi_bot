import re
import logging
import feedparser
import requests

try:
    from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
    YT_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: youtube-transcript-api import failed: {e}")
    YT_AVAILABLE = False

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
    if not YT_AVAILABLE:
        logger.error("youtube-transcript-api is not available — import failed at startup.")
        return None

    video_id = _extract_youtube_id(url)
    if not video_id:
        logger.warning(f"Could not extract YouTube video ID from: {url}")
        return None

    try:
        ytt = YouTubeTranscriptApi()
        fetched = ytt.fetch(video_id, languages=["en", "en-GB"])
        chunks = []
        for snippet in fetched.snippets:
            minutes = int(snippet.start // 60)
            seconds = int(snippet.start % 60)
            chunks.append(f"[{minutes:02d}:{seconds:02d}] {snippet.text}")
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
    """
    try:
        feed = feedparser.parse(url)
        if feed.entries:
            entry = feed.entries[0]
            title = entry.get("title", "")
            summary = entry.get("summary", "") or entry.get("description", "")
            content = entry.get("content", [{}])[0].get("value", "")
            return f"TITLE: {title}\n\nSHOW NOTES:\n{summary or content}"

        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()

        return text[:8000] if text else None

    except Exception as e:
        logger.error(f"Podcast transcript error for {url}: {e}")
        return None