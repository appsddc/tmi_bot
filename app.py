import os
import json
import logging
from flask import Flask, request, jsonify
from tmi_logic.telegram import send_message, send_chat_action
from tmi_logic.scraper import get_transcript
from tmi_logic.sieve import analyze_transcript
from tmi_logic.briefing import run_daily_briefing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "TMI Signal Scout is running.", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """Receives all incoming Telegram messages."""
    try:
        body = request.get_json(silent=True) or {}
        message = body.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()

        if not chat_id or not text:
            return jsonify({"status": "ignored"}), 200

        logger.info(f"Received message from {chat_id}: {text[:80]}")

        if text.startswith("/start"):
            send_message(chat_id, (
                "👋 Welcome to TMI — Too Much Information.\n\n"
                "Send me any podcast or YouTube link and I'll scan it for signal.\n\n"
                "Commands:\n"
                "/summary — Run your daily briefing now\n"
                "/help — Show this message"
            ))

        elif text.startswith("/summary"):
            send_message(chat_id, "📡 Running your daily briefing now...")
            run_daily_briefing(chat_id)

        elif text.startswith("/help"):
            send_message(chat_id, (
                "Send me any YouTube or podcast link and I'll return:\n\n"
                "🟢 High-value segments with timestamps\n"
                "💡 Why it's relevant to your profile\n"
                "🔴 What to skip\n\n"
                "Or use /summary for your daily ranked briefing."
            ))

        elif "http" in text:
            # Extract URL from message (handles URLs mid-sentence)
            url = next((word for word in text.split() if word.startswith("http")), None)

            if url:
                send_message(chat_id, "🔍 Link received. Scoping for signal...")
                send_chat_action(chat_id, "typing")

                transcript = get_transcript(url)

                if not transcript:
                    send_message(chat_id, "❌ Couldn't get a transcript for that link. Try a YouTube video or a podcast with captions.")
                    return jsonify({"status": "ok"}), 200

                report = analyze_transcript(transcript, url)
                send_message(chat_id, report)
            else:
                send_message(chat_id, "Couldn't find a valid URL in your message. Try again?")

        else:
            send_message(chat_id, "Send me a podcast or YouTube link to analyse, or /summary for your daily briefing.")

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)

    # Always return 200 to Telegram or it will keep retrying
    return jsonify({"status": "ok"}), 200


@app.route("/run-briefing", methods=["GET"])
def run_briefing():
    """
    Called by Render's cron job daily.
    Sends the daily briefing to the owner's chat.
    """
    chat_id = os.environ.get("MY_CHAT_ID")
    if not chat_id:
        logger.error("MY_CHAT_ID not set in environment variables.")
        return jsonify({"error": "MY_CHAT_ID not configured"}), 500

    try:
        run_daily_briefing(chat_id)
        return jsonify({"status": "briefing sent"}), 200
    except Exception as e:
        logger.error(f"Briefing error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)