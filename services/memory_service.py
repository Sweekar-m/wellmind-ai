"""Memory service using PostgreSQL for recent chat context."""

from db import get_db
from psycopg2.extras import DictCursor

class MemoryService:
    """Manage user memory using recent chat history from PostgreSQL."""
    
    def get_context(self, user_id, session_id, current_message, top_k=5):
        """Retrieve recent past interactions as context for the active session."""
        try:
            with get_db() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    # Fetch the last 'top_k' messages for this specific session
                    cursor.execute(
                        """
                        SELECT user_message, ai_response, mood, created_at 
                        FROM messages 
                        WHERE user_id = %s AND session_id = %s
                        ORDER BY created_at DESC 
                        LIMIT %s
                        """,
                        (user_id, session_id, top_k)
                    )
                    results = cursor.fetchall()
            
            if not results:
                return ""
            
            # Since we ordered DESC, reverse the results to show chronological order
            results.reverse()
            
            context_lines = []
            for row in results:
                mood = row.get("mood", "unknown")
                msg = row.get("user_message", "")
                resp = row.get("ai_response", "")
                context_lines.append(f"[Past - Mood: {mood}]\nUser: {msg}\nAssistant: {resp}")
            
            return "\n\n".join(context_lines)
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return ""
            
    def store_interaction(self, user_id, user_message, ai_response, mood):
        """No-op. The actual saving is handled by save_chat_message via the main API route."""
        pass
        
    def get_user_memory_stats(self, user_id):
        """Get total message count for user."""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM messages WHERE user_id = %s", (user_id,))
                    count = cursor.fetchone()[0]
                    return {"total_interactions": count}
        except Exception:
            return {"total_interactions": 0}

    def delete_user_memory(self, user_id):
        """Delete all messages for a user. (Optional, as schema handles it via CASCADE)"""
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM messages WHERE user_id = %s", (user_id,))
            return True
        except Exception:
            return False


# Global instance
_memory_service = None

def get_memory_service():
    """Get memory service singleton."""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
