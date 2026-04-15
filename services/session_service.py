"""Session management for chat sessions."""

import time
from db import create_session, get_session_messages, save_chat_message, get_user_sessions


class ChatSession:
    """Manage a chat session for a user."""
    
    def __init__(self, session_id):
        """Initialize session."""
        self.session_id = session_id
        self.start_time = time.time()
        self.message_count = 0
        self.mood_tracker = {}
    
    def add_message(self, mood):
        """Track a new message."""
        self.message_count += 1
        if mood not in self.mood_tracker:
            self.mood_tracker[mood] = 0
        self.mood_tracker[mood] += 1
    
    def get_stats(self):
        """Get session statistics."""
        duration = int(time.time() - self.start_time)
        
        dominant_mood = "Neutral"
        if self.mood_tracker:
            dominant_mood = max(self.mood_tracker, key=self.mood_tracker.get)
        
        return {
            "session_id": self.session_id,
            "message_count": self.message_count,
            "duration_sec": duration,
            "dominant_mood": dominant_mood,
            "mood_breakdown": self.mood_tracker
        }
    
    def get_duration_minutes(self):
        """Get session duration in minutes."""
        return int((time.time() - self.start_time) / 60)


def get_or_create_session(user_id):
    """Get or create a session for user."""
    session_id = create_session(user_id)
    return ChatSession(session_id)


def get_user_chat_history(user_id, session_id=None, limit=50):
    """Get user's chat history."""
    if session_id:
        messages = get_session_messages(session_id)
        return {
            "session_id": session_id,
            "messages": [dict(msg) for msg in messages]
        }
    else:
        # Get recent sessions
        sessions = get_user_sessions(user_id, limit=10)
        return {
            "sessions": [dict(s) for s in sessions]
        }
