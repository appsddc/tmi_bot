import os
import requests
import logging

logger = logging.getLogger(__name__)

def _token():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")
    return token

def send_message(chat_id, text):
    """Send a text message to a Telegram chat."""
    url = f"https://api.telegram.org/bot{_token()}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")

def send_chat_action(chat_id, action="typing"):
    """
    Show a status indicator in the chat.
    Valid actions: typing, upload_document, find_location, etc.
    """
    url = f"https://api.telegram.org/bot{_token()}/sendChatAction"
    try:
        requests.post(url, json={"chat_id": chat_id, "action": action}, timeout=10)
    except requests.RequestException as e:
        logger.error(f"Failed to send chat action: {e}")

def set_webhook(webhook_url):
    """Register your Render URL as the Telegram webhook. Run once after deploy."""
    url = f"https://api.telegram.org/bot{_token()}/setWebhook"
    resp = requests.post(url, json={"url": webhook_url})
    return resp.json()