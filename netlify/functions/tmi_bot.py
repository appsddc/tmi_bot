import json
import requests
import os

def handler(event, context):
    # 1. Grab the incoming message from Telegram
    body = json.loads(event.get("body", "{}"))
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    # 2. Setup your API Keys (Stored in Netlify Environment Variables)
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    # 3. Logic: If you send a link, the bot acknowledges it
    if "http" in text:
        reply = "🔍 TMI Signal Scout: Analyzing this link for macro-economic signal..."
    else:
        reply = "Hello! Send me a podcast link or type /summary to see your daily briefing."

    # 4. Send the message back to you
    url = f"https://api.telegram.org/bot8414359430:AAE7O3QN2DXSMtJe1EAGuP5E0e-0Wt9wacE/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": reply})

    return {
        "statusCode": 200,
        "body": json.dumps({"status": "ok"})
    }
