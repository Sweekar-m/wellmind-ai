"""Mood detection service for mental wellness tracking."""


def detect_mood(text):
    """Detect user's mood from text input using keyword analysis."""
    text_lower = text.lower()
    
    # Stress indicators
    stress_keywords = [
        "stress", "anxious", "anxiety", "worried", "overwhelmed", "pressure",
        "tense", "frustrated", "irritated", "rush", "deadline", "busy",
        "exhausted", "burned out", "panic", "nervous", "restless"
    ]
    
    # Sadness indicators
    sadness_keywords = [
        "sad", "sadness", "depressed", "depression", "lonely", "loneliness",
        "hurt", "heartbroken", "miserable", "unhappy", "down", "blue",
        "lost", "hopeless", "empty", "numb", "devastated"
    ]
    
    # Count keyword matches
    stress_count = sum(1 for word in stress_keywords if word in text_lower)
    sadness_count = sum(1 for word in sadness_keywords if word in text_lower)
    
    # Determine mood
    if stress_count > sadness_count and stress_count > 0:
        return "Stress"
    elif sadness_count > 0:
        return "Sadness"
    else:
        return "Neutral"


def get_mood_emoji(mood):
    """Get emoji for mood display."""
    mood_map = {
        "Stress": "😰",
        "Sadness": "😔",
        "Neutral": "😊"
    }
    return mood_map.get(mood, "😊")