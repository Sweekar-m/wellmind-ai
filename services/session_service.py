"""Session management for chat sessions."""

import time
from datetime import datetime, timedelta
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

def get_active_or_new_session(user_id, timeout_hours=12):
    """Get the most recent session if it's active, otherwise create new."""
    recent_sessions = get_user_sessions(user_id, limit=1)
    
    if recent_sessions:
        latest = recent_sessions[0]
        updated_at = latest['updated_at']
        
        # Ensure it's a datetime object
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            except:
                updated_at = datetime.now()
                
        # Strip timezone for safe subtraction
        if updated_at.tzinfo is not None:
            updated_at = updated_at.replace(tzinfo=None)
            
        if datetime.now() - updated_at < timedelta(hours=timeout_hours):
            return latest['id'], False  # Not new
            
    # Create new session if no recent active session
    session_id = create_session(user_id)
    return session_id, True

