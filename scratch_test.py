import os
from db import create_user, create_session, save_chat_message, get_user_sessions, update_session_title
from services.memory_service import get_memory_service

# Create dummy user if not exists
user_id = create_user("testuser2", "test2@example.com", "password")
if not user_id:
    # Get existing user
    from db import get_db
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username='testuser2'")
            user_id = cur.fetchone()[0]

# Create session
session_id = create_session(user_id)

mem = get_memory_service()
context = mem.get_context(user_id, session_id, "hello", top_k=5)

is_first_message = (context == "")
title = "No title"
if is_first_message:
    user_message = "This is a really long test message that should be truncated by thirty characters."
    title = user_message[:30] + ("..." if len(user_message) > 30 else "")
    update_session_title(session_id, title)
    save_chat_message(user_id, session_id, user_message, "Hi back!", "Neutral")

# Fetch to see title
sessions = get_user_sessions(user_id, limit=1)
s = dict(sessions[0])
print(s)
