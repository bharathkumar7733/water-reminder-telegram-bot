# 💧 AquaAlert: Hybrid Water Intake Reminder

> A dual-channel hydration reminder platform featuring a **24/7 Cloud Telegram Bot** for mobile notifications and a **Local Windows Desktop Notifier** with custom water chime audio.

[![Telegram Bot](https://img.shields.io/badge/Telegram-@Bharath__water__remainderbot-blue?style=for-the-badge&logo=telegram)](https://t.me/Bharath_water_remainderbot)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![Deploy on Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render)](https://render.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Cloud-lightgrey?style=for-the-badge)]()

---

## 🌟 Highlights

* **📱 24/7 Cloud Telegram Bot**: Anyone can start receiving reminders on their phone by simply tapping `/start`.
* **⏰ Smart Active Hours**: Scheduled to alert every 1 hour between **10:00 AM and 9:00 PM** daily (silent at night so sleep is never disturbed).
* **🛑 Frictionless Control**: Use `/stop` anytime to pause reminders, or `/start` to resume.
* **💻 Windows Desktop Notifier**: For laptop users who want native screen toasts every 1 hour while their PC is powered on.
* **🔊 Custom Refreshing Audio**: Plays a gentle, crisp water droplet chime instead of jarring system beeps.
* **⚡ 100% Free**: No SMS costs, no trial credits, and no monthly phone rentals.

---

## 📱 Option 1: Use the Telegram Bot (Instant & Mobile)

If you just want hydration reminders delivered straight to your phone or Telegram app:

1. Open Telegram and search for **[@Bharath_water_remainderbot](https://t.me/Bharath_water_remainderbot)**.
2. Click **Start** or send the message:
   ```text
   /start
   ```
3. That's it! You are now subscribed to automated reminders between **10:00 AM and 9:00 PM**.

### Bot Commands
| Command | Description |
| :--- | :--- |
| `/start` | Subscribe to daily water intake reminders |
| `/stop` | Pause / unsubscribe from reminders |
| `/status` | View your subscription status and active reminder window |
| `/remindme` | Trigger an instant test hydration reminder |
| `/help` | Display command instructions |

---

## 💻 Option 2: Windows Desktop Notifier (For Your Laptop)

If you want native Windows desktop banner notifications with custom water sound while working on your laptop:

### Quick Setup

1. **Clone or Download this repository:**
   ```bash
   git clone https://github.com/bharathkumar7733/water-reminder-telegram-bot.git
   cd water-reminder-telegram-bot
   ```

2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the notification:**
   ```bash
   python desktop_notifier.py --test
   ```
   *(You will see a toast notification in the corner of your screen and hear the water droplet chime!)*

### Running in the Background & Auto-Start with Windows

We have included automated batch scripts so you don't have to keep a terminal window open:

* **▶️ Run in Background:**  
  Double-click `run_desktop_notifier.bat`.  
  *It launches silently via `pythonw` with no command prompt window.*

* **🚀 Launch Automatically on Windows Startup:**  
  Double-click `add_to_startup.bat`.  
  *This automatically creates a shortcut in your Windows Startup folder. Whenever you power on your laptop, the notifier starts running automatically every 1 hour!*

* **⏹️ Stop Background Process:**  
  Double-click `stop_desktop_notifier.bat`.

---

## 🏗️ Project Architecture

```
water_reminder/
├── bot.py                     # Cloud Telegram Bot (long-polling + daily scheduler)
├── database.py                # Persistent SQLite database for subscriber tracking
├── desktop_notifier.py        # Local Windows Desktop Notifier (1-hour loop + toast + audio)
├── assets/
│   └── water_drop.wav         # Custom acoustic water droplet audio chime
├── run_desktop_notifier.bat   # Silent background launcher
├── add_to_startup.bat         # 1-click Windows startup installer
├── stop_desktop_notifier.bat  # 1-click background process stopper
├── requirements.txt           # Minimal Python dependencies
├── Procfile                   # Cloud background worker specification for Render
├── .env.example               # Configuration template
├── .gitignore                 # Standard Python & secrets ignore rules
└── README.md                  # Complete documentation & usage guide
```

---

## ☁️ Deploying the Telegram Bot to Render (24/7 Free)

To keep the Telegram bot running 24/7 without needing your laptop powered on:

1. **Push this repository to your GitHub.**
2. Go to **[Render.com](https://render.com)** and create a **New Background Worker**.
3. Link your GitHub repository.
4. Set the following settings:
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `python bot.py`
5. Under **Environment Variables**, add:
   * `TELEGRAM_BOT_TOKEN` = `your_telegram_bot_token`
   * `BOT_USERNAME` = `Bharath_water_remainderbot`
   * `TIMEZONE_OFFSET_HOURS` = `5.5` *(for IST, or your local offset)*
6. Click **Create Background Worker**.

Your bot is now live 24/7 in the cloud! 🚀

---

## 📜 License & Author

Developed by **[Bharath Kumar](https://github.com/bharathkumar7733)**.  
Feel free to star ⭐ the repository and stay hydrated! 💧
