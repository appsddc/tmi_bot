from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_transcript(url):
    try:
        # Extract Video ID
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if not video_id_match:
            return "Scraper failed: Valid YouTube ID not found."
        
        video_id = video_id_match.group(1)

        # 2026 Instance-based Fetch
        api = YouTubeTranscriptApi()
        fetched_transcript = api.fetch(video_id)
        
        # FIX: Access snippet.text (attribute) instead of snippet['text']
        full_text = " ".join([snippet.text for snippet in fetched_transcript])
        return full_text

    except Exception as e:
        return f"Scraper failed: {str(e)}"
