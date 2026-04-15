"""Database initialization and setup using PostgreSQL."""

import psycopg2
from psycopg2.extras import DictCursor
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def init_db():
    """Initialize the database with required tables."""
    if not DATABASE_URL:
        print("Warning: DATABASE_URL not set. Skipping DB init.")
        return
        
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create chat_sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            mood TEXT
        )
    """)
    
    # Safely migrate existing table
    try:
        cursor.execute("ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS title TEXT;")
    except Exception as e:
        print(f"Migration error: {e}")
    
    
    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            mood TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()


@contextmanager
def get_db():
    """Get a database connection."""
    conn = psycopg2.connect(DATABASE_URL)
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
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            return cursor.fetchone()


def get_user_by_id(user_id):
    """Get user by ID."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()


def create_user(username, email, password_hash):
    """Create a new user."""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
                    (username, email, password_hash)
                )
                return cursor.fetchone()[0]
    except psycopg2.IntegrityError:
        return None


def get_user_sessions(user_id, limit=10):
    """Get user's chat sessions."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                """SELECT id, title, created_at, updated_at, mood FROM chat_sessions 
                   WHERE user_id = %s ORDER BY created_at DESC LIMIT %s""",
                (user_id, limit)
            )
            return cursor.fetchall()


def create_session(user_id):
    """Create a new chat session."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO chat_sessions (user_id) VALUES (%s) RETURNING id", (user_id,))
            return cursor.fetchone()[0]


def get_session_messages(session_id):
    """Get all messages in a session."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                """SELECT user_message, ai_response, mood, created_at 
                   FROM messages WHERE session_id = %s ORDER BY created_at""",
                (session_id,)
            )
            return cursor.fetchall()


def save_chat_message(user_id, session_id, user_message, ai_response, mood):
    """Save a chat message to history."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO messages 
                   (user_id, session_id, user_message, ai_response, mood) 
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (user_id, session_id, user_message, ai_response, mood)
            )
            return cursor.fetchone()[0]


def update_session_mood(session_id, mood):
    """Update session mood."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE chat_sessions SET mood = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (mood, session_id)
            )

def update_session_title(session_id, title):
    """Update session title natively."""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE chat_sessions SET title = %s WHERE id = %s",
                (title, session_id)
            )
