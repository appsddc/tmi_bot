import feedparser
from tmi_logic.scraper import get_transcript
from tmi_logic.sieve import analyze_transcript

# Add your high-signal RSS feeds here
FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCASM0cgfkJxQ1ICmRilfHLw", # Patrick Boyle
    "https://feeds.megaphone.fm/the-david-mcwilliams-podcast" # McWilliams
]

def handler(event, context):
    for url in FEEDS:
        feed = feedparser.parse(url)
        # Just check the latest entry
        latest_entry = feed.entries[0]
        
        print(f"Checking: {latest_entry.title}")
        
        # You'd add logic here to check a 'Database/Blob' to see if you've read this already
        transcript = get_transcript(latest_entry.link)
        report = analyze_transcript(transcript)
        
        # If score is > 70%, send to your chat_id
        # (You'll need to hardcode your CHAT_ID in env variables for the daily scout)
        # send_telegram_message(os.environ.get("MY_CHAT_ID"), report)

    return {"statusCode": 200, "body": "Briefing complete."}
