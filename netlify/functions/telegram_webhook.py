import os
import requests

def send_chat_action(chat_id, action="typing"):
    """
    Shows 'typing...' or 'uploading_document...' at the top of the chat.
    Valid actions: 'typing', 'upload_document', 'find_location', etc.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendChatAction"
    requests.post(url, json={"chat_id": chat_id, "action": action})

def handler(event, context):
    # ... previous parsing logic ...
    
    if "http" in text:
        # 1. Immediate acknowledgement
        send_telegram_message(chat_id, "🔍 TMI: Link received. Scoping for signal...")
        
        # 2. Show the loading state (Typing...)
        send_chat_action(chat_id, "typing")
        
        # 3. Process (This is where the delay happens)
        transcript = get_transcript(text)
        report = analyze_transcript(transcript)
        
        # 4. Send the final report
        send_telegram_message(chat_id, report)
    
    return {"statusCode": 200, "body": "OK"}
