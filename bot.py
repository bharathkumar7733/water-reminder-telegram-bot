"""
Telegram Water Reminder Cloud Bot
---------------------------------
Runs 24/7 (deployable on Render or local).
- Manages user subscriptions via /start and /stop.
- Reminds active subscribers to drink water every 1 hour
  between 10:00 AM and 9:00 PM (10:00 to 21:00) daily.
"""

import os
import sys
import time
import random
import logging
import threading
from datetime import datetime, timezone, timedelta
import requests
from dotenv import load_dotenv

import database

# Configure stdout for UTF-8 support
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("WaterReminderBot")

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not found in environment variables or .env!")
    sys.exit(1)

BOT_USERNAME = os.getenv("BOT_USERNAME", "Bharath_water_remainderbot")
REMINDER_INTERVAL_MINUTES = int(os.getenv("REMINDER_INTERVAL_MINUTES", "60"))
START_HOUR = int(os.getenv("START_HOUR", "10"))   # 10:00 AM
END_HOUR = int(os.getenv("END_HOUR", "21"))       # 9:00 PM (21:00)
TZ_OFFSET = float(os.getenv("TIMEZONE_OFFSET_HOURS", "5.5"))  # Default IST (+5:30)

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

REMINDER_MESSAGES = [
    "💧 *Hydration Time!* Take a break and drink a glass of water. Stay sharp and refreshed!",
    "🌊 *Water Check!* Drink a glass of water right now to keep your energy and focus high.",
    "🥤 *Stay Hydrated!* Your body performs best with plenty of water. Take a sip!",
    "✨ *Hydration Break!* Grab a fresh glass of water. Your body and mind will thank you!",
    "💧 *Drink Up!* Remember to hydrate regularly. Take a quick stretch and drink a glass.",
    "🌿 *Refresh Yourself!* Drink a cup of water and give your eyes a quick 20-second break."
]

def get_current_time_in_tz():
    """Returns the current datetime in the configured timezone."""
    hours = int(TZ_OFFSET)
    minutes = int((abs(TZ_OFFSET) - abs(hours)) * 60)
    sign = 1 if TZ_OFFSET >= 0 else -1
    tz = timezone(timedelta(hours=hours, minutes=sign * minutes))
    return datetime.now(tz)

def send_telegram_message(chat_id: int, text: str, parse_mode: str = "Markdown") -> bool:
    """Sends a message via Telegram Bot API. Returns True if successful."""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if not data.get("ok"):
            err_code = data.get("error_code")
            desc = data.get("description", "")
            logger.warning(f"Failed to send message to {chat_id}: {err_code} - {desc}")
            # If user blocked bot, deactivate in database
            if err_code in [403, 400] and ("blocked" in desc.lower() or "not found" in desc.lower()):
                database.remove_subscriber(chat_id)
                logger.info(f"Unsubscribed inactive/blocked chat_id {chat_id}")
            return False
        return True
    except Exception as e:
        logger.error(f"Network error sending message to {chat_id}: {e}")
        return False

def handle_start(chat_id: int, username: str, first_name: str):
    database.add_subscriber(chat_id, username, first_name)
    name = first_name or "there"
    welcome_text = (
        f"👋 *Hello {name}! Welcome to the Daily Water Intake Reminder.*\n\n"
        f"💧 *You are now subscribed to automated reminders!*\n\n"
        f"⏰ *Reminder Schedule:*\n"
        f"• *Active Hours:* Daily from *{START_HOUR}:00 AM* to *{END_HOUR - 12}:00 PM* (10 AM – 9 PM)\n"
        f"• *Frequency:* Every {REMINDER_INTERVAL_MINUTES} minutes\n\n"
        f"🛑 *Commands:*\n"
        f"• `/stop` — Stop receiving reminders anytime\n"
        f"• `/status` — Check your subscription status\n"
        f"• `/remindme` — Trigger an instant water reminder\n\n"
        f"💻 *Want Windows desktop notifications on your laptop too?*\n"
        f"Download the desktop notifier from our repository to get 1-hour toast alerts with custom water sound while working on your PC!\n\n"
        f"_Stay hydrated and stay healthy!_ 🌊"
    )
    send_telegram_message(chat_id, welcome_text)
    logger.info(f"Subscribed user: {chat_id} (@{username})")

def handle_stop(chat_id: int):
    was_active = database.remove_subscriber(chat_id)
    if was_active:
        stop_text = (
            "🛑 *Water reminders have been paused.*\n\n"
            "You will not receive any more scheduled notifications.\n\n"
            "Send `/start` anytime if you'd like to resume reminders! 💧"
        )
    else:
        stop_text = (
            "ℹ️ You are not currently subscribed to reminders.\n\n"
            "Send `/start` if you want to start receiving hydration alerts! 💧"
        )
    send_telegram_message(chat_id, stop_text)
    logger.info(f"Unsubscribed user: {chat_id}")

def handle_status(chat_id: int):
    active = database.is_subscribed(chat_id)
    now = get_current_time_in_tz()
    current_time_str = now.strftime("%I:%M %p")
    is_in_window = START_HOUR <= now.hour < END_HOUR
    window_status = "🟢 Currently Active" if is_in_window else "🌙 Silent Hours (10:00 PM – 9:59 AM)"

    status_text = (
        f"📊 *Water Reminder Status*\n\n"
        f"• *Subscription:* {'✅ Subscribed' if active else '❌ Inactive'}\n"
        f"• *Current Time:* {current_time_str}\n"
        f"• *Reminder Window:* {START_HOUR}:00 AM – {END_HOUR - 12}:00 PM daily\n"
        f"• *Window State:* {window_status}\n\n"
        f"{'Send /stop to cancel' if active else 'Send /start to subscribe'}."
    )
    send_telegram_message(chat_id, status_text)

def handle_remindme(chat_id: int):
    msg = random.choice(REMINDER_MESSAGES)
    send_telegram_message(chat_id, msg)
    database.update_last_reminded(chat_id)

def handle_help(chat_id: int):
    help_text = (
        "🤖 *Water Reminder Bot Help*\n\n"
        "Available commands:\n"
        "• `/start` — Subscribe to daily hydration reminders\n"
        "• `/stop` — Stop daily hydration reminders\n"
        "• `/status` — View your current subscription status\n"
        "• `/remindme` — Trigger an immediate water reminder\n"
        "• `/help` — Show this message"
    )
    send_telegram_message(chat_id, help_text)

def process_update(update: dict):
    message = update.get("message")
    if not message:
        return
    text = (message.get("text") or "").strip()
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    user = message.get("from") or {}
    username = user.get("username")
    first_name = user.get("first_name", "")

    if not chat_id or not text:
        return

    cmd = text.split()[0].lower()
    # Normalize command if it contains @botname
    if "@" in cmd:
        cmd = cmd.split("@")[0]

    logger.info(f"Received command '{cmd}' from chat_id {chat_id} ({first_name})")

    if cmd == "/start":
        handle_start(chat_id, username, first_name)
    elif cmd == "/stop":
        handle_stop(chat_id)
    elif cmd == "/status":
        handle_status(chat_id)
    elif cmd == "/remindme":
        handle_remindme(chat_id)
    elif cmd in ["/help", "help"]:
        handle_help(chat_id)
    else:
        reply = "I didn't recognize that command. Try `/start`, `/stop`, `/status`, or `/remindme`! 💧"
        send_telegram_message(chat_id, reply)

def reminder_scheduler_loop():
    """Background thread that sends reminders during 10:00 AM to 9:00 PM."""
    logger.info("Scheduler thread started. Active window: 10:00 AM - 9:00 PM.")
    while True:
        try:
            now = get_current_time_in_tz()
            # Check if within active hours (10:00 to 20:59)
            if START_HOUR <= now.hour < END_HOUR:
                # Check at the top of the hour (minute == 0)
                # Or every interval minutes
                if now.minute == 0:
                    subscribers = database.get_active_subscribers()
                    if subscribers:
                        msg = random.choice(REMINDER_MESSAGES)
                        logger.info(f"Firing scheduled reminder to {len(subscribers)} subscriber(s).")
                        for sub in subscribers:
                            send_telegram_message(sub["chat_id"], msg)
                            database.update_last_reminded(sub["chat_id"])
                            time.sleep(0.05)  # Telegram rate-limit cushion
                    # Sleep 60 seconds to avoid repeating in the same minute
                    time.sleep(60)
            time.sleep(30)
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
            time.sleep(30)

def poll_updates():
    """Polls Telegram for updates."""
    offset = 0
    logger.info(f"Bot @{BOT_USERNAME} is running and polling for updates...")
    while True:
        try:
            url = f"{BASE_URL}/getUpdates?offset={offset}&timeout=25"
            resp = requests.get(url, timeout=30)
            data = resp.json()
            if data.get("ok"):
                updates = data.get("result", [])
                for update in updates:
                    offset = update["update_id"] + 1
                    process_update(update)
            else:
                logger.warning(f"getUpdates returned non-ok: {data}")
                time.sleep(2)
        except requests.exceptions.RequestException as e:
            logger.error(f"Polling network error: {e}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error in polling: {e}")
            time.sleep(3)

from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"AquaAlert Telegram Bot is running live 24/7!")

    def log_message(self, format, *args):
        # Silence access logs to keep terminal clean
        return

def run_health_server():
    port = int(os.getenv("PORT", "10000"))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        logger.info(f"Render Web Service health check listening on port {port} (Free Tier compatible).")
        server.serve_forever()
    except Exception as e:
        logger.warning(f"Could not start health check HTTP server on port {port}: {e}")

def main():
    database.init_db()
    
    # Start health check server for Render Web Service (Free Tier)
    http_thread = threading.Thread(target=run_health_server, daemon=True)
    http_thread.start()

    # Start scheduler daemon thread
    scheduler_thread = threading.Thread(target=reminder_scheduler_loop, daemon=True)
    scheduler_thread.start()

    # Run bot polling on main thread
    poll_updates()

if __name__ == "__main__":
    main()
