import os
import logging
import feedparser
from tmi_logic.scraper import get_transcript
from tmi_logic.sieve import analyze_transcript
from tmi_logic.telegram import send_message

logger = logging.getLogger(__name__)

# Your high-signal RSS feeds — add/remove as needed
FEEDS = [
    {
        "name": "Patrick Boyle",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCASM0cgfkJxQ1ICmRilfHLw"
    },
    {
        "name": "David McWilliams",
        "url": "https://feeds.megaphone.fm/the-david-mcwilliams-podcast"
    },
    {
        "name": "Dwarkesh Patel",
        "url": "https://www.dwarkeshpatel.com/feed"
    },
]

# Simple in-memory seen set — resets on each deploy/restart.
# For production, swap this for a small database or Render's persistent disk.
_seen_urls: set = set()


def run_daily_briefing(chat_id: str | int):
    """
    Checks each feed for new episodes, analyzes them,
    and sends a ranked digest to the given chat_id.
    """
    send_message(chat_id, "📡 *TMI Daily Briefing*\nScanning your feeds for signal...")

    results = []

    for feed_config in FEEDS:
        try:
            feed = feedparser.parse(feed_config["url"])
            if not feed.entries:
                logger.warning(f"No entries found for feed: {feed_config['name']}")
                continue

            latest = feed.entries[0]
            episode_url = latest.get("link") or latest.get("id", "")

            if episode_url in _seen_urls:
                logger.info(f"Already seen: {latest.get('title', 'unknown')}")
                continue

            title = latest.get("title", "Unknown episode")
            logger.info(f"Analyzing: {title} ({feed_config['name']})")

            transcript = get_transcript(episode_url)
            if not transcript:
                logger.warning(f"No transcript for: {title}")
                continue

            report = analyze_transcript(transcript, episode_url)

            # Extract numeric score from report for ranking
            score = _parse_score(report)
            results.append({
                "feed": feed_config["name"],
                "title": title,
                "url": episode_url,
                "score": score,
                "report": report,
            })

            _seen_urls.add(episode_url)

        except Exception as e:
            logger.error(f"Error processing feed {feed_config['name']}: {e}", exc_info=True)

    if not results:
        send_message(chat_id, "📭 Nothing new in your feeds today.")
        return

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Send top 3
    top = results[:3]
    send_message(chat_id, f"✅ Found {len(results)} new episode(s). Here are your top picks:\n")

    for i, result in enumerate(top, 1):
        header = f"*#{i} — {result['feed']}: {result['title']}*\n{result['url']}\n\n"
        send_message(chat_id, header + result["report"])

    if len(results) > 3:
        remainder = results[3:]
        skipped = "\n".join([f"• {r['feed']}: {r['title']} [{r['score']}%]" for r in remainder])
        send_message(chat_id, f"📋 *Also published today (below threshold):*\n{skipped}")


def _parse_score(report: str) -> int:
    """Extract the numeric score from a report string like '[Score: 78%]'."""
    import re
    match = re.search(r"\[Score:\s*(\d+)%\]", report)
    return int(match.group(1)) if match else 0