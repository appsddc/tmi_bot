import os
# This line fixes the Metaclass/Protobuf error in Python 3.14
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from dotenv import load_dotenv
from tmi_logic.scraper import get_transcript
from tmi_logic.sieve import analyze_transcript

load_dotenv()

def test():
    # Example: A technical podcast link
    url = "https://www.youtube.com/watch?v=MloKMQx6slo"
    
    print("🔍 Step 1: Scraping (Instance Method)...")
    text = get_transcript(url)
    
    if "Scraper failed" in text:
        print(text)
        return

    print("🧠 Step 2: Sieve Analysis (GenAI SDK)...")
    report = analyze_transcript(text)
    print("\n--- SIGNAL SCOUT REPORT ---")
    print(report)

if __name__ == "__main__":
    test()
