"""
Windows Desktop Water Intake Notifier
------------------------------------
Runs in the background on Windows.
Sends a native toast notification and plays a refreshing water chime
every 1 hour (or custom interval) while your laptop is powered on.
"""

import os
import sys
import time
import random
import argparse
import subprocess
import winsound
from datetime import datetime

# Configure Windows console output for UTF-8 and emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Path to the water droplet chime
SOUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "water_drop.wav")

HYDRATION_MESSAGES = [
    ("💧 Hydration Break!", "Time to drink a fresh glass of water. Stay sharp and refreshed!"),
    ("🌊 Water Check!", "Grab a sip! Keeping hydrated boosts your focus and energy."),
    ("🥤 Drink Up!", "Your body needs water to stay at peak performance. Take a glass now!"),
    ("✨ Stay Hydrated!", "A quick pause for a sip of cool water. Keep going strong!"),
    ("💧 Refresh & Recharge!", "Drink some water and give your eyes a quick 20-second rest.")
]

def show_toast(title: str, message: str, sound_path: str = SOUND_PATH):
    """Triggers native Windows Toast notification and plays the custom water chime."""
    # Play sound asynchronously
    if sound_path and os.path.exists(sound_path):
        try:
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Sound error: {e}")

    # Display Windows Toast notification
    ps_code = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $text = $template.GetElementsByTagName("text")
    $text[0].AppendChild($template.CreateTextNode("{title}")) | Out-Null
    $text[1].AppendChild($template.CreateTextNode("{message}")) | Out-Null
    $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("WaterReminder")
    $notifier.Show($toast)
    """

    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_code],
            capture_output=True,
            text=True,
            check=False
        )
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Toast error: {e}")

def run_notifier(interval_seconds: int = 3600, notify_on_start: bool = True):
    """Main loop: runs continuously, notifying every interval_seconds."""
    print("=" * 55)
    print(" 💧 Windows Desktop Water Intake Notifier")
    print(f" ⏱  Reminder Interval: every {interval_seconds // 60} minute(s) ({interval_seconds}s)")
    print(f" 🔊 Sound: {SOUND_PATH}")
    print(" 💻 Runs continuously while your PC is powered on.")
    print(" Press Ctrl+C anytime to stop.")
    print("=" * 55)

    if notify_on_start:
        title, msg = random.choice(HYDRATION_MESSAGES)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Launch notification sent: {title}")
        show_toast(title, msg)

    try:
        while True:
            time.sleep(interval_seconds)
            title, msg = random.choice(HYDRATION_MESSAGES)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sent reminder: {title} - {msg}")
            show_toast(title, msg)
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Desktop Notifier stopped by user. Stay hydrated!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Windows Desktop Water Reminder Notifier")
    parser.add_argument("--interval", type=int, default=3600, help="Reminder interval in seconds (default: 3600 = 1 hour)")
    parser.add_argument("--test", action="store_true", help="Send an immediate test notification and exit")
    parser.add_argument("--no-initial", action="store_true", help="Do not send a notification immediately upon launch")
    args = parser.parse_args()

    if args.test:
        title, msg = random.choice(HYDRATION_MESSAGES)
        print(f"Sending test notification: {title} - {msg}")
        show_toast(title, msg)
        print("Done!")
        sys.exit(0)

    run_notifier(interval_seconds=args.interval, notify_on_start=not args.no_initial)
