import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subscribers.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_active INTEGER DEFAULT 1,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_reminded_at TIMESTAMP
            )
        """)
        conn.commit()

def add_subscriber(chat_id: int, username: str = None, first_name: str = None) -> bool:
    """Adds a new subscriber or reactivates an existing one. Returns True if newly subscribed/reactivated."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM subscribers WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        
        now = datetime.now().isoformat()
        if row is None:
            cursor.execute("""
                INSERT INTO subscribers (chat_id, username, first_name, is_active, subscribed_at)
                VALUES (?, ?, ?, 1, ?)
            """, (chat_id, username, first_name, now))
            conn.commit()
            return True
        else:
            was_inactive = (row["is_active"] == 0)
            cursor.execute("""
                UPDATE subscribers 
                SET is_active = 1, username = ?, first_name = ?
                WHERE chat_id = ?
            """, (username, first_name, chat_id))
            conn.commit()
            return was_inactive

def remove_subscriber(chat_id: int) -> bool:
    """Deactivates a subscriber. Returns True if subscriber was previously active."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM subscribers WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        if row and row["is_active"] == 1:
            cursor.execute("UPDATE subscribers SET is_active = 0 WHERE chat_id = ?", (chat_id,))
            conn.commit()
            return True
        return False

def get_active_subscribers():
    """Returns a list of dicts for all currently active subscribers."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, username, first_name, subscribed_at FROM subscribers WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]

def is_subscribed(chat_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM subscribers WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        return bool(row and row["is_active"] == 1)

def update_last_reminded(chat_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE subscribers SET last_reminded_at = ? WHERE chat_id = ?", 
                       (datetime.now().isoformat(), chat_id))
        conn.commit()
