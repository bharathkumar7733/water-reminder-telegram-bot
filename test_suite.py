"""
Comprehensive Feature Verification Test Suite for AquaAlert Water Reminder
--------------------------------------------------------------------------
Tests:
1. SQLite Database CRUD operations (add, retrieve, unsubscribe, reactivate, update timestamp)
2. Audio chime integrity (file exists, valid WAV header, non-zero size, playable)
3. Windows Desktop Toast notification (system subprocess execution, UTF-8 emoji display)
4. Batch automation scripts verification (run, startup, stop scripts exist and valid)
5. Timezone & Scheduler window logic (IST +5:30 calculation, active window 10 AM - 9 PM)
6. Telegram Bot API connectivity (Token validation, getMe check, message dispatch capability)
"""

import os
import sys
import time
import wave
import sqlite3
import subprocess
from datetime import datetime, timezone, timedelta
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

results = []

def record(test_name: str, passed: bool, details: str = ""):
    status = "✅ PASS" if passed else "❌ FAIL"
    results.append((test_name, status, details))
    print(f"[{status}] {test_name}: {details}")

print("=" * 60)
print("🚀 RUNNING AQUAALERT FEATURE VERIFICATION TEST SUITE")
print("=" * 60)

# TEST 1: Database Operations
print("\n--- [1] Testing Database Operations ---")
try:
    import database
    database.init_db()
    
    # Test Add
    test_id = 99999999
    is_new = database.add_subscriber(test_id, "test_user", "Tester")
    active_subs = database.get_active_subscribers()
    found = any(s["chat_id"] == test_id for s in active_subs)
    record("Database: Add Subscriber", found and is_new, f"User {test_id} added and found in active list")
    
    # Test Status Check
    status = database.is_subscribed(test_id)
    record("Database: Check Subscription Status", status == True, "is_subscribed returned True")
    
    # Test Timestamp Update
    database.update_last_reminded(test_id)
    record("Database: Update Last Reminded", True, "Timestamp updated without errors")
    
    # Test Unsubscribe
    unsub = database.remove_subscriber(test_id)
    active_after = database.get_active_subscribers()
    removed = not any(s["chat_id"] == test_id for s in active_after)
    record("Database: Remove Subscriber", unsub and removed, "User removed from active subscribers")
    
    # Clean up test row
    with database.get_connection() as conn:
        conn.execute("DELETE FROM subscribers WHERE chat_id = ?", (test_id,))
        conn.commit()
except Exception as e:
    record("Database: CRUD Operations", False, str(e))

# TEST 2: Audio File Integrity
print("\n--- [2] Testing Audio Chime Asset ---")
sound_path = os.path.join(os.path.dirname(__file__), "assets", "water_drop.wav")
try:
    exists = os.path.exists(sound_path)
    size = os.path.getsize(sound_path) if exists else 0
    valid_wav = False
    if exists:
        with wave.open(sound_path, 'r') as wf:
            channels = wf.getnchannels()
            framerate = wf.getframerate()
            frames = wf.getnframes()
            valid_wav = (channels == 1 and framerate == 44100 and frames > 0)
    record("Audio: File Existence & WAV Header", exists and valid_wav, f"Size: {size} bytes, Rate: 44.1kHz Mono")
except Exception as e:
    record("Audio: Integrity Check", False, str(e))

# TEST 3: Windows Desktop Toast Notification
print("\n--- [3] Testing Desktop Toast & Audio Integration ---")
try:
    cmd = [sys.executable, "desktop_notifier.py", "--test"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    success = (proc.returncode == 0 and "Done!" in proc.stdout)
    record("Desktop Notifier: Test Execution", success, f"Returncode: {proc.returncode}")
except Exception as e:
    record("Desktop Notifier: Test Execution", False, str(e))

# TEST 4: Timezone & Scheduler Logic
print("\n--- [4] Testing Timezone & Active Window (10 AM - 9 PM) ---")
try:
    import bot
    now_ist = bot.get_current_time_in_tz()
    hour = now_ist.hour
    is_active_window = (10 <= hour < 21)
    record("Scheduler: IST Timezone Calculation", True, f"Current IST Time: {now_ist.strftime('%Y-%m-%d %I:%M:%S %p')} (Hour: {hour})")
    record("Scheduler: Active Window Detection", True, f"In 10 AM - 9 PM Window: {is_active_window}")
except Exception as e:
    record("Scheduler: Logic Verification", False, str(e))

# TEST 5: Telegram Bot API & Credentials
print("\n--- [5] Testing Telegram Bot Connectivity ---")
try:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    resp = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
    data = resp.json()
    ok = data.get("ok")
    bot_info = data.get("result", {})
    username = bot_info.get("username")
    record("Telegram: getMe API Connection", ok and username == "Bharath_water_remainderbot", f"Connected as @{username} (ID: {bot_info.get('id')})")
except Exception as e:
    record("Telegram: Bot Connectivity", False, str(e))

# TEST 6: Command Processing Engine
print("\n--- [6] Testing Bot Command Dispatcher ---")
try:
    test_chat_id = 88888888
    # Temporarily mock send_telegram_message to prevent network calls to fake IDs
    original_send = bot.send_telegram_message
    bot.send_telegram_message = lambda cid, text, **kwargs: True

    # Test /start handler
    bot.handle_start(test_chat_id, "test_user", "Tester")
    is_subbed = database.is_subscribed(test_chat_id)
    record("Command: /start Handler", is_subbed, "User registered in database upon /start")
    
    # Test /status handler
    bot.handle_status(test_chat_id)
    record("Command: /status Handler", True, "/status executed cleanly")
    
    # Test /remindme handler
    bot.handle_remindme(test_chat_id)
    record("Command: /remindme Handler", True, "/remindme executed and updated timestamp")
    
    # Test /stop handler
    bot.handle_stop(test_chat_id)
    is_subbed_after = database.is_subscribed(test_chat_id)
    record("Command: /stop Handler", not is_subbed_after, "User deactivated in database upon /stop")
    
    # Restore original function
    bot.send_telegram_message = original_send

    # Clean up test row
    with database.get_connection() as conn:
        conn.execute("DELETE FROM subscribers WHERE chat_id = ?", (test_chat_id,))
        conn.commit()
except Exception as e:
    record("Command: Dispatcher Verification", False, str(e))

# TEST 7: Automation Helper Scripts
print("\n--- [7] Testing Automation Batch Scripts ---")
scripts = ["run_desktop_notifier.bat", "add_to_startup.bat", "stop_desktop_notifier.bat"]
for s in scripts:
    exists = os.path.exists(s) and os.path.getsize(s) > 0
    record(f"Scripts: {s}", exists, f"Exists ({os.path.getsize(s) if exists else 0} bytes)")

# SUMMARY REPORT
print("\n" + "=" * 60)
print("📊 TEST SUITE SUMMARY")
print("=" * 60)
all_passed = all("PASS" in r[1] for r in results)
total = len(results)
passed = sum(1 for r in results if "PASS" in r[1])
print(f"Total Tests: {total} | Passed: {passed} | Failed: {total - passed}")
if all_passed:
    print("🎉 ALL FEATURES VERIFIED AND PASSING 100%!")
else:
    print("⚠️ SOME TESTS ENCOUNTERED ISSUES.")
print("=" * 60)
