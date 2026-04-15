"""Memory service using ChromaDB for persistent user context."""

import chromadb
import os
from datetime import datetime
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_data")

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

class MemoryService:
    """Manage user memory with vector embeddings."""
    
    def __init__(self):
        """Initialize ChromaDB client."""
        chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_data")
        os.makedirs(chroma_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=chroma_path)
    
    def get_collection(self, user_id):
        """Get or create a collection for the user."""
        collection_name = f"user_{user_id}"
        
        try:
            collection = self.client.get_collection(name=collection_name)
        except:
            collection = self.client.create_collection(name=collection_name)
        
        return collection
    
    def store_interaction(self, user_id, user_message, ai_response, mood):
        """Store a user-AI interaction with embeddings."""
        collection = self.get_collection(user_id)
        
        # Combine message and response for context
        combined_text = f"User: {user_message}\nAssistant: {ai_response}"
        
        # Create unique ID based on timestamp
        doc_id = f"msg_{int(datetime.now().timestamp() * 1000)}"
        
        collection.add(
            ids=[doc_id],
            documents=[combined_text],
            metadatas=[{
                "user_message": user_message,
                "ai_response": ai_response,
                "mood": mood,
                "timestamp": datetime.now().isoformat()
            }]
        )
    
    def get_context(self, user_id, current_message, top_k=3):
        """Retrieve relevant past interactions as context."""
        try:
            collection = self.get_collection(user_id)
            
            # Query for similar messages
            results = collection.query(
                query_texts=[current_message],
                n_results=top_k
            )
            
            if not results or not results["documents"] or not results["documents"][0]:
                return ""
            
            # Format context from retrieved interactions
            context_lines = []
            for i, doc in enumerate(results["documents"][0]):
                mood = results["metadatas"][0][i].get("mood", "unknown")
                context_lines.append(f"[Past - Mood: {mood}]\n{doc}")
            
            return "\n\n".join(context_lines)
        
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return ""
    
    def delete_user_memory(self, user_id):
        """Delete all memory for a user (for privacy)."""
        try:
            collection_name = f"user_{user_id}"
            self.client.delete_collection(name=collection_name)
            return True
        except:
            return False
    
    def get_user_memory_stats(self, user_id):
        """Get statistics about user's memory."""
        try:
            collection = self.get_collection(user_id)
            count = collection.count()
            return {"total_interactions": count}
        except:
            return {"total_interactions": 0}


# Global instance
_memory_service = None


def get_memory_service():
    """Get memory service singleton."""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
