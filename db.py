"""Database initialization and setup."""

import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.getenv("DATABASE_PATH", "wellmind.db")


def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create sessions table (for chat sessions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            mood TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Create chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            mood TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_user_by_username(username):
    """Get user by username."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()


def get_user_by_id(user_id):
    """Get user by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()


def create_user(username, email, password_hash):
    """Create a new user."""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None


def get_user_sessions(user_id, limit=10):
    """Get user's chat sessions."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, created_at, mood FROM sessions 
               WHERE user_id = ? ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit)
        )
        return cursor.fetchall()


def create_session(user_id):
    """Create a new chat session."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return cursor.lastrowid


def get_session_messages(session_id):
    """Get all messages in a session."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT user_message, ai_response, mood, created_at 
               FROM chat_history WHERE session_id = ? ORDER BY created_at""",
            (session_id,)
        )
        return cursor.fetchall()


def save_chat_message(user_id, session_id, user_message, ai_response, mood):
    """Save a chat message to history."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO chat_history 
               (user_id, session_id, user_message, ai_response, mood) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, session_id, user_message, ai_response, mood)
        )
        conn.commit()
        return cursor.lastrowid


def update_session_mood(session_id, mood):
    """Update session mood."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sessions SET mood = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (mood, session_id)
        )
        conn.commit()
